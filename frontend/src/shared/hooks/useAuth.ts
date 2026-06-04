import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { ENDPOINTS } from '../api/endpoints';
import { useAuthStore } from '../store/authStore';
import { useEffect } from 'react';
import type { User } from '../api/types';

export function useAuth() {
  const { user, isAuthenticated, setUser, clear } = useAuthStore();

  const { data, isLoading, isError } = useQuery({
    queryKey: ['me'],
    queryFn: () => apiClient.get<User>(ENDPOINTS.me),
    retry: false,
    staleTime: 60_000,
  });

  useEffect(() => {
    if (data) setUser(data);
    if (isError) clear();
  }, [data, isError, setUser, clear]);

  return { user, isAuthenticated, isLoading };
}
