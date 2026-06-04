export function formatNumber(n: number | undefined | null): string {
  if (n === undefined || n === null) return '—';
  return n.toLocaleString('pt-BR');
}

export function formatPercent(n: number | undefined | null): string {
  if (n === undefined || n === null) return '—';
  return `${n.toFixed(1)}%`;
}

export function formatCompact(n: number | undefined | null): string {
  if (n === undefined || n === null) return '—';
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}
