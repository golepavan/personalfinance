import { MoreVertical } from "lucide-react";
import { formatCurrency, type CategoryData } from "@/lib/api";
import { useState } from "react";

// Chart colors matching the theme - more vibrant pastel palette
const COLORS = [
  "#22c55e", // green
  "#3b82f6", // blue  
  "#f97316", // orange
  "#ef4444", // red
  "#14b8a6", // teal
  "#eab308", // yellow
  "#8b5cf6", // purple
  "#ec4899", // pink
];

interface TopCategoryChartProps {
  data: CategoryData[];
}

export function TopCategoryChart({ data }: TopCategoryChartProps) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const total = data.reduce((sum, c) => sum + c.total, 0);

  // Build donut segments
  let cumulative = 0;
  const segments = data.slice(0, 8).map((c, i) => {
    const pct = total > 0 ? (c.total / total) * 100 : 0;
    const offset = cumulative;
    cumulative += pct;
    return {
      pct,
      offset,
      color: COLORS[i % COLORS.length],
      category: c.category,
      amount: c.total
    };
  });

  const categories = data.slice(0, 8).map((c, i) => ({
    name: c.category,
    amount: formatCurrency(c.total),
    rawAmount: c.total,
    percentage: total > 0 ? ((c.total / total) * 100).toFixed(1) : "0",
    color: COLORS[i % COLORS.length],
    count: c.count
  }));

  // Get hovered category info
  const hoveredCategory = hoveredIndex !== null ? categories[hoveredIndex] : null;

  return (
    <div className="bg-card rounded-xl p-5 border border-border w-full lg:w-[420px]">
      <div className="flex items-center justify-between mb-6">
        <h3 className="font-semibold text-foreground">Spending by Category</h3>
        <div className="flex items-center gap-2">
          <select className="text-xs bg-secondary text-foreground rounded-lg px-3 py-1.5 border border-border outline-none cursor-pointer">
            <option>All Time</option>
          </select>
          <button className="text-muted-foreground hover:text-foreground">
            <MoreVertical className="h-4 w-4" />
          </button>
        </div>
      </div>
      <div className="flex items-center gap-6">
        <div className="relative w-40 h-40 shrink-0">
          <svg viewBox="0 0 42 42" className="w-full h-full -rotate-90">
            {/* Background circle */}
            <circle
              cx="21" cy="21" r="15"
              fill="none"
              stroke="hsl(var(--border))"
              strokeWidth="5"
            />
            {/* Segment circles */}
            {segments.map((seg, i) => (
              <circle
                key={i}
                cx="21" cy="21" r="15"
                fill="none"
                stroke={seg.color}
                strokeWidth={hoveredIndex === i ? "6.5" : "5"}
                strokeDasharray={`${seg.pct * 0.9425} ${94.25 - seg.pct * 0.9425}`}
                strokeDashoffset={`${-seg.offset * 0.9425}`}
                className="transition-all duration-300 cursor-pointer"
                style={{
                  opacity: hoveredIndex === null || hoveredIndex === i ? 1 : 0.4,
                  filter: hoveredIndex === i ? "brightness(1.1)" : "none"
                }}
                onMouseEnter={() => setHoveredIndex(i)}
                onMouseLeave={() => setHoveredIndex(null)}
              />
            ))}
          </svg>
          {/* Center content */}
          <div className="absolute inset-0 flex flex-col items-center justify-center transition-all duration-300">
            {hoveredCategory ? (
              <>
                <span className="text-lg font-bold text-foreground">{hoveredCategory.percentage}%</span>
                <span className="text-xs text-muted-foreground text-center px-2 truncate max-w-[100px]">{hoveredCategory.name}</span>
              </>
            ) : (
              <>
                <span className="text-lg font-bold text-foreground">{formatCurrency(total)}</span>
                <span className="text-xs text-muted-foreground">Total</span>
              </>
            )}
          </div>
        </div>
        <ul className="space-y-2 min-w-0 flex-1 max-h-[160px] overflow-y-auto">
          {categories.map((cat, i) => (
            <li
              key={cat.name}
              className={`flex items-center justify-between gap-2 p-1.5 rounded-lg transition-all duration-200 cursor-pointer ${hoveredIndex === i ? 'bg-secondary' : 'hover:bg-secondary/50'}`}
              onMouseEnter={() => setHoveredIndex(i)}
              onMouseLeave={() => setHoveredIndex(null)}
            >
              <div className="flex items-center gap-2 min-w-0">
                <span
                  className="w-3 h-3 rounded-full shrink-0 transition-transform duration-200"
                  style={{
                    backgroundColor: cat.color,
                    transform: hoveredIndex === i ? "scale(1.3)" : "scale(1)"
                  }}
                />
                <span className="text-xs text-foreground truncate">{cat.name}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-muted-foreground">{cat.percentage}%</span>
                <span className="text-xs font-medium text-foreground whitespace-nowrap">{cat.amount}</span>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
