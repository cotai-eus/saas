import { useState } from 'react';
import { useContacts } from '../features/contacts/hooks/useContacts';
import { ContactsTable } from '../features/contacts/components/ContactsTable';
import { Button, EmptyState, SearchIcon } from '../shared/components/ui';
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
    <div className="flex flex-col gap-[var(--space-4)] animate-fade-in">
      <div className="flex items-center justify-between">
        <div className="relative flex-1 max-w-sm">
          <input
            type="text"
            placeholder="Buscar contatos..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-bg-base)] px-[var(--space-3)] py-[var(--space-2)] pl-[var(--space-8)] text-[var(--font-size-base)] placeholder:text-[var(--color-text-muted)] focus:border-[var(--color-brand)] focus:outline-none focus:ring-2 focus:ring-[var(--color-brand)]/20 transition-colors"
          />
          <SearchIcon className="absolute left-[var(--space-2)] top-1/2 -translate-y-1/2 text-[var(--color-text-muted)] pointer-events-none" />
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
