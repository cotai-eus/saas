import { NavLink } from 'react-router-dom';
import { useUIStore } from '../../shared/store';
import { useAuthStore } from '../../shared/store';
import { useMediaQuery } from '../../shared/hooks';
import { cn } from '../../shared/utils/cn';
import { useState } from 'react';

const navGroups = [
  {
    group: 'Principal',
    items: [
      { label: 'Dashboard', path: '/dashboard', icon: 'chart-bar' },
      { label: 'Campanhas', path: '/campaigns', icon: 'send' },
      { label: 'Contatos', path: '/contacts', icon: 'users' },
      { label: 'Automações', path: '/automations', icon: 'arrows-shuffle' },
      { label: 'Agendamentos', path: '/schedules', icon: 'calendar' },
      { label: 'Relatórios', path: '/reports', icon: 'chart-line' },
    ],
  },
  {
    group: 'Sistema',
    items: [
      { label: 'Configurações', path: '/settings', icon: 'settings' },
    ],
  },
];

function NavIcon({ icon }: { icon: string }) {
  const icons: Record<string, string> = {
    'chart-bar': 'M4 20h16M6 16l4-4m4 0l4 4M8 12l4-4 4 4',
    'send': 'M5 12l14-7-7 14-3-4-4-3zm0 0l4 3',
    'users': 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197',
    'arrows-shuffle': 'M4 17h16M4 7h16M4 12h12m-4 4l4-4-4-4',
    'calendar': 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
    'chart-line': 'M3 20h18M3 16l4-8 4 4 4-8 4 4',
    'settings': 'M12 15a3 3 0 100-6 3 3 0 000 6zm0 0v3m0-12V3m0 3a9 9 0 00-9 9m18 0a9 9 0 00-9-9',
  };

  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d={icons[icon] || icons['chart-bar']} />
    </svg>
  );
}

export function Sidebar() {
  const collapsed = useUIStore((s) => s.sidebarCollapsed);
  const toggleSidebar = useUIStore((s) => s.toggleSidebar);
  const user = useAuthStore((s) => s.user);
  const isMobile = useMediaQuery('(max-width: 767px)');
  const [mobileOpen, setMobileOpen] = useState(false);

  const sidebarContent = (
    <aside
      className={cn(
        'flex flex-col bg-[var(--color-bg-base)] border-r border-[var(--color-border)] h-full transition-all duration-200 z-40',
        collapsed && !isMobile ? 'w-[var(--sidebar-collapsed-width)]' : 'w-[var(--sidebar-width)]',
        isMobile && 'fixed left-0 top-0',
        isMobile && !mobileOpen && '-translate-x-full',
      )}
    >
      <div className="flex items-center h-14 px-[var(--space-4)] border-b border-[var(--color-border)]">
        <span className={cn('font-bold text-[var(--color-brand)] text-[var(--font-size-lg)]', collapsed && !isMobile && 'hidden')}>
          SaaS
        </span>
        <button
          onClick={isMobile ? () => setMobileOpen(false) : toggleSidebar}
          className="ml-auto bg-transparent border-none text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]"
          aria-label={collapsed ? 'Expandir sidebar' : 'Colapsar sidebar'}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d={collapsed ? 'M9 5l7 7-7 7' : 'M15 5l-7 7 7 7'} strokeLinecap="round" />
          </svg>
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto py-[var(--space-3)]">
        {navGroups.map((group) => (
          <div key={group.group} className="mb-[var(--space-2)]">
            {!collapsed && (
              <p className="px-[var(--space-4)] mb-[var(--space-1)] text-[var(--font-size-xs)] font-semibold uppercase tracking-wider text-[var(--color-text-muted)]">
                {group.group}
              </p>
            )}
            {group.items.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/dashboard'}
                onClick={() => isMobile && setMobileOpen(false)}
                className={({ isActive }: { isActive: boolean }) =>
                  cn(
                    'flex items-center gap-[var(--space-3)] px-[var(--space-4)] py-[var(--space-2)] mx-[var(--space-2)] rounded-[var(--radius-md)] text-[var(--font-size-base)] font-medium transition-colors no-underline',
                    isActive
                      ? 'bg-[var(--color-brand-light)] text-[var(--color-brand-dark)]'
                      : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-subtle)] hover:text-[var(--color-text-primary)]',
                    collapsed && !isMobile && 'justify-center mx-[var(--space-2)]',
                  )
                }
              >
                <NavIcon icon={item.icon} />
                {(!collapsed || isMobile) && <span>{item.label}</span>}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      <div className={cn(
        'border-t border-[var(--color-border)] p-[var(--space-3)] flex items-center gap-[var(--space-3)]',
        collapsed && !isMobile && 'justify-center',
      )}>
        <div className="w-8 h-8 rounded-full bg-[var(--color-brand)] text-white flex items-center justify-center text-[var(--font-size-sm)] font-bold shrink-0">
          {user?.email?.[0]?.toUpperCase()}
        </div>
        {(!collapsed || isMobile) && (
          <div className="flex-1 min-w-0">
            <p className="text-[var(--font-size-sm)] font-medium text-[var(--color-text-primary)] truncate">
              {user?.email}
            </p>
            <p className="text-[var(--font-size-xs)] text-[var(--color-text-muted)] truncate">
              {user?.email}
            </p>
          </div>
        )}
      </div>
    </aside>
  );

  return (
    <>
      {isMobile && mobileOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30"
          onClick={() => setMobileOpen(false)}
        />
      )}
      {sidebarContent}
    </>
  );
}
