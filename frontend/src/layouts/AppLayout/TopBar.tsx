import { useLocation } from 'react-router-dom';
import { useUIStore } from '../../shared/store';
import { useMediaQuery } from '../../shared/hooks';

const pageTitles: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/campaigns': 'Campanhas',
  '/campaigns/new': 'Nova Campanha',
  '/contacts': 'Contatos',
  '/automations': 'Automações',
  '/schedules': 'Agendamentos',
  '/reports': 'Relatórios',
  '/settings': 'Configurações',
};

export function TopBar() {
  const location = useLocation();
  const toggleSidebar = useUIStore((s) => s.toggleSidebar);
  const isMobile = useMediaQuery('(max-width: 767px)');

  const title = Object.entries(pageTitles).find(([path]) =>
    location.pathname.startsWith(path)
  )?.[1] || 'ChannelFlow';

  return (
    <header className="flex items-center h-14 px-[var(--space-4)] bg-[var(--color-bg-base)] border-b border-[var(--color-border)]">
      {isMobile && (
        <button
          onClick={toggleSidebar}
          className="mr-[var(--space-3)] bg-transparent border-none text-[var(--color-text-secondary)]"
          aria-label="Abrir menu"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 12h18M3 6h18M3 18h18" strokeLinecap="round" />
          </svg>
        </button>
      )}
      <h1 className="text-[var(--font-size-lg)] font-semibold text-[var(--color-text-primary)]">
        {title}
      </h1>
      <div className="flex-1" />
    </header>
  );
}
