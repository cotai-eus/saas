import { Button } from '../../shared/components/ui';
import { Link } from 'react-router-dom';

export default function RegisterPage() {
  return (
    <div className="flex flex-col gap-[var(--space-6)]">
      <div className="text-center">
        <h1 className="text-[var(--font-size-xl)] font-bold text-[var(--color-text-primary)] mb-[var(--space-2)]">
          Solicitar acesso
        </h1>
        <p className="text-[var(--font-size-sm)] text-[var(--color-text-secondary)]">
          Entre em contato com o administrador para criar sua conta
        </p>
      </div>

      <Button
        size="lg"
        fullWidth
        onClick={() => window.location.href = '/oauth2/sign_in'}
      >
        Solicitar via SSO
      </Button>

      <p className="text-center text-[var(--font-size-sm)] text-[var(--color-text-secondary)]">
        Já tem conta? <Link to="/auth/login">Entrar</Link>
      </p>
    </div>
  );
}
