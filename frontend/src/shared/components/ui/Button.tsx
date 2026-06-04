import { cn } from '../../utils/cn';
import type { ButtonHTMLAttributes, ReactNode } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  fullWidth?: boolean;
  children: ReactNode;
}

export function Button({
  variant = 'primary',
  size = 'md',
  loading,
  fullWidth,
  children,
  className,
  disabled,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-[var(--radius-md)] font-medium transition-all duration-150 border-none',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        variant === 'primary' && 'bg-[var(--color-brand)] text-white hover:bg-[var(--color-brand-dark)] active:scale-[0.98]',
        variant === 'secondary' && 'bg-[var(--color-bg-subtle)] text-[var(--color-text-primary)] hover:bg-[var(--color-bg-muted)] border border-[var(--color-border)]',
        variant === 'danger' && 'bg-[var(--color-danger)] text-white hover:opacity-90',
        variant === 'ghost' && 'bg-transparent text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-subtle)]',
        size === 'sm' && 'px-[var(--space-3)] py-[var(--space-1)] text-[var(--font-size-sm)]',
        size === 'md' && 'px-[var(--space-4)] py-[var(--space-2)] text-[var(--font-size-base)]',
        size === 'lg' && 'px-[var(--space-6)] py-[var(--space-3)] text-[var(--font-size-md)]',
        fullWidth && 'w-full',
        className,
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <SpinnerIcon />}
      {children}
    </button>
  );
}

function SpinnerIcon() {
  return (
    <svg
      className="animate-spin"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
    >
      <path d="M21 12a9 9 0 11-6.219-8.56" strokeLinecap="round" />
    </svg>
  );
}
