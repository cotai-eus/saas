import { useNavigate, Link } from 'react-router-dom';
import { Button } from '../../shared/components/ui';

export default function RegisterPage() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col gap-[var(--space-6)] animate-fade-in">
      <div className="text-center">
        <h1 className="text-[var(--font-size-xl)] font-bold font-[var(--font-display)] text-[var(--color-text-primary)] mb-[var(--space-2)]">
          Solicitar acesso
        </h1>
        <p className="text-[var(--font-size-sm)] text-[var(--color-text-secondary)]">
          Preencha o formulário para solicitar acesso à plataforma
        </p>
      </div>

      <Button
        size="lg"
        fullWidth
        onClick={() => navigate('/oauth2/sign_in')}
      >
        Solicitar via SSO
      </Button>

      <p className="text-center text-[var(--font-size-sm)] text-[var(--color-text-secondary)]">
        Já tem conta?{' '}
        <Link to="/auth/login">Entrar</Link>
      </p>
    </div>
  );
}
