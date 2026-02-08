import {
  LayoutDashboard, Receipt, BarChart3, PieChart, Settings, HelpCircle, LogOut, User
} from "lucide-react";
import { NavLink } from "@/components/NavLink";

const generalItems = [
  { title: "Dashboard", url: "/", icon: LayoutDashboard },
  { title: "All Expenses", url: "/expenses", icon: Receipt },
  { title: "Paid By Me", url: "/paid-by-me", icon: User },
];

const toolItems = [
  { title: "Analytics", url: "/analytics", icon: PieChart },
];

const otherItems = [
  { title: "Settings", url: "/settings", icon: Settings },
  { title: "Help Center", url: "/help", icon: HelpCircle },
  { title: "Logout", url: "/logout", icon: LogOut },
];

export function AppSidebar() {
  return (
    <aside className="hidden lg:flex flex-col w-[220px] min-h-screen bg-card border-r border-border px-4 py-6 shrink-0">
      <div className="flex items-center gap-2 mb-8 px-2">
        <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
          <span className="text-primary-foreground font-bold text-sm">S</span>
        </div>
        <span className="font-bold text-foreground tracking-tight">Splitwise</span>
      </div>

      <nav className="flex-1 flex flex-col gap-6">
        <SidebarSection label="General" items={generalItems} />
        <SidebarSection label="Tools" items={toolItems} />
        <SidebarSection label="Other" items={otherItems} />
      </nav>

      <div className="mt-4 rounded-xl bg-accent/10 border border-accent/30 p-4 text-center">
        <p className="font-semibold text-accent-foreground text-sm">Upgrade to PRO</p>
        <p className="text-xs text-muted-foreground mt-1">Upgrade to pro plan + Get 1 month more</p>
      </div>
    </aside>
  );
}

function SidebarSection({ label, items }: { label: string; items: typeof generalItems }) {
  return (
    <div>
      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2 px-2">{label}</p>
      <ul className="space-y-0.5">
        {items.map((item) => (
          <li key={item.title}>
            <NavLink
              to={item.url}
              end={item.url === "/"}
              className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-muted-foreground hover:bg-secondary transition-colors"
              activeClassName="bg-sidebar-accent text-sidebar-accent-foreground font-medium"
            >
              <item.icon className="h-4 w-4" />
              <span>{item.title}</span>
            </NavLink>
          </li>
        ))}
      </ul>
    </div>
  );
}
