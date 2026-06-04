import { EmptyState } from '../shared/components/ui';

export default function SchedulesPage() {
  return (
    <EmptyState
      title="Nada agendado"
      description="Programe mensagens para o momento certo."
      action={{ label: 'Novo agendamento', onClick: () => {} }}
    />
  );
}
