import { Link } from 'react-router-dom';
import { Button } from '../shared/components/ui';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-[var(--color-bg-base)]">
      <header className="flex items-center justify-between px-[var(--space-6)] py-[var(--space-4)] max-w-6xl mx-auto">
        <span className="text-[var(--font-size-lg)] font-bold text-[var(--color-brand)]">SaaS Platform</span>
        <nav className="flex items-center gap-[var(--space-4)]">
          <Link to="/auth/login" className="text-[var(--font-size-sm)] font-medium text-[var(--color-text-secondary)] no-underline hover:text-[var(--color-text-primary)]">
            Entrar
          </Link>
          <Button onClick={() => window.location.href = '/oauth2/sign_in'}>
            Solicitar demo
          </Button>
        </nav>
      </header>

      <section className="max-w-6xl mx-auto px-[var(--space-6)] py-[var(--space-10)] md:py-[var(--space-20)]">
        <div className="text-center max-w-3xl mx-auto">
          <h1 className="text-[var(--font-size-2xl)] md:text-[48px] font-bold text-[var(--color-text-primary)] leading-tight mb-[var(--space-4)]">
            Comunicação em escala<br />
            <span className="text-[var(--color-brand)]">simples eeficiente</span>
          </h1>
          <p className="text-[var(--font-size-md)] text-[var(--color-text-secondary)] mb-[var(--space-8)] max-w-xl mx-auto">
            Envie campanhas em massa, automatize fluxos de comunicação e acompanhe resultados em tempo real — tudo de uma plataforma.
          </p>
          <div className="flex items-center justify-center gap-[var(--space-4)]">
            <Button size="lg" onClick={() => window.location.href = '/oauth2/sign_in'}>
              Começar agora
            </Button>
            <Button size="lg" variant="secondary">
              Ver demonstração
            </Button>
          </div>
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-[var(--space-6)] py-[var(--space-10)]">
        <div className="grid md:grid-cols-3 gap-[var(--space-6)]">
          {[
            { title: 'Campanhas em massa', desc: 'Dispare milhares de mensagens personalizadas com um clique.' },
            { title: 'Automações inteligentes', desc: 'Crie fluxos de boas-vindas, follow-up e reengajamento.' },
            { title: 'Relatórios em tempo real', desc: 'Acompanhe entregas, leituras e respostas ao vivo.' },
          ].map((feature) => (
            <div key={feature.title} className="rounded-[var(--radius-lg)] bg-[var(--color-bg-subtle)] p-[var(--space-6)]">
              <div className="w-10 h-10 rounded-[var(--radius-md)] bg-[var(--color-brand-light)] mb-[var(--space-4)]" />
              <h3 className="text-[var(--font-size-lg)] font-semibold text-[var(--color-text-primary)] mb-[var(--space-2)]">
                {feature.title}
              </h3>
              <p className="text-[var(--font-size-sm)] text-[var(--color-text-secondary)]">
                {feature.desc}
              </p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
