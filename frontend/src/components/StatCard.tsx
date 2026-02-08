import { MoreVertical, TrendingUp, TrendingDown } from "lucide-react";
import { ReactNode } from "react";

interface StatCardProps {
  title: string;
  value: string;
  trend?: { value: string; positive: boolean };
  icon?: ReactNode;
  badge?: string;
}

export function StatCard({ title, value, trend, icon, badge }: StatCardProps) {
  return (
    <div className="bg-card rounded-xl p-5 border border-border flex flex-col gap-3 min-w-0">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {icon && <div className="text-primary">{icon}</div>}
          <span className="text-sm font-medium text-muted-foreground">{title}</span>
        </div>
        <button className="text-muted-foreground hover:text-foreground">
          <MoreVertical className="h-4 w-4" />
        </button>
      </div>
      <p className="text-2xl font-bold text-foreground">{value}</p>
      {trend && (
        <div className="flex items-center gap-2">
          <span className={`flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full ${
            trend.positive 
              ? "bg-success/10 text-success" 
              : "bg-destructive/10 text-destructive"
          }`}>
            {trend.positive ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
            {trend.value}
          </span>
          {badge && <span className="text-xs text-muted-foreground bg-secondary px-2 py-0.5 rounded">{badge}</span>}
        </div>
      )}
    </div>
  );
}
