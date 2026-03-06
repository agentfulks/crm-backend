#!/usr/bin/env python3
"""
Trello Board State Fetcher
==========================
Fetches board data from Trello API with timeout handling,
caching, and graceful error recovery.

Usage:
    python fetch_board.py              # Fetch fresh data (or use cache if API fails)
    python fetch_board.py --force      # Skip cache, always fetch from API
    python fetch_board.py --timeout 5  # Use 5 second timeout (default: 10)
    python fetch_board.py --json       # Output as JSON (default: human-readable)
"""

import os
import json
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
from functools import wraps

import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
CACHE_FILE = Path("trello_cache.json")
CACHE_TTL_MINUTES = 30
DEFAULT_TIMEOUT = 10
TRELLO_API_BASE = "https://api.trello.com/1"


@dataclass
class Card:
    """Represents a Trello card."""
    id: str
    name: str
    desc: str
    id_list: str
    list_name: str
    url: str
    due: Optional[str] = None
    labels: List[str] = None
    last_activity: Optional[str] = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = []


@dataclass
class ListSummary:
    """Summary of cards in a list."""
    list_id: str
    list_name: str
    card_count: int
    cards: List[Card]


@dataclass
class BoardState:
    """Complete board state with all lists and cards."""
    board_id: str
    board_name: str
    fetched_at: str
    cache_hit: bool
    lists: List[ListSummary]
    total_cards: int
    error: Optional[str] = None


class TrelloAPIError(Exception):
    """Custom exception for Trello API errors."""
    pass


class TrelloTimeoutError(Exception):
    """Custom exception for timeout errors."""
    pass


def retry_on_error(max_retries: int = 2, delay: float = 1.0):
    """Decorator to retry API calls on failure."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (requests.Timeout, requests.ConnectionError) as e:
                    last_error = e
                    if attempt < max_retries:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                        import time
                        time.sleep(delay * (attempt + 1))  # Exponential backoff
                    else:
                        raise TrelloTimeoutError(f"Failed after {max_retries + 1} attempts: {e}")
                except requests.RequestException as e:
                    last_error = e
                    if attempt < max_retries:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                        import time
                        time.sleep(delay)
                    else:
                        raise TrelloAPIError(f"API request failed: {e}")
            raise last_error
        return wrapper
    return decorator


class TrelloClient:
    """Client for Trello API with timeout and error handling."""
    
    def __init__(self, api_key: str, token: str, timeout: int = DEFAULT_TIMEOUT):
        self.api_key = api_key
        self.token = token
        self.timeout = timeout
        self.session = requests.Session()
        
    def _auth_params(self) -> Dict[str, str]:
        """Return authentication parameters."""
        return {"key": self.api_key, "token": self.token}
    
    @retry_on_error(max_retries=2, delay=1.0)
    def get_board(self, board_id: str) -> Dict[str, Any]:
        """Fetch board details."""
        url = f"{TRELLO_API_BASE}/boards/{board_id}"
        params = {**self._auth_params(), "fields": "name,id"}
        
        logger.info(f"Fetching board: {board_id}")
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    @retry_on_error(max_retries=2, delay=1.0)
    def get_lists(self, board_id: str) -> List[Dict[str, Any]]:
        """Fetch all lists on a board."""
        url = f"{TRELLO_API_BASE}/boards/{board_id}/lists"
        params = {**self._auth_params(), "fields": "name,id"}
        
        logger.info(f"Fetching lists for board: {board_id}")
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    @retry_on_error(max_retries=2, delay=1.0)
    def get_cards(self, list_id: str) -> List[Dict[str, Any]]:
        """Fetch all cards in a list."""
        url = f"{TRELLO_API_BASE}/lists/{list_id}/cards"
        params = {
            **self._auth_params(),
            "fields": "name,desc,idList,url,due,labels,dateLastActivity"
        }
        
        logger.debug(f"Fetching cards for list: {list_id}")
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()


class CacheManager:
    """Manages local caching of Trello data."""
    
    def __init__(self, cache_file: Path = CACHE_FILE, ttl_minutes: int = CACHE_TTL_MINUTES):
        self.cache_file = cache_file
        self.ttl = timedelta(minutes=ttl_minutes)
    
    def is_valid(self) -> bool:
        """Check if cache exists and is not expired."""
        if not self.cache_file.exists():
            return False
        
        try:
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
            
            cached_time = datetime.fromisoformat(data.get('fetched_at', '2000-01-01'))
            return datetime.now() - cached_time < self.ttl
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning(f"Cache file corrupt: {e}")
            return False
    
    def load(self) -> Optional[Dict[str, Any]]:
        """Load data from cache."""
        if not self.is_valid():
            return None
        
        try:
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
            data['cache_hit'] = True
            logger.info("Cache hit - using cached data")
            return data
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
            return None
    
    def save(self, data: Dict[str, Any]) -> None:
        """Save data to cache."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Data cached to {self.cache_file}")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def clear(self) -> None:
        """Clear the cache file."""
        if self.cache_file.exists():
            self.cache_file.unlink()
            logger.info("Cache cleared")


