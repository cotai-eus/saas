export interface CampaignFormData {
  name: string;
  channel_id: string;
  contact_ids: string[];
  content_type: 'text' | 'template';
  text: string;
  scheduled_at?: string;
}
