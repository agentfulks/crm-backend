#!/usr/bin/env python3
"""
Trello Card Workflow Automation
Moves Day 1 packet cards from 'Daily Queue' to 'Awaiting Approval'

Usage:
    export TRELLO_API_KEY=your_key
    export TRELLO_TOKEN=your_token
    export TRELLO_BOARD_ID=your_board_id  # Optional - used to auto-discover list IDs
    python3 trello_automation.py

Required Environment Variables:
    TRELLO_API_KEY - Trello API key from https://trello.com/app-key
    TRELLO_TOKEN   - Trello API token (obtained after accepting terms on app-key page)

Optional Environment Variables:
    TRELLO_BOARD_ID        - Board ID to auto-discover list IDs
    DAILY_QUEUE_LIST_ID    - Source list ID (defaults to auto-discovery)
    AWAITING_APPROVAL_ID   - Target list ID (defaults to auto-discovery)
"""

import os
import sys
import json
import urllib.request
import urllib.error
from typing import Optional, List, Dict, Any


class TrelloClient:
    """Simple Trello API client for card operations."""
    
    BASE_URL = "https://api.trello.com/1"
    
    def __init__(self, api_key: str, token: str):
        self.api_key = api_key
        self.token = token
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Any:
        """Make authenticated request to Trello API."""
        url = f"{self.BASE_URL}{endpoint}"
        
        # Add auth params
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}key={self.api_key}&token={self.token}"
        
        headers = {"Content-Type": "application/json"}
        
        if data and method in ("PUT", "POST"):
            # For PUT/POST with form data (Trello's preferred format)
            url_parts = url.split("?")
            base_url = url_parts[0]
            auth_params = url_parts[1] if len(url_parts) > 1 else ""
            
            # Build form data
            form_data = urllib.parse.urlencode(data)
            full_url = f"{base_url}?{auth_params}"
            
            req = urllib.request.Request(
                full_url,
                data=form_data.encode("utf-8"),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                method=method
            )
        else:
            req = urllib.request.Request(url, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            raise Exception(f"Trello API error: {e.code} - {error_body}")
    
    def get_board_lists(self, board_id: str) -> List[Dict]:
        """Get all lists on a board."""
        return self._make_request(f"/boards/{board_id}/lists")
    
    def get_card(self, card_id: str) -> Dict:
        """Get card details."""
        return self._make_request(f"/cards/{card_id}")
    
    def move_card_to_list(self, card_id: str, list_id: str) -> Dict:
        """Move a card to a different list."""
        return self._make_request(
            f"/cards/{card_id}",
            method="PUT",
            data={"idList": list_id}
        )
    
    def get_card_checklists(self, card_id: str) -> List[Dict]:
        """Get all checklists on a card."""
        return self._make_request(f"/cards/{card_id}/checklists")
    
    def update_checklist_item(self, card_id: str, checklist_item_id: str, state: str = "complete") -> Dict:
        """Update a checklist item state."""
        return self._make_request(
            f"/cards/{card_id}/checklist/{checklist_item_id}/item/{checklist_item_id}",
            method="PUT",
            data={"state": state}
        )


class TrelloAutomation:
    """Automates Day 1 packet card workflow."""
    
    # Card IDs to process
    PACKET_CARDS = [
        {"id": "699d62440c53022f56dc42b1", "name": "BITKRAFT Ventures"},
        {"id": "699d62471bee2f60a50aab9a", "name": "Variant"},
        {"id": "699d6249d5248492eefc000e", "name": "Collab+Currency"},
        {"id": "699d624cdd614a5e0a62b5e3", "name": "Konvoy Ventures"},
        {"id": "699d624efca4d3709cef25d5", "name": "Mechanism Capital"},
    ]
    
    def __init__(self, api_key: str, token: str):
        self.client = TrelloClient(api_key, token)
        self.awaiting_approval_list_id: Optional[str] = None
    
    def discover_list_ids(self, board_id: str) -> Dict[str, str]:
        """Auto-discover list IDs by name."""
        lists = self.client.get_board_lists(board_id)
        list_map = {}
        
        for lst in lists:
            name = lst.get("name", "").strip()
            list_id = lst.get("id")
            list_map[name] = list_id
            print(f"  Found list: '{name}' -> {list_id}")
        
        return list_map
    
    def find_awaiting_approval_list(self, list_map: Dict[str, str]) -> Optional[str]:
        """Find the 'Awaiting Approval' list ID."""
        # Try exact match first
        if "Awaiting Approval" in list_map:
            return list_map["Awaiting Approval"]
        
        # Try case-insensitive match
        for name, list_id in list_map.items():
            if "awaiting" in name.lower() and "approval" in name.lower():
                return list_id
        
        return None
    
    def move_packet_cards(self, target_list_id: str) -> List[Dict]:
        """Move all packet cards to target list."""
        results = []
        
        print(f"\nMoving cards to list ID: {target_list_id}")
        print("=" * 60)
        
        for card in self.PACKET_CARDS:
            card_id = card["id"]
            card_name = card["name"]
            
            try:
                # Get current card info
                current = self.client.get_card(card_id)
                current_list = current.get("idList", "unknown")
                
                print(f"\nProcessing: Packet: {card_name}")
                print(f"  Card ID: {card_id}")
                print(f"  Current list: {current_list}")
                
                # Move the card
                updated = self.client.move_card_to_list(card_id, target_list_id)
                new_list = updated.get("idList")
                
                print(f"  ✓ Moved to: {new_list}")
                
                # Get and display checklists
                checklists = self.client.get_card_checklists(card_id)
                if checklists:
                    print(f"  Checklists found: {len(checklists)}")
                    for checklist in checklists:
                        checklist_name = checklist.get("name", "Unnamed")
                        items = checklist.get("checkItems", [])
                        print(f"    - {checklist_name}: {len(items)} items")
                
                results.append({
                    "card_id": card_id,
                    "name": card_name,
                    "success": True,
                    "previous_list": current_list,
                    "new_list": new_list
                })
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                results.append({
                    "card_id": card_id,
                    "name": card_name,
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    def run(self) -> None:
        """Execute the automation workflow."""
        print("=" * 60)
        print("Trello Day 1 Packet Card Automation")
        print("=" * 60)
        
        # Check for target list ID
        target_list_id = os.environ.get("AWAITING_APPROVAL_ID")
        
        if not target_list_id:
            # Try to discover from board
            board_id = os.environ.get("TRELLO_BOARD_ID")
            if board_id:
                print(f"\nDiscovering lists from board: {board_id}")
                list_map = self.discover_list_ids(board_id)
                target_list_id = self.find_awaiting_approval_list(list_map)
        
        if not target_list_id:
            print("\nERROR: Could not determine 'Awaiting Approval' list ID")
            print("\nOptions:")
            print("1. Set AWAITING_APPROVAL_ID environment variable")
            print("2. Set TRELLO_BOARD_ID to auto-discover")
            print("\nTo find list IDs manually:")
            print("  curl 'https://api.trello.com/1/boards/BOARD_ID/lists?key=KEY&token=TOKEN'")
            sys.exit(1)
        
        # Move the cards
        results = self.move_packet_cards(target_list_id)
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        
        print(f"\nTotal cards processed: {len(results)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(failed)}")
        
        if failed:
            print("\nFailed cards:")
            for result in failed:
                print(f"  - {result['name']}: {result.get('error', 'Unknown error')}")
        
        print("\n" + "=" * 60)


def main():
    """Main entry point."""
    # Load credentials
    api_key = os.environ.get("TRELLO_API_KEY")
    token = os.environ.get("TRELLO_TOKEN")
    
    if not api_key or not token:
        print("ERROR: Trello API credentials not found!")
        print("\nRequired environment variables:")
        print("  TRELLO_API_KEY - Your Trello API key")
        print("  TRELLO_TOKEN   - Your Trello API token")
        print("\nTo obtain credentials:")
        print("  1. Visit https://trello.com/app-key")
        print("  2. Copy the API key")
        print("  3. Click the link to generate a token")
        print("\nExample usage:")
        print("  export TRELLO_API_KEY=your_key")
        print("  export TRELLO_TOKEN=your_token")
        print("  export TRELLO_BOARD_ID=your_board_id  # Optional")
        print("  python3 trello_automation.py")
        sys.exit(1)
    
    # Run automation
    automation = TrelloAutomation(api_key, token)
    automation.run()


if __name__ == "__main__":
    main()
