// Extended types for editing
import type { Packet } from '../types';

export interface PacketFormData {
  // Packet-level fields
  priority: 'A' | 'B' | 'C';
  
  // Fund-level fields
  name: string;
  firm_type: string;
  hq_city: string;
  hq_region: string;
  hq_country: string;
  stage_focus: string[];
  check_size_min?: number;
  check_size_max?: number;
  check_size_currency: string;
  website_url: string;
  linkedin_url: string;
  twitter_url: string;
  overview: string;
  contact_email: string;
  funding_requirements: string;
}

export interface ValidationError {
  field: string;
  message: string;
}

export function packetToFormData(packet: Packet): PacketFormData {
  const fund = packet.fund;
  return {
    priority: packet.priority,
    name: fund?.name || '',
    firm_type: fund?.firm_type || '',
    hq_city: fund?.hq_city || '',
    hq_region: fund?.hq_region || '',
    hq_country: fund?.hq_country || '',
    stage_focus: fund?.stage_focus || [],
    check_size_min: fund?.check_size_min,
    check_size_max: fund?.check_size_max,
    check_size_currency: fund?.check_size_currency || 'USD',
    website_url: fund?.website_url || '',
    linkedin_url: fund?.linkedin_url || '',
    twitter_url: fund?.twitter_url || '',
    overview: fund?.overview || '',
    contact_email: fund?.contact_email || '',
    funding_requirements: fund?.funding_requirements || '',
  };
}

export function validatePacketForm(data: PacketFormData): ValidationError[] {
  const errors: ValidationError[] = [];
  
  if (!data.name.trim()) {
    errors.push({ field: 'name', message: 'Fund name is required' });
  }
  
  if (!data.firm_type.trim()) {
    errors.push({ field: 'firm_type', message: 'Firm type is required' });
  }
  
  if (data.contact_email && !isValidEmail(data.contact_email)) {
    errors.push({ field: 'contact_email', message: 'Invalid email format' });
  }
  
  if (data.website_url && !isValidUrl(data.website_url)) {
    errors.push({ field: 'website_url', message: 'Invalid URL format' });
  }
  
  if (data.linkedin_url && !isValidUrl(data.linkedin_url)) {
    errors.push({ field: 'linkedin_url', message: 'Invalid URL format' });
  }
  
  if (data.twitter_url && !isValidUrl(data.twitter_url)) {
    errors.push({ field: 'twitter_url', message: 'Invalid URL format' });
  }
  
  if (data.check_size_min !== undefined && data.check_size_min < 0) {
    errors.push({ field: 'check_size_min', message: 'Check size cannot be negative' });
  }
  
  if (data.check_size_max !== undefined && data.check_size_max < 0) {
    errors.push({ field: 'check_size_max', message: 'Check size cannot be negative' });
  }
  
  if (data.check_size_min !== undefined && data.check_size_max !== undefined) {
    if (data.check_size_max < data.check_size_min) {
      errors.push({ field: 'check_size_max', message: 'Max check size must be greater than min' });
    }
  }
  
  return errors;
}

function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}
