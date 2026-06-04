import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button, Input } from '../../../shared/components/ui';
import type { CampaignFormData } from '../types';

const schema = z.object({
  name: z.string().min(1, 'Nome é obrigatório'),
  channel_id: z.string().min(1, 'Selecione um canal'),
  content_type: z.enum(['text', 'template']),
  text: z.string().min(1, 'Mensagem é obrigatória'),
  contact_ids: z.array(z.string()).min(1, 'Selecione ao menos um contato'),
  scheduled_at: z.string().optional(),
});

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
        error={errors.name?.message}
        {...register('name')}
      />
      <Input
        label="ID do Canal"
        error={errors.channel_id?.message}
        {...register('channel_id')}
      />
      <div className="flex flex-col gap-[var(--space-1)]">
        <label className="text-[var(--font-size-sm)] font-medium text-[var(--color-text-secondary)]">
          Tipo de conteúdo
        </label>
        <select
          className="rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-bg-base)] px-[var(--space-3)] py-[var(--space-2)] text-[var(--font-size-base)]"
          {...register('content_type')}
        >
          <option value="text">Texto</option>
          <option value="template">Template</option>
        </select>
      </div>
      <div className="flex flex-col gap-[var(--space-1)]">
        <label className="text-[var(--font-size-sm)] font-medium text-[var(--color-text-secondary)]">
          Mensagem
        </label>
        <textarea
          className="rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-bg-base)] px-[var(--space-3)] py-[var(--space-2)] text-[var(--font-size-base)] min-h-[100px] resize-y"
          {...register('text')}
        />
        {errors.text && (
          <span className="text-[var(--font-size-xs)] text-[var(--color-danger)]">{errors.text.message}</span>
        )}
      </div>
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
