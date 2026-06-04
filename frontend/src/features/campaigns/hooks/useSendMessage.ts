import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../../../shared/api/client';
import { ENDPOINTS } from '../../../shared/api/endpoints';
import type { Message } from '../../../shared/api/types';

interface SendMessagePayload {
  channel_id: string;
  recipient: string;
  content_type: 'text' | 'template' | 'media';
  text?: string;
  media_url?: string;
}

export function useSendMessage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: SendMessagePayload) =>
      apiClient.post<Message>(ENDPOINTS.sendMessage, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['messages'] });
    },
  });
}
