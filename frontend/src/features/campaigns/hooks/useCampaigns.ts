import { useQuery } from '@tanstack/react-query';
import { useMemo } from 'react';
import { apiClient } from '../../../shared/api/client';
import { ENDPOINTS } from '../../../shared/api/endpoints';
import { useUIStore } from '../../../shared/store';
import type { Message, Campaign } from '../../../shared/api/types';

export function useCampaigns() {
  const filter = useUIStore((s) => s.campaignsFilter);

  const { data: messages, isLoading } = useQuery({
    queryKey: ['messages'],
    queryFn: () => apiClient.get<Message[]>(ENDPOINTS.messages),
  });

  const campaigns = useMemo<Campaign[]>(() => {
    if (!messages) return [];
    const grouped = new Map<string, Message[]>();
    for (const msg of messages) {
      const key = msg.channel_id;
      if (!grouped.has(key)) grouped.set(key, []);
      grouped.get(key)!.push(msg);
    }

    return Array.from(grouped.entries()).map(([channelId, msgs]) => {
      const sent = msgs.filter((m) => m.status === 'sent' || m.status === 'delivered' || m.status === 'read');
      const delivered = msgs.filter((m) => m.status === 'delivered' || m.status === 'read');
      return {
        id: channelId,
        name: `Campanha via ${channelId.slice(0, 8)}`,
        status: msgs.some((m) => m.status === 'failed') ? 'error'
          : msgs.some((m) => m.status === 'pending') ? 'active'
          : 'done',
        channel_id: channelId,
        recipient_count: msgs.length,
        sent_count: sent.length,
        delivered_count: delivered.length,
        replied_count: 0,
        created_at: msgs[0]?.created_at || new Date().toISOString(),
      } as Campaign;
    });
  }, [messages]);

  const filtered = useMemo(() => {
    if (filter === 'all') return campaigns;
    return campaigns.filter((c) => c.status === filter);
  }, [campaigns, filter]);

  return { campaigns: filtered, allCampaigns: campaigns, isLoading };
}

export function useCampaign(id: string) {
  const { campaigns } = useCampaigns();
  return campaigns.find((c) => c.id === id);
}
