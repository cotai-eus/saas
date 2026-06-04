import { useNavigate } from 'react-router-dom';
import { Button } from '../shared/components/ui';

const features = [
  {
    title: 'Campanhas em massa',
    desc: 'Dispare milhares de mensagens personalizadas com um clique para WhatsApp, Telegram e mais.',
    icon: 'M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z',
  },
  {
    title: 'Automações inteligentes',
    desc: 'Crie fluxos de boas-vindas, follow-up e reengajamento que disparam automaticamente.',
    icon: 'M4 4v16h16M4 12h16M12 4v16',
  },
  {
    title: 'Relatórios em tempo real',
    desc: 'Acompanhe entregas, leituras e respostas ao vivo com gráficos atualizados em tempo real.',
    icon: 'M3 20h18M3 16l4-8 4 4 4-8 4 4',
  },
  {
    title: 'Multicanal unificado',
    desc: 'Gerencie WhatsApp, Instagram, Messenger e Telegram em um só lugar.',
    icon: 'M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9',
  },
];

const stats = [
  { label: 'Mensagens enviadas', value: '+10M' },
  { label: 'Clientes ativos', value: '500+' },
  { label: 'Taxa de entrega', value: '98%' },
  { label: 'Canais integrados', value: '4' },
];

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[var(--color-bg-base)]">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 rounded-full bg-[var(--color-brand)]/5 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 rounded-full bg-[var(--color-accent)]/5 blur-3xl" />
      </div>

      <header className="relative z-10 flex items-center justify-between px-[var(--space-6)] py-[var(--space-4)] max-w-6xl mx-auto animate-fade-in">
        <span className="text-[var(--font-size-lg)] font-bold font-[var(--font-display)] text-[var(--color-brand)] tracking-tight">
          ChannelFlow
        </span>
        <nav className="flex items-center gap-[var(--space-4)]">
          <button
            onClick={() => navigate('/auth/login')}
            className="text-[var(--font-size-sm)] font-medium text-[var(--color-text-secondary)] bg-transparent border-none hover:text-[var(--color-text-primary)] transition-colors"
          >
            Entrar
          </button>
          <Button onClick={() => navigate('/oauth2/sign_in')}>
            Solicitar demo
          </Button>
        </nav>
      </header>

      <section className="relative z-10 max-w-6xl mx-auto px-[var(--space-6)] py-[var(--space-10)] md:py-[var(--space-20)] animate-slide-up">
        <div className="text-center max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-[var(--space-2)] px-[var(--space-3)] py-[var(--space-1)] rounded-full bg-[var(--color-brand-light)] text-[var(--color-brand-dark)] text-[var(--font-size-xs)] font-semibold mb-[var(--space-6)] animate-fade-in">
            <span className="w-2 h-2 rounded-full bg-[var(--color-brand)] animate-pulse" />
            Plataforma multicanal
          </div>
          <h1 className="text-[var(--font-size-2xl)] md:text-[52px] font-bold font-[var(--font-display)] text-[var(--color-text-primary)] leading-[1.1] tracking-tight mb-[var(--space-4)]">
            Comunicação em escala que
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[var(--color-brand)] to-[var(--color-accent)]">
              realmente funciona
            </span>
          </h1>
          <p className="text-[var(--font-size-md)] text-[var(--color-text-secondary)] mb-[var(--space-8)] max-w-xl mx-auto leading-relaxed">
            Envie campanhas em massa, automatize fluxos de comunicação e acompanhe resultados em tempo real — tudo de uma plataforma, com os canais que seus clientes usam.
          </p>
          <div className="flex items-center justify-center gap-[var(--space-4)]">
            <Button size="lg" onClick={() => navigate('/oauth2/sign_in')}>
              Começar agora
            </Button>
            <Button size="lg" variant="secondary" onClick={() => navigate('/auth/login')}>
              Ver demonstração
            </Button>
          </div>
        </div>
      </section>

      <section className="relative z-10 max-w-5xl mx-auto px-[var(--space-6)] mb-[var(--space-10)]">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-[var(--space-4)]">
          {stats.map((stat, i) => (
            <div
              key={stat.label}
              className="text-center p-[var(--space-4)] rounded-[var(--radius-lg)] bg-[var(--color-bg-subtle)] border border-[var(--color-border)] animate-slide-up"
              style={{ animationDelay: `${0.1 + i * 0.05}s` }}
            >
              <p className="text-[var(--font-size-2xl)] font-bold font-[var(--font-display)] text-[var(--color-text-primary)]">
                {stat.value}
              </p>
              <p className="text-[var(--font-size-sm)] text-[var(--color-text-secondary)] mt-[var(--space-1)]">
                {stat.label}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section className="relative z-10 max-w-6xl mx-auto px-[var(--space-6)] pb-[var(--space-10)]">
        <div className="text-center mb-[var(--space-8)]">
          <h2 className="text-[var(--font-size-xl)] font-bold font-[var(--font-display)] text-[var(--color-text-primary)]">
            Tudo que você precisa
          </h2>
          <p className="text-[var(--font-size-sm)] text-[var(--color-text-secondary)] mt-[var(--space-2)]">
            Uma plataforma completa para comunicação empresarial
          </p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-[var(--space-4)]">
          {features.map((feature, i) => (
            <div
              key={feature.title}
              className="group rounded-[var(--radius-lg)] bg-[var(--color-bg-base)] border border-[var(--color-border)] p-[var(--space-5)] hover:border-[var(--color-brand)]/30 hover:shadow-[var(--shadow-md)] transition-all duration-200 animate-fade-in"
              style={{ animationDelay: `${0.2 + i * 0.05}s` }}
            >
              <div className="w-10 h-10 rounded-[var(--radius-md)] bg-[var(--color-brand-light)] flex items-center justify-center mb-[var(--space-4)] group-hover:scale-110 transition-transform duration-200">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-brand-dark)" strokeWidth="1.5" strokeLinecap="round">
                  <path d={feature.icon} />
                </svg>
              </div>
              <h3 className="text-[var(--font-size-base)] font-semibold text-[var(--color-text-primary)] mb-[var(--space-2)]">
                {feature.title}
              </h3>
              <p className="text-[var(--font-size-sm)] text-[var(--color-text-secondary)] leading-relaxed">
                {feature.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      <footer className="relative z-10 border-t border-[var(--color-border)] py-[var(--space-6)]">
        <div className="max-w-6xl mx-auto px-[var(--space-6)] flex items-center justify-between">
          <span className="text-[var(--font-size-sm)] font-bold font-[var(--font-display)] text-[var(--color-brand)] tracking-tight">
            ChannelFlow
          </span>
          <p className="text-[var(--font-size-xs)] text-[var(--color-text-muted)]">
            &copy; {new Date().getFullYear()} ChannelFlow. Todos os direitos reservados.
          </p>
        </div>
      </footer>
    </div>
  );
}
