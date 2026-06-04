import { EmptyState } from '../shared/components/ui';

export default function AutomationsPage() {
  return (
    <EmptyState
      title="Sem fluxos ativos"
      description="Automatize boas-vindas, follow-ups e reengajamento."
      action={{ label: 'Novo fluxo', onClick: () => {} }}
    />
  );
}
