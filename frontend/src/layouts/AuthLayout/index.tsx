import { Outlet, Link } from 'react-router-dom';

export default function AuthLayout() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-[var(--color-bg-subtle)] px-[var(--space-4)]">
      <div className="w-full max-w-sm">
        <Link
          to="/"
          className="block text-center mb-[var(--space-8)] text-[var(--font-size-xl)] font-bold text-[var(--color-brand)] no-underline hover:no-underline"
        >
          SaaS Platform
        </Link>
        <div className="rounded-[var(--radius-lg)] bg-[var(--color-bg-base)] p-[var(--space-8)] shadow-[var(--shadow-md)]">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
