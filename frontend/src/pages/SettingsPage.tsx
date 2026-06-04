import { useChannels } from '../features/channels/hooks/useChannels';
import { Button, Spinner } from '../shared/components/ui';

export default function SettingsPage() {
  const { data: channels, isLoading } = useChannels();

  return (
    <div className="flex flex-col gap-[var(--space-6)] max-w-3xl">
      <div>
        <h2 className="text-[var(--font-size-xl)] font-bold text-[var(--color-text-primary)] mb-[var(--space-1)]">
          Configurações
        </h2>
        <p className="text-[var(--font-size-sm)] text-[var(--color-text-secondary)]">
          Gerencie seu workspace e conexões
        </p>
      </div>

      <div className="rounded-[var(--radius-md)] bg-[var(--color-bg-base)] border border-[var(--color-border)] p-[var(--space-4)]">
        <h3 className="text-[var(--font-size-base)] font-semibold text-[var(--color-text-primary)] mb-[var(--space-4)]">
          Workspace
        </h3>
        <div className="flex flex-col gap-[var(--space-3)]">
          <label className="text-[var(--font-size-sm)] font-medium text-[var(--color-text-secondary)]">
            Nome do workspace
          </label>
          <input
            type="text"
            defaultValue="Meu Workspace"
            className="rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-bg-base)] px-[var(--space-3)] py-[var(--space-2)] text-[var(--font-size-base)] max-w-sm"
          />
          <div>
            <Button variant="primary" size="sm">Salvar</Button>
          </div>
        </div>
      </div>

      <div className="rounded-[var(--radius-md)] bg-[var(--color-bg-base)] border border-[var(--color-border)] p-[var(--space-4)]">
        <div className="flex items-center justify-between mb-[var(--space-4)]">
          <h3 className="text-[var(--font-size-base)] font-semibold text-[var(--color-text-primary)]">
            Canais de comunicação
          </h3>
          <Button size="sm">Conectar novo canal</Button>
        </div>

        {isLoading ? (
          <Spinner size="sm" />
        ) : (
          <div className="flex flex-col gap-[var(--space-3)]">
            {channels?.length === 0 && (
              <p className="text-[var(--font-size-sm)] text-[var(--color-text-muted)] py-[var(--space-4)] text-center">
                Nenhum canal conectado. Clique em "Conectar novo canal" para começar.
              </p>
            )}
            {channels?.map((ch) => (
              <div key={ch.id} className="flex items-center justify-between py-[var(--space-3)] border-b border-[var(--color-border)] last:border-0">
                <div className="flex items-center gap-[var(--space-3)]">
                  <div className={`w-3 h-3 rounded-full ${
                    ch.status === 'connected' ? 'bg-[var(--color-success)]' : 'bg-[var(--color-danger)]'
                  }`} />
                  <div>
                    <p className="text-[var(--font-size-sm)] font-medium text-[var(--color-text-primary)]">{ch.name}</p>
                    <p className="text-[var(--font-size-xs)] text-[var(--color-text-muted)]">{ch.phone_number}</p>
                  </div>
                </div>
                <div className="flex items-center gap-[var(--space-2)]">
                  <span className="text-[var(--font-size-xs)] text-[var(--color-text-secondary)] capitalize">{ch.type}</span>
                  {ch.status === 'disconnected' && (
                    <Button size="sm" variant="secondary">Reconectar</Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="rounded-[var(--radius-md)] bg-[var(--color-bg-base)] border border-[var(--color-border)] p-[var(--space-4)]">
        <h3 className="text-[var(--font-size-base)] font-semibold text-[var(--color-text-primary)] mb-[var(--space-3)]">
          Em breve
        </h3>
        <div className="flex flex-col gap-[var(--space-3)]">
          {['Instagram', 'Messenger', 'Telegram'].map((name) => (
            <div key={name} className="flex items-center gap-[var(--space-3)] py-[var(--space-2)] opacity-50">
              <div className="w-8 h-8 rounded-[var(--radius-sm)] bg-[var(--color-bg-muted)]" />
              <div>
                <p className="text-[var(--font-size-sm)] font-medium text-[var(--color-text-primary)]">{name}</p>
                <p className="text-[var(--font-size-xs)] text-[var(--color-text-muted)]">Em desenvolvimento</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
