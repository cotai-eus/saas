import { useState } from 'react';
import { useContacts } from '../features/contacts/hooks/useContacts';
import { ContactsTable } from '../features/contacts/components/ContactsTable';
import { Button, EmptyState } from '../shared/components/ui';
import { useDebounce } from '../shared/hooks';

export default function ContactsPage() {
  const { data: contacts, isLoading } = useContacts();
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebounce(search, 300);

  const filtered = (contacts || []).filter((c) =>
    c.name.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
    c.phone.includes(debouncedSearch) ||
    c.email?.toLowerCase().includes(debouncedSearch.toLowerCase())
  );

  return (
    <div className="flex flex-col gap-[var(--space-4)]">
      <div className="flex items-center justify-between">
        <div className="relative flex-1 max-w-sm">
          <input
            type="text"
            placeholder="Buscar contatos..."
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
        <Button>Importar CSV</Button>
      </div>

      {!isLoading && contacts?.length === 0 ? (
        <EmptyState
          title="Base de contatos vazia"
          description="Importe um CSV ou adicione contatos manualmente."
          action={{ label: 'Importar CSV', onClick: () => {} }}
        />
      ) : (
        <div className="rounded-[var(--radius-md)] bg-[var(--color-bg-base)] border border-[var(--color-border)]">
          <ContactsTable contacts={filtered} />
        </div>
      )}
    </div>
  );
}
