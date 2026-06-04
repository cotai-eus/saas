import { useParams, useNavigate } from 'react-router-dom';
import { useContact } from '../features/contacts/hooks/useContacts';
import { Button, Spinner } from '../shared/components/ui';
import { formatDateTime } from '../shared/utils/date';

export default function ContactDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: contact, isLoading } = useContact(id!);

  if (isLoading) return <Spinner size="lg" />;

  if (!contact) {
    return (
      <div className="flex flex-col items-center justify-center py-[var(--space-10)] gap-[var(--space-4)]">
        <p className="text-[var(--color-text-muted)]">Contato não encontrado</p>
        <Button onClick={() => navigate('/contacts')}>Voltar</Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-[var(--space-6)]">
      <button
        onClick={() => navigate('/contacts')}
        className="text-[var(--font-size-sm)] text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)] bg-transparent border-none mb-[var(--space-1)]"
      >
        ← Voltar
      </button>

      <div className="flex items-center gap-[var(--space-4)]">
        <div className="w-12 h-12 rounded-full bg-[var(--color-brand)] text-white flex items-center justify-center text-[var(--font-size-lg)] font-bold">
          {contact.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
        </div>
        <div>
          <h1 className="text-[var(--font-size-xl)] font-bold text-[var(--color-text-primary)]">{contact.name}</h1>
          <p className="text-[var(--font-size-sm)] text-[var(--color-text-secondary)]">{contact.email || 'Sem email'}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-[var(--space-4)]">
        <div className="rounded-[var(--radius-md)] bg-[var(--color-bg-base)] border border-[var(--color-border)] p-[var(--space-4)]">
          <h3 className="text-[var(--font-size-base)] font-semibold mb-[var(--space-3)]">Informações</h3>
          <dl className="flex flex-col gap-[var(--space-2)]">
            <div className="flex justify-between">
              <dt className="text-[var(--font-size-sm)] text-[var(--color-text-muted)]">Telefone</dt>
              <dd className="text-[var(--font-size-sm)] text-[var(--color-text-primary)]">{contact.phone}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-[var(--font-size-sm)] text-[var(--color-text-muted)]">Status</dt>
              <dd className="text-[var(--font-size-sm)] text-[var(--color-text-primary)] capitalize">{contact.status}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-[var(--font-size-sm)] text-[var(--color-text-muted)]">Criado em</dt>
              <dd className="text-[var(--font-size-sm)] text-[var(--color-text-primary)]">{formatDateTime(contact.created_at)}</dd>
            </div>
            {contact.last_interaction_at && (
              <div className="flex justify-between">
                <dt className="text-[var(--font-size-sm)] text-[var(--color-text-muted)]">Última interação</dt>
                <dd className="text-[var(--font-size-sm)] text-[var(--color-text-primary)]">{formatDateTime(contact.last_interaction_at)}</dd>
              </div>
            )}
          </dl>
        </div>
      </div>
    </div>
  );
}
