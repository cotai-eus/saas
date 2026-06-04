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

export function SendsLineChart({ data }: SendsLineChartProps) {
  const chartData = data || mockData;

  return (
    <div className="rounded-[var(--radius-md)] bg-[var(--color-bg-base)] border border-[var(--color-border)] p-[var(--space-4)]">
      <h3 className="text-[var(--font-size-base)] font-semibold text-[var(--color-text-primary)] mb-[var(--space-4)]">
        Envios por dia
      </h3>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
          <XAxis dataKey="date" tick={{ fontSize: 12, fill: 'var(--color-text-muted)' }} />
          <YAxis tick={{ fontSize: 12, fill: 'var(--color-text-muted)' }} />
          <Tooltip
            contentStyle={{
              background: 'var(--color-bg-base)',
              border: '1px solid var(--color-border)',
              borderRadius: '8px',
              fontSize: '13px',
            }}
          />
          <Legend />
          <Line type="monotone" dataKey="sent" stroke="var(--color-brand)" strokeWidth={2} name="Enviadas" dot={false} />
          <Line type="monotone" dataKey="delivered" stroke="var(--color-info)" strokeWidth={2} name="Entregues" dot={false} />
          <Line type="monotone" dataKey="replied" stroke="var(--color-warning)" strokeWidth={2} name="Respondidas" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
