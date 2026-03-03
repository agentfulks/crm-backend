import { describe, it, expect } from 'vitest';
import { validatePacketForm, packetToFormData } from '../types/form';
import type { Packet, Fund } from '../types';

const mockFund: Fund = {
  id: 'fund-1',
  name: 'Test Fund',
  firm_type: 'VC',
  hq_city: 'San Francisco',
  hq_region: 'California',
  hq_country: 'USA',
  stage_focus: ['Series A'],
  check_size_min: 1000000,
  check_size_max: 5000000,
  check_size_currency: 'USD',
  website_url: 'https://testfund.com',
  linkedin_url: 'https://linkedin.com/company/testfund',
  overview: 'A test fund',
  contact_email: 'test@testfund.com',
  priority: 'A',
  status: 'READY',
  target_countries: ['USA'],
  tags: {},
  created_at: '2025-02-25T00:00:00Z',
  updated_at: '2025-02-25T00:00:00Z',
};

const mockPacket: Packet = {
  id: 'packet-1',
  fund_id: 'fund-1',
  fund: mockFund,
  status: 'AWAITING_APPROVAL',
  priority: 'A',
  score_snapshot: 85,
  created_at: '2025-02-25T00:00:00Z',
  updated_at: '2025-02-25T00:00:00Z',
};

describe('packetToFormData', () => {
  it('converts packet to form data correctly', () => {
    const formData = packetToFormData(mockPacket);
    
    expect(formData.name).toBe('Test Fund');
    expect(formData.firm_type).toBe('VC');
    expect(formData.priority).toBe('A');
    expect(formData.stage_focus).toEqual(['Series A']);
    expect(formData.check_size_min).toBe(1000000);
    expect(formData.check_size_max).toBe(5000000);
  });

  it('handles missing fund data gracefully', () => {
    const packetWithoutFund: Packet = {
      ...mockPacket,
      fund: undefined,
    };
    
    const formData = packetToFormData(packetWithoutFund);
    
    expect(formData.name).toBe('');
    expect(formData.firm_type).toBe('');
  });
});

describe('validatePacketForm', () => {
  it('returns empty array for valid data', () => {
    const formData = packetToFormData(mockPacket);
    const errors = validatePacketForm(formData);
    
    expect(errors).toHaveLength(0);
  });

  it('validates required fields', () => {
    const formData = packetToFormData(mockPacket);
    formData.name = '';
    formData.firm_type = '';
    
    const errors = validatePacketForm(formData);
    
    expect(errors).toContainEqual({ field: 'name', message: 'Fund name is required' });
    expect(errors).toContainEqual({ field: 'firm_type', message: 'Firm type is required' });
  });

  it('validates email format', () => {
    const formData = packetToFormData(mockPacket);
    formData.contact_email = 'invalid-email';
    
    const errors = validatePacketForm(formData);
    
    expect(errors).toContainEqual({ field: 'contact_email', message: 'Invalid email format' });
  });

  it('validates URL format', () => {
    const formData = packetToFormData(mockPacket);
    formData.website_url = 'not-a-url';
    formData.linkedin_url = 'also-not-valid';
    
    const errors = validatePacketForm(formData);
    
    expect(errors).toContainEqual({ field: 'website_url', message: 'Invalid URL format' });
    expect(errors).toContainEqual({ field: 'linkedin_url', message: 'Invalid URL format' });
  });

  it('validates check size is not negative', () => {
    const formData = packetToFormData(mockPacket);
    formData.check_size_min = -1000;
    
    const errors = validatePacketForm(formData);
    
    expect(errors).toContainEqual({ field: 'check_size_min', message: 'Check size cannot be negative' });
  });

  it('validates max check size is greater than min', () => {
    const formData = packetToFormData(mockPacket);
    formData.check_size_min = 5000000;
    formData.check_size_max = 1000000;
    
    const errors = validatePacketForm(formData);
    
    expect(errors).toContainEqual({ field: 'check_size_max', message: 'Max check size must be greater than min' });
  });

  it('accepts empty optional fields', () => {
    const formData = packetToFormData(mockPacket);
    formData.contact_email = '';
    formData.website_url = '';
    
    const errors = validatePacketForm(formData);
    
    expect(errors).not.toContainEqual(expect.objectContaining({ field: 'contact_email' }));
    expect(errors).not.toContainEqual(expect.objectContaining({ field: 'website_url' }));
  });
});
