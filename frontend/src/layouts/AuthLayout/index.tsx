import { Outlet, Link } from 'react-router-dom';

export default function AuthLayout() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-[var(--color-bg-subtle)] px-[var(--space-4)]">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -left-40 w-80 h-80 rounded-full bg-[var(--color-brand)]/5 blur-3xl" />
        <div className="absolute -bottom-40 -right-40 w-96 h-96 rounded-full bg-[var(--color-accent)]/5 blur-3xl" />
      </div>
      <div className="w-full max-w-sm relative z-10 animate-scale-in">
        <Link
          to="/"
          className="flex items-center justify-center gap-[var(--space-2)] mb-[var(--space-8)] no-underline hover:no-underline"
        >
          <div className="w-8 h-8 rounded-[var(--radius-md)] bg-[var(--color-brand)] flex items-center justify-center">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
            </svg>
          </div>
          <span className="text-[var(--font-size-xl)] font-bold font-[var(--font-display)] text-[var(--color-brand)] tracking-tight">
            ChannelFlow
          </span>
        </Link>
        <div className="rounded-[var(--radius-lg)] bg-[var(--color-bg-base)] p-[var(--space-8)] shadow-[var(--shadow-md)] border border-[var(--color-border)]">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
