import type { ReactNode } from 'react';
import { cn } from '../../utils/cn';
import { Spinner } from './Spinner';

interface StatCardProps {
  label: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon?: ReactNode;
  loading?: boolean;
  className?: string;
}

export function StatCard({ label, value, change, changeLabel, icon, loading, className }: StatCardProps) {
  return (
    <div
      className={cn(
        'rounded-[var(--radius-md)] bg-[var(--color-bg-subtle)] p-[var(--space-4)] flex flex-col gap-[var(--space-2)]',
        className,
      )}
    >
      <div className="flex items-center justify-between">
        <span className="text-[var(--font-size-sm)] text-[var(--color-text-secondary)] font-medium">
          {label}
        </span>
        {icon && <span className="text-[var(--color-text-muted)]">{icon}</span>}
      </div>
      {loading ? (
        <Spinner size="sm" />
      ) : (
        <>
          <span className="text-[var(--font-size-xl)] font-semibold text-[var(--color-text-primary)]">
            {value}
          </span>
          {change !== undefined && (
            <div className="flex items-center gap-[var(--space-1)]">
              <span
                className={cn(
                  'text-[var(--font-size-xs)] font-medium',
                  change >= 0 ? 'text-[var(--color-success)]' : 'text-[var(--color-danger)]',
                )}
              >
                {change >= 0 ? '↑' : '↓'} {Math.abs(change)}%
              </span>
              {changeLabel && (
                <span className="text-[var(--font-size-xs)] text-[var(--color-text-muted)]">
                  {changeLabel}
                </span>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
