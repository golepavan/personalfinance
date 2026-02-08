import { AppSidebar } from "@/components/AppSidebar";
import { DashboardHeader } from "@/components/DashboardHeader";
import { StatCard } from "@/components/StatCard";
import { MonthlyExpensesChart } from "@/components/MonthlyExpensesChart";
import { TopCategoryChart } from "@/components/TopCategoryChart";
import { RecentExpenses } from "@/components/RecentExpenses";
import { Wallet, Receipt, CalendarDays, TrendingUp } from "lucide-react";
import { useEffect, useState, useMemo } from "react";
import { fetchDashboard, syncExpenses, formatCurrency, type DashboardData } from "@/lib/api";

const Index = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [selectedYear, setSelectedYear] = useState<string>(""); // "" = All Years

  const loadData = () => {
    setLoading(true);
    fetchDashboard()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSync = async () => {
    setSyncing(true);
    try {
      await syncExpenses(30);
      loadData();
    } catch (error) {
      console.error('Sync failed:', error);
    } finally {
      setSyncing(false);
    }
  };

  // Get available years from yearly data
  const availableYears = useMemo(() => {
    if (!data?.yearly) return [];
    return data.yearly.map(y => y.year).sort().reverse();
  }, [data?.yearly]);

  // Calculate totals based on selected year
  const { totalExpenses, expenseCount } = useMemo(() => {
    if (!data) return { totalExpenses: 0, expenseCount: 0 };

    if (selectedYear === "") {
      // All years
      return {
        totalExpenses: data.total_expenses || 0,
        expenseCount: data.expense_count || 0
      };
    }

    // Find selected year data
    const yearData = data.yearly?.find(y => y.year === selectedYear);
    return {
      totalExpenses: yearData?.total || 0,
      expenseCount: yearData?.count || 0
    };
  }, [data, selectedYear]);

  // Filter monthly data by selected year for average calculation
  const filteredMonthly = useMemo(() => {
    if (!data?.monthly) return [];
    if (selectedYear === "") return data.monthly;
    return data.monthly.filter(m => m.month.startsWith(selectedYear));
  }, [data?.monthly, selectedYear]);

  // Calculate this month's expenses
  const currentMonth = new Date().toISOString().slice(0, 7);
  const thisMonthData = data?.monthly?.find(m => m.month === currentMonth);
  const thisMonthExpenses = data?.this_month_expenses || thisMonthData?.total || 0;

  // Calculate average monthly (based on filtered data)
  const avgMonthly = filteredMonthly.length
    ? filteredMonthly.reduce((sum, m) => sum + m.total, 0) / filteredMonthly.length
    : 0;

  if (loading) {
    return (
      <div className="flex min-h-screen w-full bg-background items-center justify-center">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen w-full bg-background">
      <AppSidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <DashboardHeader onSync={handleSync} syncing={syncing} />
        <main className="flex-1 p-6 overflow-auto">
          {/* Year Filter */}
          <div className="flex items-center justify-end mb-4">
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(e.target.value)}
              className="text-sm bg-card text-foreground rounded-lg px-4 py-2 border border-border outline-none cursor-pointer font-medium"
            >
              <option value="">All Years</option>
              {availableYears.map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>

          {/* Stat Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
            <StatCard
              title="Total Expenses"
              value={formatCurrency(totalExpenses)}
              icon={<Wallet className="h-4 w-4" />}
              trend={{ value: selectedYear || "All time", positive: true }}
            />
            <StatCard
              title="This Month"
              value={formatCurrency(thisMonthExpenses)}
              icon={<CalendarDays className="h-4 w-4" />}
              trend={{ value: "Current month", positive: true }}
            />
            <StatCard
              title="Monthly Average"
              value={formatCurrency(avgMonthly)}
              icon={<TrendingUp className="h-4 w-4" />}
              trend={{ value: selectedYear || "All time", positive: true }}
            />
            <StatCard
              title="Total Transactions"
              value={expenseCount.toLocaleString()}
              icon={<Receipt className="h-4 w-4" />}
              trend={{ value: selectedYear || "All time", positive: true }}
            />
          </div>

          {/* Charts */}
          <div className="flex flex-col lg:flex-row gap-4 mb-6">
            <MonthlyExpensesChart data={data?.monthly || []} />
            <TopCategoryChart data={data?.categories || []} />
          </div>

          {/* Recent Expenses */}
          <RecentExpenses data={data?.recent_expenses || []} />
        </main>
      </div>
    </div>
  );
};

export default Index;
