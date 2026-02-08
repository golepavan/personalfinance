import { MoreVertical, Filter } from "lucide-react";
import { formatCurrency, type Expense } from "@/lib/api";

interface RecentExpensesProps {
  data: Expense[];
}

export function RecentExpenses({ data }: RecentExpensesProps) {
  return (
    <div className="bg-card rounded-xl p-5 border border-border flex-1">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-foreground">Recent Expenses</h3>
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-1 text-xs bg-secondary text-foreground rounded-lg px-3 py-1.5 border border-border">
            <Filter className="h-3 w-3" /> Filter
          </button>
          <select className="text-xs bg-secondary text-foreground rounded-lg px-3 py-1.5 border border-border outline-none">
            <option>Recent</option>
          </select>
          <button className="text-muted-foreground hover:text-foreground">
            <MoreVertical className="h-4 w-4" />
          </button>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-muted-foreground text-xs border-b border-border">
              <th className="text-left py-2 font-medium">S.N</th>
              <th className="text-left py-2 font-medium">Amount</th>
              <th className="text-left py-2 font-medium">Category</th>
              <th className="text-left py-2 font-medium">Description</th>
              <th className="text-left py-2 font-medium">Date</th>
            </tr>
          </thead>
          <tbody>
            {data.slice(0, 10).map((e, index) => (
              <tr key={e.id} className="border-b border-border last:border-0">
                <td className="py-3 text-foreground">{index + 1}.</td>
                <td className="py-3 font-medium text-foreground">{formatCurrency(e.amount)}</td>
                <td className="py-3">
                  <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded">{e.category}</span>
                </td>
                <td className="py-3 text-foreground truncate max-w-[200px]">{e.description}</td>
                <td className="py-3 text-muted-foreground">
                  {new Date(e.date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
