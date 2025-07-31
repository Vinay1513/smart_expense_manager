import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { DollarSign, TrendingUp, Receipt, Calendar, Sparkles, TrendingDown, Users, Target } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import AnimatedGif from '../components/AnimatedGif';
import api from '../services/api';

const Dashboard = () => {
  const [summary, setSummary] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [summaryResponse, chartResponse] = await Promise.all([
        api.get('/analytics/summary/'),
        api.get('/analytics/chart-data/?type=category')
      ]);
      
      console.log('Summary response:', summaryResponse.data);
      console.log('Chart response:', chartResponse.data);
      
      setSummary(summaryResponse.data);
      setChartData(chartResponse.data);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="large" text="Loading your dashboard..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <div className="card-gradient max-w-md mx-auto">
          <div className="text-danger-600 dark:text-danger-400 mb-4">{error}</div>
          <button
            onClick={fetchDashboardData}
            className="btn btn-primary"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const COLORS = ['#0ea5e9', '#22c55e', '#f59e0b', '#ef4444', '#a855f7', '#06b6d4'];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="text-center">
        <div className="flex items-center justify-center space-x-3 mb-4">
          <div className="p-2 bg-gradient-to-r from-primary-500 to-purple-500 rounded-xl">
            <Sparkles className="h-6 w-6 text-white" />
          </div>
          <h1 className="text-4xl font-bold gradient-text">Dashboard</h1>
        </div>
        <p className="text-gray-600 dark:text-gray-400 text-lg">Overview of your expense management</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="stat-card group">
          <div className="flex items-center">
            <div className="p-4 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-2xl shadow-lg group-hover:shadow-xl transition-all duration-300">
              <DollarSign className="h-8 w-8 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Expenses</p>
              <p className="text-2xl font-bold text-gradient">
                ${(parseFloat(summary?.total_expenses) || 0).toLocaleString()}
              </p>
            </div>
          </div>
        </div>

        <div className="stat-card group">
          <div className="flex items-center">
            <div className="p-4 bg-gradient-to-r from-green-500 to-emerald-500 rounded-2xl shadow-lg group-hover:shadow-xl transition-all duration-300">
              <Receipt className="h-8 w-8 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Transactions</p>
              <p className="text-2xl font-bold text-gradient-success">
                {summary?.total_count || '0'}
              </p>
            </div>
          </div>
        </div>

        <div className="stat-card group">
          <div className="flex items-center">
            <div className="p-4 bg-gradient-to-r from-orange-500 to-red-500 rounded-2xl shadow-lg group-hover:shadow-xl transition-all duration-300">
              <TrendingUp className="h-8 w-8 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Average Amount</p>
              <p className="text-2xl font-bold text-gradient-warning">
                ${(parseFloat(summary?.average_amount) || 0).toFixed(2)}
              </p>
            </div>
          </div>
        </div>

        <div className="stat-card group">
          <div className="flex items-center">
            <div className="p-4 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl shadow-lg group-hover:shadow-xl transition-all duration-300">
              <Calendar className="h-8 w-8 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">This Month</p>
              <p className="text-2xl font-bold text-gradient-danger">
                ${(parseFloat(summary?.monthly_data?.[0]?.total) || 0).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Category Breakdown */}
        <div className="card-gradient">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 bg-gradient-to-r from-primary-500 to-purple-500 rounded-xl">
              <Target className="h-5 w-5 text-white" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Category Breakdown</h3>
          </div>
          {chartData && chartData.labels && chartData.labels.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={chartData.labels.map((label, index) => ({
                    name: label,
                    value: chartData.datasets[0].data[index]
                  }))}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {chartData.labels.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'var(--tw-bg-opacity, 1)',
                    border: 'none',
                    borderRadius: '12px',
                    color: 'var(--tw-text-opacity, 1)',
                    boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
              <div className="text-center">
                <Target className="h-12 w-12 mx-auto mb-4 text-gray-300 dark:text-gray-600" />
                <p>No category data available</p>
              </div>
            </div>
          )}
        </div>

        {/* Monthly Trend */}
        <div className="card-gradient">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl">
              <TrendingUp className="h-5 w-5 text-white" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Monthly Trend</h3>
          </div>
          {summary?.monthly_data && summary.monthly_data.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={summary.monthly_data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                <XAxis 
                  dataKey="month" 
                  stroke="#6B7280"
                  fontSize={12}
                />
                <YAxis 
                  stroke="#6B7280"
                  fontSize={12}
                />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'var(--tw-bg-opacity, 1)',
                    border: 'none',
                    borderRadius: '12px',
                    color: 'var(--tw-text-opacity, 1)',
                    boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)'
                  }}
                />
                <Bar dataKey="total" fill="url(#gradient)" radius={[6, 6, 0, 0]} />
                <defs>
                  <linearGradient id="gradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#0ea5e9" />
                    <stop offset="100%" stopColor="#0284c7" />
                  </linearGradient>
                </defs>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
              <div className="text-center">
                <TrendingUp className="h-12 w-12 mx-auto mb-4 text-gray-300 dark:text-gray-600" />
                <p>No monthly data available</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Category Breakdown Table */}
      {summary?.category_breakdown && summary.category_breakdown.length > 0 && (
        <div className="card-gradient">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl">
              <Users className="h-5 w-5 text-white" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Category Details</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Category
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Count
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Percentage
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white/50 dark:bg-gray-800/50 divide-y divide-gray-200 dark:divide-gray-700">
                {summary.category_breakdown.map((category) => (
                  <tr key={category.id} className="hover:bg-gray-50/50 dark:hover:bg-gray-700/50 transition-all duration-200">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div
                          className="w-4 h-4 rounded-full mr-3 shadow-lg"
                          style={{ backgroundColor: category.color }}
                        ></div>
                        <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                          {category.name}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900 dark:text-gray-100">
                      ${(parseFloat(category.total) || 0).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900 dark:text-gray-100">
                      {category.count}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900 dark:text-gray-100">
                      {category.percentage}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty State */}
      {(!summary?.category_breakdown || summary.category_breakdown.length === 0) && (
        <div className="card-gradient text-center py-16 bounce-in">
          <div className="text-gray-400 dark:text-gray-500 mb-6">
            <AnimatedGif 
              src="https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif"
              alt="Empty state animation"
              className="w-32 h-32 mx-auto mb-4"
            />
          </div>
          <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">No expenses yet</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-8 text-lg">Start tracking your expenses to see beautiful analytics here</p>
          <button
            onClick={() => window.location.href = '/expenses/add'}
            className="btn btn-primary pulse-glow"
          >
            Add Your First Expense
          </button>
        </div>
      )}
    </div>
  );
};

export default Dashboard; 