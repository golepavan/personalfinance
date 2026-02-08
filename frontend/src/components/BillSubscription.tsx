import { MoreVertical } from "lucide-react";

const subscriptions = [
  { name: "Netflix", date: "15 June 2025", amount: "₹149.00", color: "hsl(var(--chart-red))" },
  { name: "Spotify", date: "24 Aug 2025", amount: "₹49.00", color: "hsl(var(--chart-green))" },
  { name: "Figma", date: "01 Jan 2026", amount: "₹3,999.00", color: "hsl(var(--chart-blue))" },
  { name: "WIFI", date: "11 June 2025", amount: "₹399.00", color: "hsl(var(--chart-orange))" },
  { name: "Electricity", date: "31 June 2025", amount: "₹1,265.00", color: "hsl(var(--chart-yellow))" },
];

export function BillSubscription() {
  return (
    <div className="bg-card rounded-xl p-5 border border-border w-full lg:w-[280px]">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-foreground text-sm">Bill & Subscription</h3>
        <button className="text-muted-foreground hover:text-foreground">
          <MoreVertical className="h-4 w-4" />
        </button>
      </div>
      <ul className="space-y-3">
        {subscriptions.map((sub) => (
          <li key={sub.name} className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3 min-w-0">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold shrink-0" style={{ backgroundColor: sub.color, color: "white" }}>
                {sub.name[0]}
              </div>
              <div className="min-w-0">
                <p className="text-sm font-medium text-foreground">{sub.name}</p>
                <p className="text-[11px] text-muted-foreground">{sub.date}</p>
              </div>
            </div>
            <span className="text-sm font-semibold text-foreground whitespace-nowrap">{sub.amount}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
