import axios from 'axios';
import type {
  Packet,
  PacketListResponse,
  QueueStatus,
  Fund,
  StudioPacket,
  EmailTemplate,
  EmailTemplateListResponse
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============================================
// PRODUCTION API - VC FUNDS
// ============================================

export const fundsApi = {
  async listFunds(): Promise<{ items: Fund[] }> {
    const response = await api.get('/funds');
    return response.data;
  },

  async getFund(id: string): Promise<Fund> {
    const response = await api.get(`/funds/${id}`);
    return response.data;
  },
};

export const packetsApi = {
  async listPackets(status?: string): Promise<PacketListResponse> {
    const params = status ? { status } : {};
    const response = await api.get('/packets', { params });
    return response.data;
  },

  async getPendingPackets(): Promise<PacketListResponse> {
    const response = await api.get('/packets', { params: { status: 'AWAITING_APPROVAL' } });
    return response.data;
  },

  async approvePacket(id: string): Promise<Packet> {
    const response = await api.post(`/packets/${id}/approve`);
    return response.data;
  },

  async rejectPacket(id: string): Promise<Packet> {
    const response = await api.post(`/packets/${id}/reject`);
    return response.data;
  },

  async updatePacketStatus(id: string, status: string): Promise<Packet> {
    const response = await api.patch(`/packets/${id}`, { status });
    return response.data;
  },

  async getQueueStatus(): Promise<QueueStatus> {
    const response = await api.get('/packets/queue/status');
    return response.data;
  },
};

// ============================================
// PRODUCTION API - BDR STUDIOS
// ============================================

// Get studios from bdr_companies table via API
export const studiosApi = {
  async listStudios(): Promise<{ items: any[] }> {
    // Using the bdr_companies endpoint
    const response = await api.get('/bdr/companies/');
    return response.data;
  },

  async getStudio(id: string): Promise<any> {
    const response = await api.get(`/bdr/companies/${id}/`);
    return response.data;
  },
};

// Studio packets - combining company data with contacts
export const studioPacketsApi = {
  async listStudioPackets(status?: string): Promise<{ total: number; items: StudioPacket[] }> {
    // Get companies from bdr_companies
    const companiesResponse = await api.get('/bdr/companies/', { 
      params: status ? { status } : {} 
    });
    
    // Get all contacts from bdr_contacts
    const contactsResponse = await api.get('/bdr/contacts/');
    const contactsByCompany: Record<string, any[]> = {};
    
    // Group contacts by company_id
    contactsResponse.data?.items?.forEach((contact: any) => {
      if (!contactsByCompany[contact.company_id]) {
        contactsByCompany[contact.company_id] = [];
      }
      contactsByCompany[contact.company_id].push(contact);
    });
    
    // Transform to StudioPacket format
    const items = companiesResponse.data.items?.map((company: any, index: number) => {
      // Get contacts for this company
      const companyContacts = contactsByCompany[company.id] || [];
      
      // Prefer decision maker, then champion, then first contact
      const primaryContact = companyContacts.find((c: any) => c.is_decision_maker) ||
                            companyContacts.find((c: any) => c.is_champion) ||
                            companyContacts[0];
      
      // Parse contact info
      const contactName = primaryContact?.full_name || 
                         company.ideal_buyer_persona?.split('(')[0]?.trim() || 
                         'CEO';
      const contactRole = primaryContact?.job_title || 
                         company.ideal_buyer_persona?.match(/\(([^)]+)\)/)?.[1] || 
                         'CEO';
      
      return {
        id: `studio-packet-${company.id || index}`,
        studio_id: company.id,
        studio: {
          id: company.id,
          name: company.company_name,
          hq_city: company.headquarters_city,
          hq_region: company.headquarters_state,
          hq_country: company.headquarters_country,
          studio_type: company.industry || 'Game Studio',
          employee_count: company.company_size,
          overview: company.use_case_fit || `${company.company_name} - ${company.industry || 'Game Studio'}`,
          priority: company.priority === 'A' ? 'A' : company.priority === 'B' ? 'B' : 'C',
          status: 'READY',
          website_url: company.website_url || `https://${company.company_name?.toLowerCase().replace(/\s+/g, '')}.com`,
          linkedin_url: `https://linkedin.com/company/${company.company_name?.toLowerCase().replace(/\s+/g, '-')}`.substring(0, 100),
          created_at: company.created_at,
          updated_at: company.updated_at,
        },
        contact_name: contactName,
        contact_role: contactRole,
        contact_email: primaryContact?.email || '',
        contact_linkedin: primaryContact?.linkedin_url || '',
        status: (company.status?.toUpperCase().replace(' ', '_') || 'NEW') as any,
        priority: (company.priority || 'B') as any,
        score_snapshot: company.icp_score || 75,
        email_draft: {
          to: primaryContact?.email || '',
          subject: `Partnership opportunity - ${company.company_name}`,
          body: `Hi ${contactName.split(' ')[0] || 'there'},\n\nI'm reaching out about a partnership opportunity with ${company.company_name}.\n\nBest,\nLucas Fulks`,
        },
        created_at: company.created_at,
        updated_at: company.updated_at,
      };
    }) || [];
    
    return { 
      total: companiesResponse.data.total || items.length, 
      items 
    };
  },

  async getPendingStudioPackets(): Promise<{ total: number; items: StudioPacket[] }> {
    return this.listStudioPackets('AWAITING_APPROVAL');
  },

  async approveStudioPacket(id: string): Promise<StudioPacket> {
    const companyId = id.replace('studio-packet-', '');
    const response = await api.patch(`/bdr/companies/${companyId}/`, { status: 'APPROVED' });
    return response.data;
  },

  async rejectStudioPacket(id: string): Promise<StudioPacket> {
    const companyId = id.replace('studio-packet-', '');
    const response = await api.patch(`/bdr/companies/${companyId}/`, { status: 'CLOSED' });
    return response.data;
  },

  async updateStudioPacketStatus(id: string, status: string): Promise<StudioPacket> {
    const companyId = id.replace('studio-packet-', '');
    const response = await api.patch(`/bdr/companies/${companyId}/`, { status });
    return response.data;
  },

  async getStudioQueueStatus(): Promise<QueueStatus> {
    const response = await api.get('/bdr/companies');
    const items = response.data.items || [];
    
    return {
      date: new Date().toISOString().split('T')[0],
      total_queued: items.filter((c: any) => c.status === 'QUEUED').length,
      awaiting_approval: items.filter((c: any) => c.status === 'AWAITING_APPROVAL').length,
      approved_today: 0,
      sent_today: items.filter((c: any) => c.status === 'SENT').length,
    };
  },
};

