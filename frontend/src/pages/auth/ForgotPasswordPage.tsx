import { useNavigate, Link } from 'react-router-dom';
import { Button } from '../../shared/components/ui';

export default function ForgotPasswordPage() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col gap-[var(--space-6)] animate-fade-in">
      <div className="text-center">
        <h1 className="text-[var(--font-size-xl)] font-bold font-[var(--font-display)] text-[var(--color-text-primary)] mb-[var(--space-2)]">
          Recuperar senha
        </h1>
        <p className="text-[var(--font-size-sm)] text-[var(--color-text-secondary)]">
          O reset de senha é gerenciado pelo Keycloak
        </p>
      </div>

      <Button
        size="lg"
        fullWidth
        onClick={() => navigate('/oauth2/sign_in')}
      >
        Ir para o Keycloak
      </Button>

      <p className="text-center text-[var(--font-size-sm)]">
        <Link to="/auth/login">Voltar para login</Link>
      </p>
    </div>
  );
}
