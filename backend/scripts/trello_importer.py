"""
Trello Card Importer
Automates importing outreach cards from markdown files to Trello board.
"""
import os
import re
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TrelloCard:
    """Represents a card to be imported to Trello."""
    name: str
    description: str
    labels: List[str]
    due_date: Optional[str] = None
    source_file: str = ""
    
    def to_api_payload(self, list_id: str) -> dict:
        """Convert to Trello API payload."""
        return {
            "name": self.name[:500],  # Trello limit
            "desc": self.description[:10000],  # Trello limit
            "idList": list_id,
            "due": self.due_date,
        }


class TrelloImporter:
    """Imports outreach cards to Trello board."""
    
    def __init__(self):
        self.api_key = os.getenv("TRELLO_API_KEY")
        self.api_token = os.getenv("TRELLO_API_TOKEN")
        self.board_id = os.getenv("TRELLO_BOARD_ID")
        self.list_name = os.getenv("TRELLO_TARGET_LIST", "To Do")
        
        if not all([self.api_key, self.api_token, self.board_id]):
            raise ValueError(
                "Missing Trello credentials. Set TRELLO_API_KEY, "
                "TRELLO_API_TOKEN, and TRELLO_BOARD_ID in .env"
            )
        
        self.base_url = "https://api.trello.com/1"
        self.auth_params = {
            "key": self.api_key,
            "token": self.api_token
        }
        self.list_id = self._get_list_id()
        self.existing_cards = self._get_existing_cards()
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make authenticated request to Trello API."""
        url = f"{self.base_url}{endpoint}"
        params = {**self.auth_params, **kwargs.get("params", {})}
        
        try:
            response = requests.request(
                method, url, params=params, json=kwargs.get("json"), timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def _get_list_id(self) -> str:
        """Get list ID by name from board."""
        lists = self._make_request("GET", f"/boards/{self.board_id}/lists")
        for lst in lists:
            if lst["name"].lower() == self.list_name.lower():
                logger.info(f"Found list '{self.list_name}' with ID {lst['id']}")
                return lst["id"]
        raise ValueError(f"List '{self.list_name}' not found on board")
    
    def _get_existing_cards(self) -> set:
        """Get set of existing card names for deduplication."""
        cards = self._make_request(
            "GET", f"/boards/{self.board_id}/cards", params={"fields": "name"}
        )
        names = {card["name"].strip().lower() for card in cards}
        logger.info(f"Found {len(names)} existing cards on board")
        return names
    
    def parse_markdown_file(self, filepath: Path) -> List[TrelloCard]:
        """Parse markdown file and extract card data."""
        cards = []
        content = filepath.read_text(encoding="utf-8")
        
        # Parse VC cards (### Fund Name format)
        vc_pattern = r"###\s+(.+?)\n\n\*\*Partner:\*\*\s*(.+?)\n\*\*Fit Score:\*\*\s*(\d+)\n\*\*Check Size:\*\*\s*(.+?)\n\*\*Why:\*\*\s*(.+?)(?=\n\n###|\Z)"
        
        for match in re.finditer(vc_pattern, content, re.DOTALL):
            fund, partner, fit, check_size, why = match.groups()
            card = TrelloCard(
                name=f"VC Outreach: {fund.strip()}",
                description=(
                    f"**Partner:** {partner.strip()}\n\n"
                    f"**Fit Score:** {fit.strip()}/100\n\n"
                    f"**Check Size:** {check_size.strip()}\n\n"
                    f"**Why:** {why.strip()}\n\n"
                    f"**Source:** {filepath.name}"
                ),
                labels=["vc-outreach", f"fit-{fit.strip()}"],
                source_file=str(filepath)
            )
            cards.append(card)
        
        # Parse BDR cards (### Studio Name format)
        bdr_pattern = r"###\s+(.+?)\n\n\*\*CEO/Contact:\*\*\s*(.+?)\n\*\*Downloads:\*\*\s*(.+?)\n\*\*Why:\*\*\s*(.+?)(?=\n\n###|\Z)"
        
        for match in re.finditer(bdr_pattern, content, re.DOTALL):
            studio, contact, downloads, why = match.groups()
            card = TrelloCard(
                name=f"BDR Outreach: {studio.strip()}",
                description=(
                    f"**Contact:** {contact.strip()}\n\n"
                    f"**Downloads:** {downloads.strip()}\n\n"
                    f"**Why:** {why.strip()}\n\n"
                    f"**Source:** {filepath.name}"
                ),
                labels=["bdr-outreach", "game-studio"],
                source_file=str(filepath)
            )
            cards.append(card)
        
        logger.info(f"Parsed {len(cards)} cards from {filepath.name}")
        return cards
    
    def card_exists(self, card: TrelloCard) -> bool:
        """Check if card already exists on board."""
        return card.name.strip().lower() in self.existing_cards
    
    def create_card(self, card: TrelloCard) -> Optional[dict]:
        """Create a single card on Trello."""
        if self.card_exists(card):
            logger.info(f"Skipping duplicate: {card.name[:50]}...")
            return None
        
        try:
            payload = card.to_api_payload(self.list_id)
            result = self._make_request("POST", "/cards", json=payload)
            
            # Add labels if card created successfully
            if result and card.labels:
                self._add_labels(result["id"], card.labels)
            
            logger.info(f"Created card: {card.name[:50]}...")
            self.existing_cards.add(card.name.strip().lower())
            return result
            
        except Exception as e:
            logger.error(f"Failed to create card '{card.name[:50]}': {e}")
            return None
    
    def _add_labels(self, card_id: str, labels: List[str]):
        """Add labels to a card."""
        for label in labels[:3]:  # Max 3 labels
            try:
                self._make_request(
                    "POST", "/labels",
                    json={
                        "name": label[:20],
                        "color": "green" if "vc" in label else "blue",
                        "idBoard": self.board_id
                    }
                )
            except Exception as e:
                logger.warning(f"Could not add label '{label}': {e}")
    
    def import_batch(self, filepath: Path, dry_run: bool = False) -> dict:
        """Import a batch of cards from markdown file."""
        logger.info(f"Processing batch: {filepath.name}")
        
        cards = self.parse_markdown_file(filepath)
        results = {
            "total": len(cards),
            "created": 0,
            "skipped": 0,
            "failed": 0,
            "dry_run": dry_run
        }
        
        for card in cards:
            if self.card_exists(card):
                results["skipped"] += 1
                continue
            
            if dry_run:
                logger.info(f"[DRY RUN] Would create: {card.name[:50]}...")
                results["created"] += 1
            else:
                if self.create_card(card):
                    results["created"] += 1
                    time.sleep(6)  # Rate limit: 10 cards/minute
                else:
                    results["failed"] += 1
        
        logger.info(
            f"Batch complete: {results['created']} created, "
            f"{results['skipped']} skipped, {results['failed']} failed"
        )
        return results
    
    def import_all(self, import_dir: Path, dry_run: bool = False) -> dict:
        """Import all markdown files from directory."""
        markdown_files = sorted(import_dir.glob("TRELLO_IMPORT_*.md"))
        
        if not markdown_files:
            logger.warning(f"No import files found in {import_dir}")
            return {"batches": 0, "total_cards": 0}
        
        logger.info(f"Found {len(markdown_files)} batch files to import")
        
        total_results = {
            "batches": len(markdown_files),
            "total_cards": 0,
            "created": 0,
            "skipped": 0,
            "failed": 0,
            "dry_run": dry_run
        }
        
        for filepath in markdown_files:
            batch_results = self.import_batch(filepath, dry_run)
            for key in ["total_cards", "created", "skipped", "failed"]:
                if key in batch_results:
                    total_results[key] = total_results.get(key, 0) + batch_results[key]
            total_results["total_cards"] += batch_results["total"]
            
            if not dry_run:
                time.sleep(2)  # Brief pause between batches
        
        return total_results


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Import outreach cards to Trello")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview imports without creating cards"
    )
    parser.add_argument(
        "--file", type=str,
        help="Import specific file (default: all files in trello-import-ready/)"
    )
    parser.add_argument(
        "--list", type=str, default="To Do",
        help="Target Trello list name (default: To Do)"
    )
    
    args = parser.parse_args()
    
    # Override list name if provided
    if args.list:
        os.environ["TRELLO_TARGET_LIST"] = args.list
    
    try:
        importer = TrelloImporter()
        
        if args.file:
            filepath = Path(args.file)
            if not filepath.exists():
                filepath = Path("output/trello-import-ready") / args.file
            results = importer.import_batch(filepath, dry_run=args.dry_run)
        else:
            import_dir = Path("output/trello-import-ready")
            results = importer.import_all(import_dir, dry_run=args.dry_run)
        
        logger.info("=" * 50)
        logger.info("IMPORT SUMMARY")
        logger.info("=" * 50)
        for key, value in results.items():
            logger.info(f"  {key}: {value}")
        
        return 0 if results.get("failed", 0) == 0 else 1
        
    except Exception as e:
        logger.error(f"Import failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