def parse_card(card_data: Dict[str, Any], list_name: str) -> Card:
    """Parse raw card data into Card object."""
    labels = [label.get('name', label.get('color', 'unknown')) for label in card_data.get('labels', [])]
    
    return Card(
        id=card_data.get('id', ''),
        name=card_data.get('name', ''),
        desc=card_data.get('desc', ''),
        id_list=card_data.get('idList', ''),
        list_name=list_name,
        url=card_data.get('url', ''),
        due=card_data.get('due'),
        labels=labels,
        last_activity=card_data.get('dateLastActivity')
    )


def fetch_board_state(
    client: TrelloClient,
    board_id: str,
    cache_manager: CacheManager,
    force_refresh: bool = False
) -> BoardState:
    """
    Fetch complete board state with caching and error handling.
    
    Returns cached data if API fails (unless force_refresh=True).
    """
    # Try cache first if not forcing refresh
    if not force_refresh:
        cached = cache_manager.load()
        if cached:
            # Reconstruct BoardState from cache
            lists = []
            total_cards = 0
            for lst in cached.get('lists', []):
                cards = [Card(**c) for c in lst.get('cards', [])]
                lists.append(ListSummary(
                    list_id=lst['list_id'],
                    list_name=lst['list_name'],
                    card_count=len(cards),
                    cards=cards
                ))
                total_cards += len(cards)
            
            return BoardState(
                board_id=cached['board_id'],
                board_name=cached['board_name'],
                fetched_at=cached['fetched_at'],
                cache_hit=True,
                lists=lists,
                total_cards=total_cards
            )
    
    # Fetch from API
    try:
        # Get board info
        board = client.get_board(board_id)
        board_name = board.get('name', 'Unknown Board')
        
        # Get all lists
        lists_data = client.get_lists(board_id)
        
        # Fetch cards for each list
        list_summaries = []
        total_cards = 0
        
        for lst in lists_data:
            list_id = lst.get('id')
            list_name = lst.get('name', 'Unknown')
            
            # Get cards for this list
            cards_data = client.get_cards(list_id)
            cards = [parse_card(c, list_name) for c in cards_data]
            
            list_summaries.append(ListSummary(
                list_id=list_id,
                list_name=list_name,
                card_count=len(cards),
                cards=cards
            ))
            total_cards += len(cards)
            
            logger.info(f"List '{list_name}': {len(cards)} cards")
        
        # Create board state
        state = BoardState(
            board_id=board_id,
            board_name=board_name,
            fetched_at=datetime.now().isoformat(),
            cache_hit=False,
            lists=list_summaries,
            total_cards=total_cards
        )
        
        # Save to cache
        cache_manager.save(board_state_to_dict(state))
        
        return state
        
    except (TrelloAPIError, TrelloTimeoutError) as e:
        logger.error(f"API error: {e}")
        
        # Try to return cached data even if expired
        cached = cache_manager.load()
        if cached:
            logger.warning("Using expired cache due to API failure")
            lists = []
            total_cards = 0
            for lst in cached.get('lists', []):
                cards = [Card(**c) for c in lst.get('cards', [])]
                lists.append(ListSummary(
                    list_id=lst['list_id'],
                    list_name=lst['list_name'],
                    card_count=len(cards),
                    cards=cards
                ))
                total_cards += len(cards)
            
            return BoardState(
                board_id=cached['board_id'],
                board_name=cached['board_name'],
                fetched_at=cached['fetched_at'],
                cache_hit=True,
                lists=lists,
                total_cards=total_cards,
                error=f"API failed, using cached data: {e}"
            )
        
        # No cache available
        return BoardState(
            board_id=board_id,
            board_name="Error",
            fetched_at=datetime.now().isoformat(),
            cache_hit=False,
            lists=[],
            total_cards=0,
            error=str(e)
        )


