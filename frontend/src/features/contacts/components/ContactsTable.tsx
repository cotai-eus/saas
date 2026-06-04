import { Link } from 'react-router-dom';
import { formatDate } from '../../../shared/utils/date';
import type { Contact } from '../../../shared/api/types';

interface ContactsTableProps {
  contacts: Contact[];
}

function ContactAvatar({ name }: { name: string }) {
  const initials = name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
  return (
    <div className="w-8 h-8 rounded-full bg-[var(--color-brand)] text-white flex items-center justify-center text-[var(--font-size-sm)] font-bold shrink-0">
      {initials}
    </div>
  );
}

const statusColors: Record<string, string> = {
  active: 'bg-[var(--color-success)]',
  unsubscribed: 'bg-[var(--color-warning)]',
  bounce: 'bg-[var(--color-danger)]',
};

export function ContactsTable({ contacts }: ContactsTableProps) {
  if (contacts.length === 0) {
    return (
      <div className="text-center py-[var(--space-10)] text-[var(--color-text-muted)]">
        Nenhum contato encontrado
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b border-[var(--color-border)]">
            <th scope="col" className="text-left py-[var(--space-3)] px-[var(--space-3)] text-[var(--font-size-xs)] font-semibold uppercase tracking-wider text-[var(--color-text-muted)]">Contato</th>
            <th scope="col" className="text-left py-[var(--space-3)] px-[var(--space-3)] text-[var(--font-size-xs)] font-semibold uppercase tracking-wider text-[var(--color-text-muted)]">Telefone</th>
            <th scope="col" className="text-left py-[var(--space-3)] px-[var(--space-3)] text-[var(--font-size-xs)] font-semibold uppercase tracking-wider text-[var(--color-text-muted)]">Status</th>
            <th scope="col" className="text-right py-[var(--space-3)] px-[var(--space-3)] text-[var(--font-size-xs)] font-semibold uppercase tracking-wider text-[var(--color-text-muted)]">Última interação</th>
          </tr>
        </thead>
        <tbody>
          {contacts.map((contact) => (
            <tr key={contact.id} className="border-b border-[var(--color-border)] hover:bg-[var(--color-bg-subtle)] transition-colors">
              <td className="py-[var(--space-3)] px-[var(--space-3)]">
                <Link
                  to={`/contacts/${contact.id}`}
                  className="flex items-center gap-[var(--space-3)] no-underline"
                >
                  <ContactAvatar name={contact.name} />
                  <div>
                    <p className="text-[var(--font-size-base)] font-medium text-[var(--color-text-primary)]">
                      {contact.name}
                    </p>
                    {contact.email && (
                      <p className="text-[var(--font-size-xs)] text-[var(--color-text-muted)]">
                        {contact.email}
                      </p>
                    )}
                  </div>
                </Link>
              </td>
              <td className="py-[var(--space-3)] px-[var(--space-3)] text-[var(--font-size-base)] text-[var(--color-text-secondary)]">
                {contact.phone}
              </td>
              <td className="py-[var(--space-3)] px-[var(--space-3)]">
                <div className="flex items-center gap-[var(--space-1)]">
                  <span className={`w-2 h-2 rounded-full ${statusColors[contact.status] || 'bg-[var(--color-text-muted)]'}`} />
                  <span className="text-[var(--font-size-sm)] text-[var(--color-text-secondary)] capitalize">
                    {contact.status === 'active' ? 'Ativo' : contact.status === 'unsubscribed' ? 'Descadastrado' : 'Bounce'}
                  </span>
                </div>
              </td>
              <td className="py-[var(--space-3)] px-[var(--space-3)] text-right text-[var(--font-size-sm)] text-[var(--color-text-secondary)]">
                {formatDate(contact.last_interaction_at)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
