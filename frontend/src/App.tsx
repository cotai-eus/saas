import { Component, type ReactNode, type ErrorInfo } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('ErrorBoundary caught:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-[var(--color-bg-base)] px-[var(--space-4)]">
          <div className="text-center max-w-md">
            <div className="w-16 h-16 mx-auto mb-[var(--space-4)] rounded-[var(--radius-lg)] bg-[var(--color-danger-bg)] flex items-center justify-center">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--color-danger)" strokeWidth="2" strokeLinecap="round">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
            </div>
            <h1 className="text-[var(--font-size-xl)] font-bold text-[var(--color-text-primary)] mb-[var(--space-2)]">
              Algo deu errado
            </h1>
            <p className="text-[var(--font-size-sm)] text-[var(--color-text-secondary)] mb-[var(--space-6)]">
              Ocorreu um erro inesperado. Tente recarregar a página.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="inline-flex items-center justify-center px-[var(--space-4)] py-[var(--space-2)] rounded-[var(--radius-md)] bg-[var(--color-brand)] text-white font-medium text-[var(--font-size-base)] border-none hover:bg-[var(--color-brand-dark)] transition-colors"
            >
              Recarregar página
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
