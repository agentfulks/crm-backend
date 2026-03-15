"""Trello API client with rate limiting and error handling."""

import time
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass

import requests
import yaml


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""
    pass


class TrelloAPIError(Exception):
    """Raised for Trello API errors."""
    pass


@dataclass
class TrelloCard:
    """Represents a Trello card."""
    id: str
    name: str
    desc: str
    id_list: str
    id_board: str
    labels: List[Dict[str, Any]]
    url: str
    due: Optional[str] = None
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "TrelloCard":
        """Create from API response."""
        return cls(
            id=data["id"],
            name=data["name"],
            desc=data.get("desc", ""),
            id_list=data["idList"],
            id_board=data["idBoard"],
            labels=data.get("labels", []),
            url=data["url"],
            due=data.get("due")
        )


class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, max_requests: int, window_seconds: int = 10, buffer_percent: float = 10):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
            buffer_percent: Safety buffer percentage
        """
        self.max_requests = int(max_requests * (1 - buffer_percent / 100))
        self.window_seconds = window_seconds
        self.tokens = self.max_requests
        self.last_update = time.time()
    
    def acquire(self) -> None:
        """Acquire a token, blocking if necessary."""
        now = time.time()
        elapsed = now - self.last_update
        
        # Replenish tokens based on elapsed time
        tokens_to_add = (elapsed / self.window_seconds) * self.max_requests
        self.tokens = min(self.max_requests, self.tokens + tokens_to_add)
        self.last_update = now
        
        if self.tokens < 1:
            # Need to wait
            wait_time = (1 - self.tokens) * (self.window_seconds / self.max_requests)
            time.sleep(wait_time)
            self.tokens = 0
        else:
            self.tokens -= 1


class TrelloClient:
    """Trello API client with rate limiting."""
    
    def __init__(self, gateway_url: str, api_key: str, rate_limiter: Optional[RateLimiter] = None):
        self.gateway_url = gateway_url.rstrip("/")
        self.api_key = api_key
        self.rate_limiter = rate_limiter or RateLimiter(300, 10, 10)
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    @classmethod
    def from_config(cls, config_path: str = "config.yaml") -> "TrelloClient":
        """Create client from config file."""
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        
        trello_config = config["trello"]
        rate_config = config.get("rate_limiting", {})
        
        rate_limiter = RateLimiter(
            max_requests=rate_config.get("max_requests_per_10s", 300),
            window_seconds=10,
            buffer_percent=rate_config.get("buffer_percent", 10)
        )
        
        return cls(
            gateway_url=trello_config["gateway_url"],
            api_key=trello_config["api_key"],
            rate_limiter=rate_limiter
        )
    
    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make a rate-limited request to the Trello API."""
        self.rate_limiter.acquire()
        
        url = f"{self.gateway_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            if response.status_code == 429:
                raise RateLimitExceeded("Rate limit exceeded")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            raise TrelloAPIError(f"API error: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            raise TrelloAPIError(f"Request failed: {str(e)}")
    
    def get_board(self, board_id: str) -> Dict[str, Any]:
        """Get board details."""
        return self._request("GET", f"/1/boards/{board_id}")
    
    def get_lists(self, board_id: str) -> List[Dict[str, Any]]:
        """Get all lists on a board."""
        return self._request("GET", f"/1/boards/{board_id}/lists")
    
    def get_cards_in_list(self, list_id: str) -> List[TrelloCard]:
        """Get all cards in a list."""
        data = self._request("GET", f"/1/lists/{list_id}/cards")
        return [TrelloCard.from_api(card) for card in data]
    
    def move_card(self, card_id: str, target_list_id: str) -> TrelloCard:
        """Move a card to a different list."""
        data = self._request(
            "PUT",
            f"/1/cards/{card_id}",
            params={"idList": target_list_id}
        )
        return TrelloCard.from_api(data)
    
    def update_card(self, card_id: str, **updates) -> TrelloCard:
        """Update card fields."""
        data = self._request(
            "PUT",
            f"/1/cards/{card_id}",
            params=updates
        )
        return TrelloCard.from_api(data)
    
    def add_label_to_card(self, card_id: str, label_id: str) -> None:
        """Add a label to a card."""
        self._request(
            "POST",
            f"/1/cards/{card_id}/idLabels",
            params={"value": label_id}
        )
    
    def get_list_by_name(self, board_id: str, name: str) -> Optional[Dict[str, Any]]:
        """Find a list by name on a board."""
        lists = self.get_lists(board_id)
        for lst in lists:
            if lst.get("name", "").lower() == name.lower():
                return lst
        return None
    
    def get_or_create_list(self, board_id: str, name: str) -> Dict[str, Any]:
        """Get or create a list by name."""
        existing = self.get_list_by_name(board_id, name)
        if existing:
            return existing
        
        # Create new list
        data = self._request(
            "POST",
            "/1/lists",
            params={
                "name": name,
                "idBoard": board_id
            }
        )
        return data
