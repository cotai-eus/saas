import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../api/client';
import { ENDPOINTS } from '../../api/endpoints';
import { useAuthStore } from '../../store/authStore';
import { useEffect, type ReactNode } from 'react';
import { FullPageSpinner } from './Spinner';
import type { User } from '../../api/types';

export function AuthGuard({ children }: { children: ReactNode }) {
  const setUser = useAuthStore((s) => s.setUser);

  const { data, isLoading, isError } = useQuery({
    queryKey: ['me'],
    queryFn: () => apiClient.get<User>(ENDPOINTS.me),
    retry: false,
    staleTime: 60_000,
  });

  useEffect(() => {
    if (data) setUser(data);
  }, [data, setUser]);

  if (isLoading) return <FullPageSpinner />;

  if (isError || !data?.user_id) {
    window.location.href = '/oauth2/sign_in';
    return null;
  }

  return <>{children}</>;
}
