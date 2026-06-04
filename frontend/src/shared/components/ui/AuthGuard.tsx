import { useAuth } from '../../hooks/useAuth';
import { type ReactNode } from 'react';
import { FullPageSpinner } from './Spinner';

export function AuthGuard({ children }: { children: ReactNode }) {
  const { isLoading, isAuthenticated } = useAuth();

  if (isLoading) return <FullPageSpinner />;

  if (!isAuthenticated) {
    window.location.href = '/oauth2/sign_in';
    return null;
  }

  return <>{children}</>;
}
