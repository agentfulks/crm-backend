#!/usr/bin/env python3
"""Generate missing Trello import CSV files for VC outreach batches."""

import json
import csv
import os
from pathlib import Path

# Days that need CSV generation
MISSING_CSV_DAYS = [3, 4, 5, 6, 10, 11, 12, 13, 14, 15, 16, 17, 18, 23, 24, 25, 26]

def format_check_size(check_size):
    """Format check size for display."""
    if isinstance(check_size, dict):
        min_val = check_size.get('min_usd', 0)
        max_val = check_size.get('max_usd', 0)
        if min_val and max_val:
            if min_val >= 1000000:
                min_str = f"${min_val/1000000:.1f}M"
            else:
                min_str = f"${min_val/1000:.0f}K"
            if max_val >= 1000000:
                max_str = f"${max_val/1000000:.1f}M"
            else:
                max_str = f"${max_val/1000:.0f}K"
            return f"{min_str}-{max_str}"
        return check_size.get('range', 'TBD')
    return str(check_size)

def get_partner_info(packet):
    """Extract partner info from packet."""
    # Try different field names
    if 'target_partner' in packet:
        return packet['target_partner']
    if 'partner' in packet:
        return packet['partner']
    if 'primary_contact' in packet:
        return packet['primary_contact']
    return {}

def get_score(packet):
    """Extract score from packet."""
    if 'score' in packet:
        return packet['score']
    if 'signal_score' in packet:
        return packet['signal_score']
    if 'fit_score' in packet:
        return packet['fit_score']
    return 85  # default

def get_thesis(packet):
    """Extract thesis from packet."""
    if 'thesis' in packet:
        return packet['thesis']
    if 'investment_thesis' in packet:
        return packet['investment_thesis']
    if 'gaming_ai_thesis' in packet:
        return packet['gaming_ai_thesis']
    return 'Gaming/AI infrastructure focus'

def get_stage(packet):
    """Extract stage from packet."""
    if 'stage_focus' in packet:
        if isinstance(packet['stage_focus'], list):
            return ', '.join(packet['stage_focus'])
        return packet['stage_focus']
    if 'stages' in packet:
        if isinstance(packet['stages'], list):
            return ', '.join(packet['stages'])
        return packet['stages']
    if 'stage' in packet:
        return packet['stage']
    return 'Seed to Series A'

def get_priority_rank(packet, index):
    """Get priority rank."""
    if 'priority_rank' in packet:
        return packet['priority_rank']
    return index + 1

def generate_csv_for_day(day_num):
    """Generate trello_import.csv for a specific day."""
    base_path = Path(f'/data/workspace/deliverables/day{day_num}_vc_batch')
    packets_file = base_path / 'packets.json'
    
    if not packets_file.exists():
        print(f"  ⚠️  Day {day_num}: packets.json not found")
        return False
    
    try:
        with open(packets_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"  ⚠️  Day {day_num}: Error reading packets.json: {e}")
        return False
    
    # Extract packets array - handle different structures
    packets = []
    if isinstance(data, list):
        packets = data
    elif isinstance(data, dict):
        if 'packets' in data:
            packets = data['packets']
        elif 'vc_targets' in data:
            packets = data['vc_targets']
    
    if not packets:
        print(f"  ⚠️  Day {day_num}: No packets found")
        return False
    
    # Generate CSV rows
    csv_rows = []
    for i, packet in enumerate(packets):
        fund_name = packet.get('fund_name', 'Unknown Fund')
        partner = get_partner_info(packet)
        partner_name = partner.get('name', 'Unknown Partner')
        partner_title = partner.get('title', '')
        partner_email = partner.get('email', '')
        score = get_score(packet)
        thesis = get_thesis(packet)
        stage = get_stage(packet)
        check_size = format_check_size(packet.get('check_size', packet.get('check_size_range', 'TBD')))
        priority = get_priority_rank(packet, i)
        location = packet.get('location', packet.get('geographic_focus', 'Global'))
        
        # Build description
        description = f"""**Fund:** {fund_name}
**Partner:** {partner_name} ({partner_title})
**Email:** {partner_email}
**Priority:** P{priority}
**Score:** {score}/100
**Stage:** {stage}
**Check Size:** {check_size}
**Location:** {location}

**Thesis:** {thesis}

**Packet:** Day {day_num} | Ready for review"""
        
        card_name = f"Packet: {fund_name}"
        csv_rows.append({
            'Name': card_name,
            'Description': description,
            'List': 'Daily Queue'
        })
    
    # Write CSV
    output_file = base_path / 'trello_import.csv'
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Name', 'Description', 'List'])
        writer.writeheader()
        writer.writerows(csv_rows)
    
    print(f"  ✓ Day {day_num}: Created {output_file} ({len(csv_rows)} cards)")
    return True

def main():
    """Main entry point."""
    print("Generating missing Trello CSV files...")
    print("=" * 50)
    
    success_count = 0
    for day in MISSING_CSV_DAYS:
        if generate_csv_for_day(day):
            success_count += 1
    
    print("=" * 50)
    print(f"Complete: {success_count}/{len(MISSING_CSV_DAYS)} days processed")
    
    # Summary of all CSVs now available
    print("\nTrello CSV Status:")
    all_days = range(1, 32)
    for day in all_days:
        csv_path = Path(f'/data/workspace/deliverables/day{day}_vc_batch/trello_import.csv')
        status = "✓" if csv_path.exists() else "✗"
        print(f"  Day {day:2d}: {status}")

if __name__ == '__main__':
    main()
