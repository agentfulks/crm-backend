"""Trello API client with retry logic and rate limit handling."""

import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import requests
import structlog

from src.config import Settings, get_settings
from src.models import TrelloCard, TrelloLabel, TrelloList

logger = structlog.get_logger()


class TrelloAPIError(Exception):
    """Custom exception for Trello API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_body: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class TrelloClient:
    """Client for interacting with the Trello API."""
    
    def __init__(self, settings: Optional[Settings] = None):
        """Initialize with settings."""
        self.settings = settings or get_settings()
        self.base_url = self.settings.trello_api_base.rstrip("/")
        self.session = requests.Session()
        
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the Trello API with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            json_data: JSON body for POST/PUT requests
            retry_count: Current retry attempt
            
        Returns:
            Parsed JSON response
            
        Raises:
            TrelloAPIError: If request fails after all retries
        """
        # Add auth credentials to params
        request_params = {
            "key": self.settings.trello_api_key,
            "token": self.settings.trello_token,
        }
        if params:
            request_params.update(params)
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                params=request_params,
                json=json_data,
                timeout=self.settings.request_timeout,
            )
            
            # Handle rate limiting (429 Too Many Requests)
            if response.status_code == 429:
                if retry_count < self.settings.max_retries:
                    # Exponential backoff with jitter
                    delay = (self.settings.retry_delay * (2 ** retry_count)) + (retry_count * 0.5)
                    logger.warning(
                        "Rate limited by Trello API, retrying",
                        retry_count=retry_count + 1,
                        delay=delay,
                    )
                    time.sleep(delay)
                    return self._make_request(method, endpoint, params, json_data, retry_count + 1)
                else:
                    raise TrelloAPIError(
                        "Rate limit exceeded after max retries",
                        status_code=429,
                    )
            
            # Handle server errors (5xx) with retry
            if 500 <= response.status_code < 600:
                if retry_count < self.settings.max_retries:
                    delay = self.settings.retry_delay * (2 ** retry_count)
                    logger.warning(
                        "Trello server error, retrying",
                        status_code=response.status_code,
                        retry_count=retry_count + 1,
                        delay=delay,
                    )
                    time.sleep(delay)
                    return self._make_request(method, endpoint, params, json_data, retry_count + 1)
            
            # Raise for other HTTP errors
            response.raise_for_status()
            
            # Return JSON response (or empty dict for 204 No Content)
            if response.status_code == 204:
                return {}
            return response.json()
            
        except requests.exceptions.Timeout as e:
            if retry_count < self.settings.max_retries:
                delay = self.settings.retry_delay * (2 ** retry_count)
                logger.warning(
                    "Request timeout, retrying",
                    retry_count=retry_count + 1,
                    delay=delay,
                )
                time.sleep(delay)
                return self._make_request(method, endpoint, params, json_data, retry_count + 1)
            raise TrelloAPIError(f"Request timeout after {self.settings.max_retries} retries") from e
            
        except requests.exceptions.RequestException as e:
            raise TrelloAPIError(f"Request failed: {e}") from e
    
    def get_board_labels(self, board_id: Optional[str] = None) -> List[TrelloLabel]:
        """
        Get all labels for a board.
        
        Args:
            board_id: Board ID (defaults to settings)
            
        Returns:
            List of TrelloLabel objects
        """
        board_id = board_id or self.settings.trello_board_id
        response = self._make_request("GET", f"/boards/{board_id}/labels")
        return [TrelloLabel.model_validate(label) for label in response]
    
    def get_board_lists(self, board_id: Optional[str] = None) -> List[TrelloList]:
        """
        Get all lists for a board.
        
        Args:
            board_id: Board ID (defaults to settings)
            
        Returns:
            List of TrelloList objects
        """
        board_id = board_id or self.settings.trello_board_id
        response = self._make_request("GET", f"/boards/{board_id}/lists")
        return [TrelloList.model_validate(lst) for lst in response]
    
    def search_cards(
        self, 
        query: str, 
        board_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Search for cards on a board.
        
        Args:
            query: Search query string
            board_id: Board ID to search within
            limit: Maximum results to return
            
        Returns:
            List of matching card data
        """
        params = {
            "query": query,
            "modelTypes": "cards",
            "cards_limit": limit,
        }
        if board_id:
            params["idBoards"] = board_id
            
        response = self._make_request("GET", "/search", params=params)
        return response.get("cards", [])
    
    def check_card_exists_by_prefix(
        self, 
        name_prefix: str,
        board_id: Optional[str] = None,
        lookback_days: int = 30,
    ) -> bool:
        """
        Check if a card with the given name prefix already exists.
        
        Args:
            name_prefix: The prefix to search for
            board_id: Board ID to search within
            lookback_days: Not used by Trello API but kept for interface consistency
            
        Returns:
            True if a matching card exists, False otherwise
        """
        try:
            cards = self.search_cards(name_prefix, board_id, limit=10)
            for card in cards:
                if card.get("name", "").startswith(name_prefix):
                    return True
            return False
        except TrelloAPIError as e:
            logger.error("Failed to check for existing card", error=str(e))
            # Fail safe: assume no duplicate to avoid blocking creation
            return False
    
    def create_card(
        self, 
        card: TrelloCard,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a new Trello card.
        
        Args:
            card: TrelloCard model with card data
            dry_run: If True, don't actually create the card
            
        Returns:
            Created card data from API
            
        Raises:
            TrelloAPIError: If card creation fails
        """
        if dry_run:
            logger.info(
                "DRY RUN: Would create card",
                name=card.name,
                idList=card.idList,
                idLabels=card.idLabels,
            )
            # Return mock response for dry run
            return {
                "id": "dry_run_card_id",
                "name": card.name,
                "shortUrl": "https://trello.com/c/dryrun",
            }
        
        # Build request payload
        payload = {
            "name": card.name,
            "desc": card.desc,
            "idList": card.idList,
            "pos": card.pos,
        }
        
        # Add labels if provided
        if card.idLabels:
            payload["idLabels"] = ",".join(card.idLabels)
        
        # Add due date if provided
        if card.due:
            payload["due"] = card.due
        
        response = self._make_request("POST", "/cards", json_data=payload)
        
        logger.info(
            "Created Trello card",
            card_id=response.get("id"),
            name=response.get("name"),
            url=response.get("shortUrl"),
        )
        
        return response
    
    def add_checklist_to_card(
        self,
        card_id: str,
        name: str,
        items: List[str],
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """
        Add a checklist with items to a card.
        
        Args:
            card_id: ID of the card
            name: Name of the checklist
            items: List of checklist item names
            dry_run: If True, don't actually create
            
        Returns:
            Created checklist data
        """
        if dry_run:
            logger.info(
                "DRY RUN: Would add checklist",
                card_id=card_id,
                name=name,
                item_count=len(items),
            )
            return {"id": "dry_run_checklist_id", "name": name}
        
        # Create the checklist
        checklist = self._make_request(
            "POST",
            f"/cards/{card_id}/checklists",
            json_data={"name": name},
        )
        
        # Add items to the checklist
        for item in items:
            self._make_request(
                "POST",
                f"/checklists/{checklist['id']}/checkItems",
                json_data={"name": item},
            )
        
        logger.info(
            "Added checklist to card",
            card_id=card_id,
            checklist_name=name,
            item_count=len(items),
        )
        
        return checklist
