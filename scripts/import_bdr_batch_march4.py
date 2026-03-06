#!/usr/bin/env python3
"""
BDR Studio Batch Import Script (YAML Version)
Imports 10 game studios from deliverable markdown into Trello cards.
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


# Constants
DELIVERABLE_PATH = Path("/data/workspace/agents/bdr-strategist/output/BDR_RESEARCH_BATCH_MARCH04_1917.md")
BOARD_ID = "699f37680e0b1bc16721ae44"
TARGET_LIST_NAME = "Ready for Review"
MATON_API_BASE = "https://api.maton.ai/v1"

# Idempotency: Track processed studios to prevent duplicates across runs
IMPORT_STATE_FILE = Path("/data/workspace/.import_state_bdr.json")

# Tier to Label mapping
TIER_LABELS = {
    "Tier-1": "P0",
    "Tier-2": "P1", 
    "Tier-3": "P2"
}


@dataclass
class Contact:
    """Represents a contact person at a studio."""
    full_name: str
    title: str
    email: str
    linkedin: str
    seniority: str = ""
    
    def to_markdown(self) -> str:
        """Format contact as markdown for Trello card."""
        lines = [f"**{self.full_name}** — {self.title}"]
        if self.email:
            lines.append(f"📧 {self.email}")
        if self.linkedin:
            lines.append(f"🔗 [LinkedIn]({self.linkedin})")
        return "\n".join(lines)


@dataclass
class Studio:
    """Represents a game studio with all relevant data."""
    name: str
    website: str
    headquarters: str
    employee_count: str
    total_downloads: str
    key_titles: str
    linkedin_company: str
    tier: str
    primary_contact: Contact
    secondary_contact: Optional[Contact] = None
    targeting_angle: str = ""
    recent_news: str = ""
    why_now: str = ""
    hypothesis: str = ""
    personalization_hook: str = ""
    draft_subject: str = ""
    draft_message: str = ""
    
    @property
    def priority_label(self) -> str:
        """Get the Trello label based on tier."""
        return TIER_LABELS.get(self.tier, "P2")
    
    def to_card_description(self) -> str:
        """Generate the Trello card description."""
        lines = [
            f"## Studio Profile",
            f"",
            f"**Website:** [{self.website}]({self.website})",
            f"**HQ:** {self.headquarters}",
            f"**Employees:** {self.employee_count}",
            f"**Downloads:** {self.total_downloads}",
            f"**Key Titles:** {self.key_titles}",
            f"**LinkedIn:** [Company Page]({self.linkedin_company})",
            f"",
            f"---",
            f"",
            f"## Primary Contact",
            f"",
            self.primary_contact.to_markdown(),
            f"",
            f"---",
            f"",
            f"## Outreach Context",
            f"",
            f"**Targeting Angle:** {self.targeting_angle}",
            f"**Recent News:** {self.recent_news}",
            f"**Why Now:** {self.why_now}",
            f"**Hypothesis:** {self.hypothesis}",
            f"**Hook:** {self.personalization_hook}",
            f"",
            f"---",
            f"",
            f"*Imported: {datetime.now().strftime('%Y-%m-%d')} | Batch: March 4, 2026*",
        ]
        
        return "\n".join(lines)


class ImportState:
    """Tracks import state for idempotency across runs."""
    
    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.processed_studios: set = set()
        self._load()
    
    def _load(self):
        """Load state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.processed_studios = set(data.get('processed_studios', []))
                print(f"Loaded import state: {len(self.processed_studios)} previously processed studios")
            except Exception as e:
                print(f"Warning: Could not load state file: {e}")
                self.processed_studios = set()
    
    def save(self):
        """Save state to file."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump({
                    'processed_studios': list(self.processed_studios),
                    'last_run': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save state file: {e}")
    
    def is_processed(self, studio_name: str) -> bool:
        """Check if a studio has already been processed."""
        return studio_name.lower() in {s.lower() for s in self.processed_studios}
    
    def mark_processed(self, studio_name: str):
        """Mark a studio as processed."""
        self.processed_studios.add(studio_name)


class TrelloImporter:
    """Handles Trello API interactions via Maton."""
    
    def __init__(self, api_key: str, state: Optional[ImportState] = None):
        self.api_key = api_key
        self.state = state
        self._list_id: Optional[str] = None
        self._existing_cards: Optional[List[Dict]] = None
        self._board_labels: Optional[Dict[str, str]] = None
    
    def _api_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make an API request to Maton."""
        url = f"{MATON_API_BASE}/{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            if data:
                payload = json.dumps(data).encode('utf-8')
                req = Request(url, data=payload, headers=headers, method=method)
            else:
                req = Request(url, headers=headers, method=method)
            
            with urlopen(req, timeout=30) as response:
                response_data = response.read().decode('utf-8')
                return json.loads(response_data) if response_data else {}
                
        except HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"API Error ({e.code}): {error_body}")
            raise
        except URLError as e:
            print(f"URL Error: {e.reason}")
            raise
        except Exception as e:
            print(f"Request Error: {e}")
            raise
    
    def get_list_id(self) -> str:
        """Get the Trello list ID for 'Ready for Review'."""
        if self._list_id:
            return self._list_id
        
        print(f"Fetching lists for board {BOARD_ID}...")
        result = self._api_request("GET", f"trello/boards/{BOARD_ID}/lists")
        
        lists = result.get("data", [])
        for lst in lists:
            if lst.get("name") == TARGET_LIST_NAME:
                self._list_id = lst.get("id")
                print(f"Found list '{TARGET_LIST_NAME}' with ID: {self._list_id}")
                return self._list_id
        
        raise ValueError(f"List '{TARGET_LIST_NAME}' not found on board {BOARD_ID}")
    
    def get_existing_cards(self) -> List[Dict]:
        """Fetch existing cards to check for duplicates."""
        if self._existing_cards is not None:
            return self._existing_cards
        
        list_id = self.get_list_id()
        print(f"Fetching existing cards from list...")
        result = self._api_request("GET", f"trello/lists/{list_id}/cards")
        
        self._existing_cards = result.get("data", [])
        print(f"Found {len(self._existing_cards)} existing cards")
        return self._existing_cards
    
    def get_board_labels(self) -> Dict[str, str]:
        """Get label IDs for P0, P1, P2."""
        if self._board_labels is not None:
            return self._board_labels
        
        print(f"Fetching board labels...")
        result = self._api_request("GET", f"trello/boards/{BOARD_ID}/labels")
        
        labels = result.get("data", [])
        self._board_labels = {}
        
        for label in labels:
            name = label.get("name", "")
            if name in ["P0", "P1", "P2"]:
                self._board_labels[name] = label.get("id")
        
        print(f"Found labels: {list(self._board_labels.keys())}")
        return self._board_labels
    
    def card_exists(self, studio_name: str) -> bool:
        """Check if a card for this studio already exists (API + local state)."""
        # Check local state first (idempotency across runs)
        if self.state and self.state.is_processed(studio_name):
            return True
        
        # Check Trello API for existing cards
        existing = self.get_existing_cards()
        studio_name_lower = studio_name.lower()
        
        for card in existing:
            card_name = card.get("name", "").lower()
            # Match if studio name appears in card name
            if studio_name_lower in card_name or card_name in studio_name_lower:
                # Update local state for future runs
                if self.state:
                    self.state.mark_processed(studio_name)
                return True
        
        return False
    
    def create_card(self, studio: Studio, dry_run: bool = False) -> Optional[Dict]:
        """Create a Trello card for the studio."""
        
        # Check for duplicates (API + local state)
        if self.card_exists(studio.name):
            print(f"  ⚠️  Card for '{studio.name}' already exists. Skipping.")
            return None
        
        # Get label ID
        labels = self.get_board_labels()
        label_id = labels.get(studio.priority_label)
        
        card_data = {
            "name": f"{studio.name} — {studio.primary_contact.full_name}",
            "desc": studio.to_card_description(),
            "idList": self.get_list_id(),
            "idLabels": [label_id] if label_id else [],
        }
        
        if dry_run:
            print(f"  [DRY RUN] Would create card:")
            print(f"    Title: {card_data['name']}")
            print(f"    Label: {studio.priority_label}")
            print(f"    Contact: {studio.primary_contact.email}")
            # Mark as processed even in dry run for testing idempotency
            if self.state:
                self.state.mark_processed(studio.name)
            return {"dry_run": True, "studio": studio.name}
        
        print(f"  Creating card for '{studio.name}'...")
        result = self._api_request("POST", "trello/cards", data=card_data)
        
        card = result.get("data", {})
        print(f"  ✅ Created: {card.get('shortUrl', 'N/A')}")
        
        # Mark as processed for idempotency
        if self.state:
            self.state.mark_processed(studio.name)
        
        return card


