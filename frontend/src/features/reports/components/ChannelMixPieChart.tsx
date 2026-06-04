import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

interface ChannelMixPieChartProps {
  data?: { name: string; value: number }[];
}

const mockData = [
  { name: 'WhatsApp', value: 65 },
  { name: 'Telegram', value: 20 },
  { name: 'Messenger', value: 10 },
  { name: 'Instagram', value: 5 },
];

const CHART_COLORS = ['#00C853', '#2962FF', '#FF6D00', '#D50000'];
const DARK_CHART_COLORS = ['#00E676', '#448AFF', '#FF9100', '#FF5252'];

function getColors() {
  if (typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return DARK_CHART_COLORS;
  }
  return CHART_COLORS;
}

export function ChannelMixPieChart({ data }: ChannelMixPieChartProps) {
  const chartData = data || mockData;
  const colors = getColors();

  return (
    <div className="rounded-[var(--radius-md)] bg-[var(--color-bg-base)] border border-[var(--color-border)] p-[var(--space-4)]">
      <h3 className="text-[var(--font-size-base)] font-semibold text-[var(--color-text-primary)] mb-[var(--space-4)]">
        Mix por canal
      </h3>
      <ResponsiveContainer width="100%" height={260}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={50}
            outerRadius={90}
            paddingAngle={2}
            dataKey="value"
          >
            {chartData.map((_, index) => (
              <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: 'var(--color-bg-base)',
              border: '1px solid var(--color-border)',
              borderRadius: '8px',
              fontSize: '13px',
            }}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
