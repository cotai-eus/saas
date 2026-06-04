import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { useUIStore } from '../../shared/store';
import { useMediaQuery } from '../../shared/hooks';

export default function AppLayout() {
  const sidebarCollapsed = useUIStore((s) => s.sidebarCollapsed);
  const isMobile = useMediaQuery('(max-width: 767px)');

  return (
    <div className="flex h-screen overflow-hidden bg-[var(--color-bg-subtle)]">
      <Sidebar />
      <div
        className="flex flex-col flex-1 min-w-0 transition-all duration-200"
        style={{
          marginLeft: isMobile ? 0 : (sidebarCollapsed ? 'var(--sidebar-collapsed-width)' : 'var(--sidebar-width)'),
        }}
      >
        <TopBar />
        <main className="flex-1 overflow-y-auto p-[var(--space-6)]">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
