import { EmptyState } from '../shared/components/ui';

export default function AutomationsPage() {
  return (
    <div className="animate-fade-in">
      <EmptyState
        icon={
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
            <path d="M4 17h16M4 7h16M4 12h12m-4 4l4-4-4-4" />
          </svg>
        }
        title="Sem fluxos ativos"
        description="Automatize boas-vindas, follow-ups e reengajamento."
        action={{ label: 'Novo fluxo', onClick: () => {} }}
      />
    </div>
  );
}