// ============================================
// EMAIL TEMPLATES API
// ============================================

export const emailTemplatesApi = {
  async listTemplates(category?: string): Promise<EmailTemplateListResponse> {
    const params = category ? { category } : {};
    const response = await api.get('/email-templates', { params });
    return response.data;
  },

  async getTemplate(id: string): Promise<EmailTemplate> {
    const response = await api.get(`/email-templates/${id}`);
    return response.data;
  },

  async createTemplate(data: Partial<EmailTemplate>): Promise<EmailTemplate> {
    const response = await api.post('/email-templates', data);
    return response.data;
  },

  async updateTemplate(id: string, data: Partial<EmailTemplate>): Promise<EmailTemplate> {
    const response = await api.patch(`/email-templates/${id}`, data);
    return response.data;
  },

  async deleteTemplate(id: string): Promise<void> {
    await api.delete(`/email-templates/${id}`);
  },

  async applyTemplate(templateId: string, studioName: string, contactName: string): Promise<{ subject: string; body: string }> {
    const response = await api.post(
      `/email-templates/${templateId}/apply`,
      null,
      { params: { studio_name: studioName, contact_name: contactName } }
    );
    return response.data;
  },
};

// Legacy exports for backward compatibility
export const fundApi = fundsApi;
export const packetApi = packetsApi;
export const studioApi = studioPacketsApi;

// Export the axios instance for direct use
export { api };

export default api;
