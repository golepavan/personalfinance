import { MoreVertical } from "lucide-react";

export function GoalCard() {
  const progress = (75000 / 145000) * 100;

  return (
    <div className="bg-card rounded-xl p-5 border border-border flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-muted-foreground">Goal</span>
        <button className="text-muted-foreground hover:text-foreground">
          <MoreVertical className="h-4 w-4" />
        </button>
      </div>
      <div className="flex items-center gap-4">
        <div className="relative w-14 h-14 shrink-0">
          <svg className="w-14 h-14 -rotate-90" viewBox="0 0 56 56">
            <circle cx="28" cy="28" r="24" fill="none" stroke="hsl(var(--border))" strokeWidth="4" />
            <circle
              cx="28" cy="28" r="24" fill="none"
              stroke="hsl(var(--accent))" strokeWidth="4"
              strokeDasharray={`${(progress / 100) * 150.8} 150.8`}
              strokeLinecap="round"
            />
          </svg>
        </div>
        <div className="min-w-0">
          <p className="font-semibold text-foreground text-sm">Apple iPhone 17 Pro</p>
          <p className="text-xs text-muted-foreground">Required: ₹1,45,000</p>
          <p className="text-xs text-muted-foreground">Collect: ₹75,000</p>
        </div>
      </div>
    </div>
  );
}
