import { useNavigate } from 'react-router-dom';
import { CampaignForm } from '../features/campaigns/components/CampaignForm';
import { useSendMessage } from '../features/campaigns/hooks/useSendMessage';
import type { CampaignFormData } from '../features/campaigns/types';

export default function CampaignNewPage() {
  const navigate = useNavigate();
  const sendMessage = useSendMessage();

  const handleSubmit = async (data: CampaignFormData) => {
    await sendMessage.mutateAsync({
      channel_id: data.channel_id,
      recipient: '',
      content_type: data.content_type,
      text: data.text,
    });
    navigate('/campaigns');
  };

  return (
    <div className="max-w-2xl">
      <button
        onClick={() => navigate('/campaigns')}
        className="text-[var(--font-size-sm)] text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)] bg-transparent border-none mb-[var(--space-3)]"
      >
        ← Voltar para campanhas
      </button>
      <h1 className="text-[var(--font-size-xl)] font-bold text-[var(--color-text-primary)] mb-[var(--space-6)]">
        Nova campanha
      </h1>
      <div className="rounded-[var(--radius-md)] bg-[var(--color-bg-base)] border border-[var(--color-border)] p-[var(--space-6)]">
        <CampaignForm onSubmit={handleSubmit} loading={sendMessage.isPending} />
      </div>
    </div>
  );
}
