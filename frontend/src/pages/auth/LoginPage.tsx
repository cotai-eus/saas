import { useNavigate, Link } from 'react-router-dom';
import { Button } from '../../shared/components/ui';

export default function LoginPage() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col gap-[var(--space-6)] animate-fade-in">
      <div className="text-center">
        <div className="w-12 h-12 mx-auto mb-[var(--space-4)] rounded-[var(--radius-lg)] bg-[var(--color-brand-light)] flex items-center justify-center">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--color-brand-dark)" strokeWidth="1.5" strokeLinecap="round">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
          </svg>
        </div>
        <h1 className="text-[var(--font-size-xl)] font-bold font-[var(--font-display)] text-[var(--color-text-primary)] mb-[var(--space-2)]">
          Entrar na plataforma
        </h1>
        <p className="text-[var(--font-size-sm)] text-[var(--color-text-secondary)]">
          Acesse sua conta para gerenciar campanhas
        </p>
      </div>

      <Button
        size="lg"
        fullWidth
        onClick={() => navigate('/oauth2/sign_in')}
      >
        Entrar com SSO
      </Button>

      <p className="text-center text-[var(--font-size-sm)] text-[var(--color-text-secondary)]">
        Primeira vez?{' '}
        <Link to="/auth/register">Solicitar acesso</Link>
      </p>

      <p className="text-center text-[var(--font-size-xs)] text-[var(--color-text-muted)]">
        <Link to="/auth/forgot-password">Esqueceu a senha?</Link>
      </p>
    </div>
  );
}
