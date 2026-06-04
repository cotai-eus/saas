import { useNavigate } from 'react-router-dom';
import { useCampaigns } from '../features/campaigns/hooks/useCampaigns';
import { CampaignTable } from '../features/campaigns/components/CampaignTable';
import { Button, EmptyState } from '../shared/components/ui';
import { useUIStore } from '../shared/store';
import { useDebounce } from '../shared/hooks';
import { cn } from '../shared/utils/cn';
import { useState } from 'react';
import type { CampaignStatus } from '../shared/api/types';

const FILTERS: { label: string; value: CampaignStatus | 'all' }[] = [
  { label: 'Todas', value: 'all' },
  { label: 'Ativas', value: 'active' },
  { label: 'Agendadas', value: 'scheduled' },
  { label: 'Pausadas', value: 'paused' },
  { label: 'Concluídas', value: 'done' },
];

export default function CampaignsPage() {
  const navigate = useNavigate();
  const { campaigns, allCampaigns, isLoading } = useCampaigns();
  const filter = useUIStore((s) => s.campaignsFilter);
  const setFilter = useUIStore((s) => s.setCampaignsFilter);
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebounce(search, 300);

  const filtered = campaigns.filter((c) =>
    c.name.toLowerCase().includes(debouncedSearch.toLowerCase())
  );

  return (
    <div className="flex flex-col gap-[var(--space-4)]">
      <div className="flex items-center justify-between">
        <div className="flex gap-[var(--space-1)]">
          {FILTERS.map((f) => (
            <button
              key={f.value}
              onClick={() => setFilter(f.value)}
              className={cn(
                'px-[var(--space-3)] py-[var(--space-1)] rounded-[var(--radius-md)] text-[var(--font-size-sm)] font-medium transition-colors border-none',
                filter === f.value
                  ? 'bg-[var(--color-brand)] text-white'
                  : 'bg-[var(--color-bg-subtle)] text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-muted)]',
              )}
            >
              {f.label}
            </button>
          ))}
        </div>
        <Button onClick={() => navigate('/campaigns/new')}>
          Nova campanha
        </Button>
      </div>

      <div className="relative">
        <input
          type="text"
          placeholder="Buscar campanhas..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-bg-base)] px-[var(--space-3)] py-[var(--space-2)] pl-[var(--space-8)] text-[var(--font-size-base)]"
        />
        <svg
          className="absolute left-[var(--space-2)] top-1/2 -translate-y-1/2 text-[var(--color-text-muted)]"
          width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
        >
          <circle cx="11" cy="11" r="8" />
          <path d="M21 21l-4.35-4.35" strokeLinecap="round" />
        </svg>
      </div>

      {allCampaigns.length === 0 && !isLoading ? (
        <EmptyState
          title="Nenhuma campanha ainda"
          description="Crie sua primeira campanha e comece a se comunicar em escala."
          action={{ label: 'Nova campanha', onClick: () => navigate('/campaigns/new') }}
        />
      ) : (
        <div className="rounded-[var(--radius-md)] bg-[var(--color-bg-base)] border border-[var(--color-border)]">
          <CampaignTable campaigns={filtered} />
        </div>
      )}
    </div>
  );
}
