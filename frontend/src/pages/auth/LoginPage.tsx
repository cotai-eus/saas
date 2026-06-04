import { Button } from '../../shared/components/ui';

export default function LoginPage() {
  return (
    <div className="flex flex-col gap-[var(--space-6)]">
      <div className="text-center">
        <h1 className="text-[var(--font-size-xl)] font-bold text-[var(--color-text-primary)] mb-[var(--space-2)]">
          Entrar na plataforma
        </h1>
        <p className="text-[var(--font-size-sm)] text-[var(--color-text-secondary)]">
          Acesse sua conta para gerenciar campanhas
        </p>
      </div>

      <Button
        size="lg"
        fullWidth
        onClick={() => window.location.href = '/oauth2/sign_in'}
      >
        Entrar com SSO
      </Button>

      <p className="text-center text-[var(--font-size-sm)] text-[var(--color-text-secondary)]">
        Primeira vez?{' '}
        <a href="/auth/register">Solicitar acesso</a>
      </p>

      <p className="text-center text-[var(--font-size-xs)] text-[var(--color-text-muted)]">
        <a href="/auth/forgot-password">Esqueceu a senha?</a>
      </p>
    </div>
  );
}
