export interface User {
  user_id: string | null;
  email: string | null;
  tenant_id: string | null;
  roles: string[];
  groups: string[];
}

export interface Channel {
  id: string;
  type: 'whatsapp' | 'telegram' | 'messenger' | 'instagram';
  name: string;
  phone_number: string;
  status: 'connected' | 'disconnected' | 'expired' | 'pending';
  config: Record<string, unknown>;
  created_at: string;
}

export interface Message {
  id: string;
  channel_id: string;
  recipient: string;
  content_type: 'text' | 'template' | 'media';
  text?: string;
  media_url?: string;
  status: 'pending' | 'sent' | 'delivered' | 'read' | 'failed' | 'scheduled';
  direction: 'outbound' | 'inbound';
  sent_at?: string;
  scheduled_at?: string;
  delivered_at?: string;
  read_at?: string;
  created_at: string;
}

export interface Contact {
  id: string;
  name: string;
  email?: string;
  phone: string;
  channel_id: string;
  status: 'active' | 'unsubscribed' | 'bounce';
  metadata?: Record<string, unknown>;
  last_interaction_at?: string;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export type CampaignStatus = 'active' | 'scheduled' | 'paused' | 'done' | 'draft' | 'error';

export interface Campaign {
  id: string;
  name: string;
  status: CampaignStatus;
  channel_id: string;
  channel_name?: string;
  recipient_count: number;
  sent_count: number;
  delivered_count: number;
  replied_count: number;
  scheduled_at?: string;
  created_at: string;
}
