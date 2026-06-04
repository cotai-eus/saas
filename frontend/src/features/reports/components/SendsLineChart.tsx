import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface SendsLineChartProps {
  data?: { date: string; sent: number; delivered: number; replied: number }[];
}

const mockData = [
  { date: '01/06', sent: 120, delivered: 110, replied: 45 },
  { date: '02/06', sent: 200, delivered: 185, replied: 72 },
  { date: '03/06', sent: 150, delivered: 140, replied: 60 },
  { date: '04/06', sent: 80, delivered: 75, replied: 30 },
  { date: '05/06', sent: 250, delivered: 230, replied: 95 },
  { date: '06/06', sent: 180, delivered: 170, replied: 68 },
  { date: '07/06', sent: 300, delivered: 280, replied: 110 },
];

const CHART_COLORS = {
  brand: '#00C853',
  info: '#2962FF',
  warning: '#FF6D00',
  border: '#E1E4E8',
  textMuted: '#8B98A5',
  bgBase: '#FAFAFA',
};

const DARK_CHART_COLORS = {
  brand: '#00E676',
  info: '#448AFF',
  warning: '#FF9100',
  border: '#30363D',
  textMuted: '#6B7280',
  bgBase: '#0A0E17',
};

function getColors() {
  if (typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return DARK_CHART_COLORS;
  }
  return CHART_COLORS;
}

export function SendsLineChart({ data }: SendsLineChartProps) {
  const chartData = data || mockData;
  const colors = getColors();

  return (
    <div className="rounded-[var(--radius-md)] bg-[var(--color-bg-base)] border border-[var(--color-border)] p-[var(--space-4)]">
      <h3 className="text-[var(--font-size-base)] font-semibold text-[var(--color-text-primary)] mb-[var(--space-4)]">
        Envios por dia
      </h3>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke={colors.border} />
          <XAxis dataKey="date" tick={{ fontSize: 12, fill: colors.textMuted }} />
          <YAxis tick={{ fontSize: 12, fill: colors.textMuted }} />
          <Tooltip
            contentStyle={{
              background: colors.bgBase,
              border: `1px solid ${colors.border}`,
              borderRadius: '8px',
              fontSize: '13px',
            }}
          />
          <Legend />
          <Line type="monotone" dataKey="sent" stroke={colors.brand} strokeWidth={2} name="Enviadas" dot={false} />
          <Line type="monotone" dataKey="delivered" stroke={colors.info} strokeWidth={2} name="Entregues" dot={false} />
          <Line type="monotone" dataKey="replied" stroke={colors.warning} strokeWidth={2} name="Respondidas" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
