import { AppSidebar } from "@/components/AppSidebar";
import { DashboardHeader } from "@/components/DashboardHeader";
import { useEffect, useState } from "react";
import { fetchExpenses, formatCurrency, type Expense } from "@/lib/api";
import { Filter, Download, Search } from "lucide-react";

const Expenses = () => {
    const [expenses, setExpenses] = useState<Expense[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");
    const [selectedYear, setSelectedYear] = useState<string>("");
    const [selectedMonth, setSelectedMonth] = useState<string>("");
    const [selectedCategory, setSelectedCategory] = useState<string>("");

    useEffect(() => {
        setLoading(true);
        fetchExpenses({
            year: selectedYear || undefined,
            month: selectedMonth || undefined,
            category: selectedCategory || undefined
        })
            .then(setExpenses)
            .catch(console.error)
            .finally(() => setLoading(false));
    }, [selectedYear, selectedMonth, selectedCategory]);

    // Get unique years and AI categories for filters
    const years = [...new Set(expenses.map(e => e.date.split('-')[0]))].sort().reverse();
    const categories = [...new Set(expenses.map(e => e.ai_category || e.category).filter(Boolean))].sort();

    // Filter by search term (check description and ai_category)
    const filteredExpenses = expenses.filter(e => {
        const aiCat = e.ai_category || e.category || '';
        return e.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
            aiCat.toLowerCase().includes(searchTerm.toLowerCase());
    });

    // Calculate totals (my share, not full amount)
    const totalAmount = filteredExpenses.reduce((sum, e) => sum + e.user_share, 0);

    return (
        <div className="flex min-h-screen w-full bg-background">
            <AppSidebar />
            <div className="flex-1 flex flex-col min-w-0">
                <DashboardHeader />
                <main className="flex-1 p-6 overflow-auto">
                    {/* Header */}
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h2 className="text-2xl font-bold text-foreground">All Expenses</h2>
                            <p className="text-sm text-muted-foreground">
                                {filteredExpenses.length} transactions • Total: {formatCurrency(totalAmount)}
                            </p>
                        </div>
                        <button className="flex items-center gap-2 px-4 py-2 bg-secondary text-foreground rounded-xl border border-border hover:bg-secondary/80 transition-colors">
                            <Download className="h-4 w-4" />
                            Export
                        </button>
                    </div>

                    {/* Filters */}
                    <div className="bg-card rounded-xl p-4 border border-border mb-6">
                        <div className="flex flex-wrap items-center gap-4">
                            <div className="flex items-center gap-2 bg-secondary rounded-lg px-3 py-2 flex-1 min-w-[200px]">
                                <Search className="h-4 w-4 text-muted-foreground" />
                                <input
                                    type="text"
                                    placeholder="Search expenses..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="bg-transparent border-none outline-none text-sm w-full text-foreground placeholder:text-muted-foreground"
                                />
                            </div>
                            <select
                                value={selectedYear}
                                onChange={(e) => setSelectedYear(e.target.value)}
                                className="text-sm bg-secondary text-foreground rounded-lg px-3 py-2 border border-border outline-none cursor-pointer"
                            >
                                <option value="">All Years</option>
                                {years.map(year => (
                                    <option key={year} value={year}>{year}</option>
                                ))}
                            </select>
                            <select
                                value={selectedMonth}
                                onChange={(e) => setSelectedMonth(e.target.value)}
                                className="text-sm bg-secondary text-foreground rounded-lg px-3 py-2 border border-border outline-none cursor-pointer"
                            >
                                <option value="">All Months</option>
                                {Array.from({ length: 12 }, (_, i) => (
                                    <option key={i + 1} value={String(i + 1).padStart(2, '0')}>
                                        {new Date(2000, i).toLocaleString('en-US', { month: 'long' })}
                                    </option>
                                ))}
                            </select>
                            <select
                                value={selectedCategory}
                                onChange={(e) => setSelectedCategory(e.target.value)}
                                className="text-sm bg-secondary text-foreground rounded-lg px-3 py-2 border border-border outline-none cursor-pointer"
                            >
                                <option value="">All Categories</option>
                                {categories.map(cat => (
                                    <option key={cat} value={cat}>{cat}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {/* Expenses Table */}
                    <div className="bg-card rounded-xl border border-border overflow-hidden">
                        {loading ? (
                            <div className="p-8 text-center text-muted-foreground">Loading...</div>
                        ) : filteredExpenses.length === 0 ? (
                            <div className="p-8 text-center text-muted-foreground">No expenses found</div>
                        ) : (
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm">
                                    <thead>
                                        <tr className="bg-secondary/50 text-muted-foreground text-xs border-b border-border">
                                            <th className="text-left py-3 px-4 font-medium">Date</th>
                                            <th className="text-left py-3 px-4 font-medium">Description</th>
                                            <th className="text-left py-3 px-4 font-medium">AI Category</th>
                                            <th className="text-right py-3 px-4 font-medium">Amount</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {filteredExpenses.map((e) => (
                                            <tr key={e.id} className="border-b border-border last:border-0 hover:bg-secondary/30 transition-colors">
                                                <td className="py-3 px-4 text-muted-foreground whitespace-nowrap">
                                                    {new Date(e.date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                                                </td>
                                                <td className="py-3 px-4 text-foreground max-w-[300px] truncate">{e.description}</td>
                                                <td className="py-3 px-4">
                                                    <span className="text-xs bg-emerald-500/10 text-emerald-500 px-2 py-1 rounded-full">
                                                        {e.ai_category || e.category}
                                                    </span>
                                                </td>
                                                <td className="py-3 px-4 text-right font-medium text-primary">{formatCurrency(e.user_share)}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                </main>
            </div>
        </div>
    );
};

export default Expenses;
