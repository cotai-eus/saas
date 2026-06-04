import type { ReactNode } from 'react';
import { Button } from './Button';

interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description: string;
  action?: { label: string; onClick: () => void };
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-[var(--space-10)] px-[var(--space-4)] text-center">
      {icon && <div className="mb-[var(--space-4)] text-[var(--color-text-muted)]">{icon}</div>}
      <h3 className="text-[var(--font-size-lg)] font-semibold text-[var(--color-text-primary)] mb-[var(--space-2)]">
        {title}
      </h3>
      <p className="text-[var(--font-size-base)] text-[var(--color-text-secondary)] max-w-sm mb-[var(--space-6)]">
        {description}
      </p>
      {action && (
        <Button onClick={action.onClick} variant="primary">
          {action.label}
        </Button>
      )}
    </div>
  );
}
