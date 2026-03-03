import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { emailTemplatesApi } from '../api';
import type { EmailTemplate } from '../types';

// Hook to fetch all email templates
export function useEmailTemplates(category?: string) {
  return useQuery({
    queryKey: ['email-templates', category],
    queryFn: () => emailTemplatesApi.listTemplates(category),
  });
}

// Hook to fetch a single email template
export function useEmailTemplate(id: string) {
  return useQuery({
    queryKey: ['email-template', id],
    queryFn: () => emailTemplatesApi.getTemplate(id),
    enabled: !!id,
  });
}

// Hook to create a new email template
export function useCreateEmailTemplate() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: Partial<EmailTemplate>) => emailTemplatesApi.createTemplate(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['email-templates'] });
    },
  });
}

// Hook to update an email template
export function useUpdateEmailTemplate() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<EmailTemplate> }) => 
      emailTemplatesApi.updateTemplate(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['email-templates'] });
    },
  });
}

// Hook to delete an email template
export function useDeleteEmailTemplate() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => emailTemplatesApi.deleteTemplate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['email-templates'] });
    },
  });
}

// Hook to apply a template and get rendered email
export function useApplyTemplate() {
  return useMutation({
    mutationFn: ({ 
      templateId, 
      studioName, 
      contactName 
    }: { 
      templateId: string; 
      studioName: string; 
      contactName: string 
    }) => emailTemplatesApi.applyTemplate(templateId, studioName, contactName),
  });
}
