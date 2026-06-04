import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../../../shared/api/client';
import { ENDPOINTS } from '../../../shared/api/endpoints';
import type { Channel } from '../../../shared/api/types';

export function useChannels() {
  return useQuery({
    queryKey: ['channels'],
    queryFn: () => apiClient.get<Channel[]>(ENDPOINTS.channels),
  });
}

export function useChannel(id: string) {
  return useQuery({
    queryKey: ['channels', id],
    queryFn: () => apiClient.get<Channel>(ENDPOINTS.channel(id)),
    enabled: !!id,
  });
}

export function useChannelQR(id: string) {
  return useQuery({
    queryKey: ['channels', id, 'qr'],
    queryFn: () => apiClient.get<{ qrcode: string }>(ENDPOINTS.channelQR(id)),
    enabled: !!id,
    refetchInterval: 3000,
  });
}

export function useCreateChannel() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { type: string; name: string; phone_number: string }) =>
      apiClient.post<Channel>(ENDPOINTS.channels, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['channels'] }),
  });
}

export function useValidateChannel() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => apiClient.post<Channel>(ENDPOINTS.channelValidate(id), {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['channels'] }),
  });
}
