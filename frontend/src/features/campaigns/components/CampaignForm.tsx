import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button, Input, Select, Textarea } from '../../../shared/components/ui';
import type { CampaignFormData } from '../types';

const schema = z.object({
  name: z.string().min(1, 'Nome é obrigatório'),
  channel_id: z.string().min(1, 'Selecione um canal'),
  content_type: z.enum(['text', 'template']),
  text: z.string().min(1, 'Mensagem é obrigatória'),
  contact_ids: z.array(z.string()).min(1, 'Selecione ao menos um contato'),
  scheduled_at: z.string().optional(),
});

const channelOptions = [
  { value: 'wa-1', label: 'WhatsApp - Comercial' },
  { value: 'wa-2', label: 'WhatsApp - Suporte' },
  { value: 'tg-1', label: 'Telegram - Geral' },
];

const contentTypeOptions = [
  { value: 'text', label: 'Texto' },
  { value: 'template', label: 'Template' },
];

interface CampaignFormProps {
  onSubmit: (data: CampaignFormData) => void;
  loading?: boolean;
}

export function CampaignForm({ onSubmit, loading }: CampaignFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CampaignFormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: '',
      channel_id: '',
      content_type: 'text',
      text: '',
      contact_ids: [],
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-[var(--space-4)]">
      <Input
        label="Nome da campanha"
        placeholder="Ex: Black Friday 2024"
        error={errors.name?.message}
        {...register('name')}
      />
      <Select
        label="Canal"
        placeholder="Selecione um canal"
        options={channelOptions}
        error={errors.channel_id?.message}
        {...register('channel_id')}
      />
      <Select
        label="Tipo de conteúdo"
        options={contentTypeOptions}
        {...register('content_type')}
      />
      <Textarea
        label="Mensagem"
        placeholder="Digite a mensagem da campanha..."
        error={errors.text?.message}
        {...register('text')}
      />
      <Input
        label="Agendamento (opcional)"
        type="datetime-local"
        error={errors.scheduled_at?.message}
        {...register('scheduled_at')}
      />
      <Button type="submit" loading={loading} size="lg" fullWidth>
        Criar campanha
      </Button>
    </form>
  );
}