def board_state_to_dict(state: BoardState) -> Dict[str, Any]:
    """Convert BoardState to dictionary for JSON serialization."""
    return {
        "board_id": state.board_id,
        "board_name": state.board_name,
        "fetched_at": state.fetched_at,
        "cache_hit": state.cache_hit,
        "total_cards": state.total_cards,
        "error": state.error,
        "lists": [
            {
                "list_id": lst.list_id,
                "list_name": lst.list_name,
                "card_count": lst.card_count,
                "cards": [
                    {
                        "id": c.id,
                        "name": c.name,
                        "desc": c.desc,
                        "id_list": c.id_list,
                        "list_name": c.list_name,
                        "url": c.url,
                        "due": c.due,
                        "labels": c.labels,
                        "last_activity": c.last_activity
                    }
                    for c in lst.cards
                ]
            }
            for lst in state.lists
        ]
    }


def print_human_readable(state: BoardState) -> None:
    """Print board state in human-readable format."""
    print("\n" + "=" * 60)
    print(f"📋 Board: {state.board_name}")
    print(f"🆔 Board ID: {state.board_id}")
    print(f"⏰ Fetched: {state.fetched_at}")
    print(f"💾 Cache: {'HIT' if state.cache_hit else 'MISS'}")
    print(f"🎯 Total Cards: {state.total_cards}")
    
    if state.error:
        print(f"\n⚠️  Warning: {state.error}")
    
    print("\n" + "-" * 60)
    print("📊 List Summary:")
    print("-" * 60)
    
    for lst in state.lists:
        print(f"\n📁 {lst.list_name}")
        print(f"   Cards: {lst.card_count}")
        
        for card in lst.cards[:5]:  # Show first 5 cards
            labels_str = f" [{', '.join(card.labels)}]" if card.labels else ""
            due_str = f" (Due: {card.due[:10]})" if card.due else ""
            print(f"   • {card.name}{labels_str}{due_str}")
        
        if len(lst.cards) > 5:
            print(f"   ... and {len(lst.cards) - 5} more")
    
    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Fetch Trello board state")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force API fetch, skip cache"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"API timeout in seconds (default: {DEFAULT_TIMEOUT})"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear the cache file"
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()
    
    # Get credentials
    api_key = os.getenv("TRELLO_API_KEY")
    token = os.getenv("TRELLO_TOKEN")
    board_id = os.getenv("TRELLO_BOARD_ID", "699d2728fd2ae8c35d1f7a44")
    
    # Validate credentials
    if not api_key or not token:
        print("❌ Error: TRELLO_API_KEY and TRELLO_TOKEN must be set in .env")
        print("\nSee trello_api_setup.md for instructions on getting credentials.")
        return 1
    
    # Clear cache if requested
    cache_manager = CacheManager()
    if args.clear_cache:
        cache_manager.clear()
        return 0
    
    # Create client and fetch data
    client = TrelloClient(api_key, token, timeout=args.timeout)
    state = fetch_board_state(client, board_id, cache_manager, force_refresh=args.force)
    
    # Output results
    if args.json:
        print(json.dumps(board_state_to_dict(state), indent=2))
    else:
        print_human_readable(state)
    
    # Return error code if there was an error and no cache
    if state.error and not state.cache_hit:
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
