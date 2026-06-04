import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../../shared/api/client';
import { ENDPOINTS } from '../../../shared/api/endpoints';
import type { Contact } from '../../../shared/api/types';

export function useContacts() {
  return useQuery({
    queryKey: ['contacts'],
    queryFn: () => apiClient.get<Contact[]>(ENDPOINTS.contacts),
  });
}

export function useContact(id: string) {
  return useQuery({
    queryKey: ['contacts', id],
    queryFn: () => apiClient.get<Contact>(ENDPOINTS.contact(id)),
    enabled: !!id,
  });
}
