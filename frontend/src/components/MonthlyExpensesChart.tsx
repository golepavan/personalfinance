import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip } from "recharts";
import { MoreVertical, TrendingUp } from "lucide-react";
import { formatCurrency, type MonthlyData } from "@/lib/api";
import { useState, useMemo } from "react";

interface MonthlyExpensesChartProps {
  data: MonthlyData[];
}

export function MonthlyExpensesChart({ data }: MonthlyExpensesChartProps) {
  // Get available years from data
  const availableYears = useMemo(() => {
    const years = [...new Set(data.map(m => m.month.split('-')[0]))];
    return years.sort().reverse();
  }, [data]);

  const [selectedYear, setSelectedYear] = useState<string>(availableYears[0] || new Date().getFullYear().toString());

  // Filter and format data for selected year
  const chartData = useMemo(() => {
    const yearData = data.filter(m => m.month.startsWith(selectedYear));
    return yearData.reverse().map(m => {
      const [year, month] = m.month.split('-');
      const date = new Date(parseInt(year), parseInt(month) - 1);
      return {
        month: date.toLocaleDateString('en-US', { month: 'short' }),
        amount: m.total,
        fullMonth: m.month
      };
    });
  }, [data, selectedYear]);

  // Calculate total for selected year
  const yearTotal = useMemo(() =>
    chartData.reduce((sum, m) => sum + m.amount, 0), [chartData]);

  return (
    <div className="bg-card rounded-xl p-5 border border-border flex-1">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <h3 className="font-semibold text-foreground">Monthly Expenses</h3>
          <span className="flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-success/10 text-success">
            <TrendingUp className="h-3 w-3" /> {formatCurrency(yearTotal)}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={selectedYear}
            onChange={(e) => setSelectedYear(e.target.value)}
            className="text-xs bg-secondary text-foreground rounded-lg px-3 py-1.5 border border-border outline-none cursor-pointer"
          >
            {availableYears.map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
          <button className="text-muted-foreground hover:text-foreground">
            <MoreVertical className="h-4 w-4" />
          </button>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={chartData} barSize={32}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
          <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} />
          <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
          <Tooltip
            contentStyle={{ backgroundColor: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 8 }}
            formatter={(value: number) => [formatCurrency(value), "Amount"]}
          />
          <Bar dataKey="amount" fill="hsl(var(--primary))" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
