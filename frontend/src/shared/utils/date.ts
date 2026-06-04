import { format, formatDistanceToNow, parseISO } from 'date-fns';
import { ptBR } from 'date-fns/locale';

export function formatDate(iso: string | undefined | null, fmt = 'dd/MM/yyyy'): string {
  if (!iso) return '—';
  return format(parseISO(iso), fmt, { locale: ptBR });
}

export function formatDateTime(iso: string | undefined | null): string {
  if (!iso) return '—';
  return format(parseISO(iso), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR });
}

export function formatRelative(iso: string | undefined | null): string {
  if (!iso) return '—';
  return formatDistanceToNow(parseISO(iso), { addSuffix: true, locale: ptBR });
}
