"""Pydantic data models for Daily Intake Automation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class InvestorEntry(BaseModel):
    """Represents an investor entry from the CRM database."""
    
    id: str = Field(..., description="CRM entry ID")
    investor_name: str = Field(..., description="Full name of the investor")
    firm_name: str = Field(..., description="Investment firm name")
    job_title: str = Field(default="", description="Job title at the firm")
    email_address: str = Field(..., description="Primary email address")
    phone_number: Optional[str] = Field(default=None, description="Phone number")
    linkedin_profile_url: Optional[str] = Field(default=None, description="LinkedIn profile URL")
    investment_thesis_summary: Optional[str] = Field(default=None, description="Summary of investment focus")
    outreach_score: int = Field(..., description="Outreach priority score (0-100)", ge=0, le=100)
    created_at: datetime = Field(..., description="When the entry was created")
    updated_at: Optional[datetime] = Field(default=None, description="When the entry was last updated")
    
    @field_validator("investor_name", "firm_name")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Ensure required string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()
    
    @property
    def card_title(self) -> str:
        """Generate the card title for Trello."""
        return f"Investor Packet: {self.investor_name}"
    
    @property
    def card_description(self) -> str:
        """Generate the card description in markdown format."""
        lines = [
            "## Investor Information",
            "",
            f"**Name:** {self.investor_name}",
            f"**Firm:** {self.firm_name}",
            f"**Title:** {self.job_title}" if self.job_title else "",
            f"**Score:** {self.outreach_score}/100",
            "",
            "## Contact Details",
            "",
            f"- **Email:** {self.email_address}",
        ]
        
        if self.phone_number:
            lines.append(f"- **Phone:** {self.phone_number}")
        if self.linkedin_profile_url:
            lines.append(f"- **LinkedIn:** {self.linkedin_profile_url}")
        
        lines.extend([
            "",
            "## Investment Focus",
            "",
        ])
        
        if self.investment_thesis_summary:
            lines.append(self.investment_thesis_summary)
        else:
            lines.append("*No investment focus summary available.*")
        
        lines.extend([
            "",
            "## Source",
            "",
            f"CRM Entry ID: {self.id}",
            f"Created from Daily Intake Automation at {datetime.utcnow().isoformat()}",
        ])
        
        return "\n".join(lines)


class TrelloCard(BaseModel):
    """Represents a Trello card to be created."""
    
    name: str = Field(..., max_length=256, description="Card name/title")
    desc: str = Field(..., description="Card description (markdown)")
    idList: str = Field(..., description="List ID where card will be created")
    idLabels: list[str] = Field(default_factory=list, description="Label IDs to apply")
    pos: str = Field(default="top", description="Position in list (top, bottom, or position number)")
    due: Optional[str] = Field(default=None, description="Due date in ISO 8601 format")
    
    
class TrelloLabel(BaseModel):
    """Represents a Trello label."""
    
    id: str = Field(..., description="Label ID")
    name: str = Field(..., description="Label name")
    color: Optional[str] = Field(default=None, description="Label color")


class TrelloList(BaseModel):
    """Represents a Trello list."""
    
    id: str = Field(..., description="List ID")
    name: str = Field(..., description="List name")
    

class CardCreationResult(BaseModel):
    """Result of creating a Trello card."""
    
    success: bool = Field(..., description="Whether the creation was successful")
    investor_entry: InvestorEntry = Field(..., description="The source investor entry")
    trello_card_id: Optional[str] = Field(default=None, description="Created card ID if successful")
    trello_card_url: Optional[str] = Field(default=None, description="Created card URL if successful")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the result was recorded")
    dry_run: bool = Field(default=False, description="Whether this was a dry run")


class DailyIntakeResult(BaseModel):
    """Overall result of the daily intake process."""
    
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the job ran")
    total_entries_found: int = Field(..., description="Number of investor entries found")
    cards_created: int = Field(..., description="Number of cards successfully created")
    cards_skipped: int = Field(..., description="Number of cards skipped (duplicates)")
    cards_failed: int = Field(..., description="Number of cards that failed to create")
    dry_run: bool = Field(default=False, description="Whether this was a dry run")
    details: list[CardCreationResult] = Field(default_factory=list, description="Detailed results")
    
    @property
    def success_rate(self) -> float:
        """Calculate the success rate as a percentage."""
        if self.total_entries_found == 0:
            return 100.0
        return (self.cards_created / self.total_entries_found) * 100