def parse_yaml_block(content: str, block_name: str) -> dict:
    """Extract a YAML block from markdown."""
    pattern = rf'###\s*{re.escape(block_name)}\s*\n```yaml\n(.*?)```'
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    if not match:
        return {}
    
    yaml_content = match.group(1)
    result = {}
    current_key = None
    current_list = []
    in_list = False
    
    for line in yaml_content.split('\n'):
        stripped = line.rstrip()
        if not stripped or stripped.startswith('#'):
            continue
        
        # Check for list item
        if stripped.strip().startswith('- '):
            if in_list and current_key:
                current_list.append(stripped.strip()[2:].strip())
            continue
        else:
            # End of list
            if in_list and current_key and current_list:
                result[current_key] = '\n'.join(current_list)
                current_list = []
                in_list = False
        
        # Check for key: value
        if ':' in stripped:
            key, value = stripped.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            if value:
                result[key] = value
                in_list = False
            else:
                # Might be a list coming
                current_key = key
                current_list = []
                in_list = True
    
    # Don't forget any pending list
    if in_list and current_key and current_list:
        result[current_key] = '\n'.join(current_list)
    
    return result


def parse_studios_from_deliverable(file_path: Path) -> List[Studio]:
    """Parse all studios from the deliverable file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Deliverable not found: {file_path}")
    
    content = file_path.read_text(encoding="utf-8")
    print(f"Loaded deliverable: {file_path}")
    print(f"Content size: {len(content)} characters")
    
    studios = []
    
    # Split by STUDIO headers (case insensitive)
    # Pattern: ## STUDIO N: Name
    parts = re.split(r'(##\s+STUDIO\s+\d+:[^\n]+\n)', content, flags=re.IGNORECASE)
    
    current_section = ""
    for part in parts:
        if re.match(r'##\s+STUDIO\s+\d+:', part, re.IGNORECASE):
            if current_section:
                studio = parse_studio_section(current_section)
                if studio:
                    studios.append(studio)
            current_section = part
        else:
            current_section += part
    
    # Process final section
    if current_section and re.search(r'##\s+STUDIO\s+\d+:', current_section, re.IGNORECASE):
        studio = parse_studio_section(current_section)
        if studio:
            studios.append(studio)
    
    return studios


def parse_studio_section(section: str) -> Optional[Studio]:
    """Parse a single studio section from the deliverable."""
    # Parse YAML blocks
    studio_yaml = parse_yaml_block(section, "Studio Entity")
    contact_yaml = parse_yaml_block(section, "Contact Entity")
    outreach_yaml = parse_yaml_block(section, "Outreach Context")
    
    if not studio_yaml or not contact_yaml:
        return None
    
    studio_name = studio_yaml.get('studio_name', '')
    if not studio_name:
        return None
    
    print(f"  Parsing: {studio_name}")
    
    # Build contact
    primary_contact = Contact(
        full_name=contact_yaml.get('full_name', ''),
        title=contact_yaml.get('title', ''),
        email=contact_yaml.get('email', ''),
        linkedin=contact_yaml.get('linkedin_profile_url', ''),
        seniority=contact_yaml.get('seniority_level', '')
    )
    
    # Key titles might be a list
    key_titles = studio_yaml.get('key_titles', '')
    
    tier = studio_yaml.get('tier', 'Tier-3')
    
    return Studio(
        name=studio_name,
        website=studio_yaml.get('website', ''),
        headquarters=studio_yaml.get('headquarters_location', ''),
        employee_count=studio_yaml.get('employee_count', ''),
        total_downloads=studio_yaml.get('total_downloads_estimate', ''),
        key_titles=key_titles,
        linkedin_company=studio_yaml.get('linkedin_company_url', ''),
        tier=tier,
        primary_contact=primary_contact,
        secondary_contact=None,
        targeting_angle=outreach_yaml.get('targeting_angle', ''),
        recent_news=outreach_yaml.get('recent_news_or_trigger', ''),
        why_now=outreach_yaml.get('why_now', ''),
        hypothesis=outreach_yaml.get('hypothesis_of_pain_or_opportunity', ''),
        personalization_hook=outreach_yaml.get('personalization_hook', ''),
        draft_subject=f"LiveOps Partnership: {studio_name}",
        draft_message=outreach_yaml.get('personalization_hook', '')
    )


def print_summary(studios: List[Studio]):
    """Print a summary of studios to be imported."""
    print("\n" + "="*70)
    print("IMPORT SUMMARY — BDR Studio Batch (March 4, 2026)")
    print("="*70)
    
    tier_counts = {"Tier-1": 0, "Tier-2": 0, "Tier-3": 0}
    
    for studio in studios:
        tier_counts[studio.tier] = tier_counts.get(studio.tier, 0) + 1
        label = studio.priority_label
        contact = studio.primary_contact
        
        print(f"\n  [{label}] {studio.name}")
        print(f"      Contact: {contact.full_name}")
        print(f"      Email:   {contact.email}")
        print(f"      Title:   {contact.title}")
    
    print("\n" + "-"*70)
    print(f"  Total Studios: {len(studios)}")
    print(f"    Tier-1 (P0 - Highest): {tier_counts.get('Tier-1', 0)}")
    print(f"    Tier-2 (P1 - Medium):  {tier_counts.get('Tier-2', 0)}")
    print(f"    Tier-3 (P2 - Lower):   {tier_counts.get('Tier-3', 0)}")
    print("="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Import BDR studios from deliverable to Trello",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python import_bdr_batch_march4.py --summary-only     # Preview what will be imported
  python import_bdr_batch_march4.py --dry-run          # Test without creating cards
  python import_bdr_batch_march4.py --reset-state      # Clear processed state and re-import
  python import_bdr_batch_march4.py                    # Execute import
        """
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and validate without creating cards"
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Only print summary, don't import"
    )
    parser.add_argument(
        "--reset-state",
        action="store_true",
        help="Clear import state to allow re-processing"
    )
    args = parser.parse_args()
    
    # Initialize state manager for idempotency
    state = ImportState(IMPORT_STATE_FILE)
    
    if args.reset_state:
        print("Resetting import state...")
        state.processed_studios = set()
        state.save()
        print("State cleared. All studios can be re-imported.")
        return
    
    # Check for API key (if not in summary-only mode)
    api_key = os.environ.get("MATON_API_KEY") or os.environ.get("TRELLO_API_KEY")
    if not api_key and not args.dry_run and not args.summary_only:
        print("Error: MATON_API_KEY or TRELLO_API_KEY environment variable is required for import.")
        print("")
        print("Set it with:")
        print("  export MATON_API_KEY=your_key_here")
        print("")
        print("Or run in dry-run mode to test parsing:")
        print("  python import_bdr_batch_march4.py --dry-run")
        sys.exit(1)
    
    # Parse deliverable
    try:
        print("="*70)
        print("PARSING DELIVERABLE")
        print("="*70)
        studios = parse_studios_from_deliverable(DELIVERABLE_PATH)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing deliverable: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    if not studios:
        print("Error: No studios found in deliverable.")
        sys.exit(1)
    
    # Print summary
    print_summary(studios)
    
    if args.summary_only:
        return
    
    # Import to Trello
    print("="*70)
    print("TRELLO IMPORT")
    print("="*70)
    
    if args.dry_run:
        print("[DRY RUN MODE — No cards will be created]\n")
    
    try:
        importer = TrelloImporter(api_key, state=state)
        
        created = 0
        skipped = 0
        failed = 0
        imported_studios = []
        failed_studios = []
        
        for i, studio in enumerate(studios, 1):
            print(f"\n[{i}/{len(studios)}] {studio.name}")
            
            try:
                result = importer.create_card(studio, dry_run=args.dry_run)
                if result is None:
                    skipped += 1
                elif result.get("dry_run"):
                    created += 1
                    imported_studios.append(studio.name)
                else:
                    created += 1
                    imported_studios.append(studio.name)
            except Exception as e:
                print(f"  ❌ Failed: {e}")
                failed += 1
                failed_studios.append((studio.name, str(e)))
        
        # Save state after successful processing
        state.save()
        
        # Final report
        print("\n" + "="*70)
        print("IMPORT COMPLETE")
        print("="*70)
        if args.dry_run:
            print(f"  Would create: {created}")
            print(f"  Would skip:   {skipped} (duplicates)")
            print(f"  Failed:       {failed}")
        else:
            print(f"  Created: {created}")
            print(f"  Skipped: {skipped} (duplicates)")
            print(f"  Failed:  {failed}")
        print(f"  State saved to: {IMPORT_STATE_FILE}")
        print("="*70)
        
        # Return exit code based on results
        if failed > 0:
            sys.exit(1)
        
    except Exception as e:
        print(f"\nImport failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
