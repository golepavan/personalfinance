import { Search, Bell, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";
import { fetchAuthStatus, type User } from "@/lib/api";

interface DashboardHeaderProps {
  onSync?: () => void;
  syncing?: boolean;
}

export function DashboardHeader({ onSync, syncing }: DashboardHeaderProps) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    fetchAuthStatus()
      .then(data => setUser(data.user))
      .catch(console.error);
  }, []);

  const userName = user?.first_name || "User";
  const userInitial = userName.charAt(0).toUpperCase();

  return (
    <header className="flex items-center justify-between px-6 py-4 bg-card border-b border-border">
      <div>
        <h1 className="text-xl font-semibold text-foreground">
          Hi, {userName} 👋
        </h1>
        <p className="text-sm text-muted-foreground">Track your expenses and transactions</p>
      </div>

      <div className="flex items-center gap-4">
        <div className="hidden md:flex items-center gap-2 bg-secondary rounded-xl px-4 py-2 w-72">
          <Search className="h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search expenses, transactions..."
            className="bg-transparent border-none outline-none text-sm w-full text-foreground placeholder:text-muted-foreground"
          />
        </div>

        {/* Sync Button */}
        <button
          onClick={onSync}
          disabled={syncing}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-xl hover:bg-primary/90 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${syncing ? 'animate-spin' : ''}`} />
          <span className="hidden sm:inline">{syncing ? 'Syncing...' : 'Sync'}</span>
        </button>

        <button className="relative p-2 rounded-xl hover:bg-secondary transition-colors">
          <Bell className="h-5 w-5 text-muted-foreground" />
        </button>

        <div className="w-9 h-9 rounded-full bg-primary/20 flex items-center justify-center overflow-hidden">
          <span className="text-sm font-semibold text-primary">{userInitial}</span>
        </div>
      </div>
    </header>
  );
}
