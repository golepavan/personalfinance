// API Service for Splitwise Analytics
const API_BASE = '/api';

export interface Expense {
    id: number;
    description: string;
    date: string;
    amount: number;
    category: string;
    ai_category?: string;
    payer_name: string;
    user_share: number;
}

export interface CategoryData {
    category: string;
    total: number;
    count: number;
}

export interface MonthlyData {
    month: string;
    total: number;
    count: number;
}

export interface DashboardData {
    total_expenses: number;
    expense_count: number;
    categories: CategoryData[];
    monthly: MonthlyData[];
    yearly: { year: string; total: number; count: number }[];
    recent_expenses: Expense[];
    this_month_expenses?: number; // Optional - calculated from monthly if not present
}

export async function fetchDashboard(): Promise<DashboardData> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5s timeout

    try {
        const response = await fetch(`${API_BASE}/dashboard`, { signal: controller.signal });
        clearTimeout(timeoutId);
        if (!response.ok) {
            throw new Error('Failed to fetch dashboard data');
        }
        const json = await response.json();
        // API returns { dashboard: {...} }, so unwrap it
        return json.dashboard || json;
    } catch (error) {
        clearTimeout(timeoutId);
        throw error;
    }
}

export async function fetchExpenses(params?: {
    year?: string;
    month?: string;
    category?: string;
}): Promise<Expense[]> {
    const searchParams = new URLSearchParams();
    if (params?.year) searchParams.set('year', params.year);
    if (params?.month) searchParams.set('month', params.month);
    if (params?.category) searchParams.set('category', params.category);

    const url = searchParams.toString()
        ? `${API_BASE}/expenses?${searchParams}`
        : `${API_BASE}/expenses`;

    const response = await fetch(url);
    if (!response.ok) {
        throw new Error('Failed to fetch expenses');
    }
    const json = await response.json();
    // API returns { expenses: [...], count, success }, so unwrap it
    return json.expenses || [];
}

export async function syncExpenses(daysBack: number = 30): Promise<{ message: string; new_expenses: number }> {
    const response = await fetch(`${API_BASE}/sync`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ days_back: daysBack })
    });
    if (!response.ok) {
        throw new Error('Failed to sync expenses');
    }
    return response.json();
}

export function formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(amount);
}

export interface User {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
}

export interface AuthStatus {
    authenticated: boolean;
    user: User | null;
}

export async function fetchAuthStatus(): Promise<AuthStatus> {
    const response = await fetch(`${API_BASE}/auth/status`);
    if (!response.ok) {
        throw new Error('Failed to fetch auth status');
    }
    const json = await response.json();
    return {
        authenticated: json.authenticated,
        user: json.user || null
    };
}
