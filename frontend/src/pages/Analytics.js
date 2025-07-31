import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { DollarSign, TrendingUp, Receipt, Calendar, Filter, BarChart3, Sparkles } from 'lucide-react';
import api from '../services/api';

const Analytics = () => {
  const [summary, setSummary] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [chartType, setChartType] = useState('category');
  const [dateRange, setDateRange] = useState('month');

  useEffect(() => {
    fetchAnalyticsData();
  }, [chartType, dateRange]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const [summaryResponse, chartResponse] = await Promise.all([
        api.get(`/analytics/summary/?date_range=${dateRange}`),
        api.get(`/analytics/chart-data/?type=${chartType}&date_range=${dateRange}`)
      ]);
      
      console.log('Summary response:', summaryResponse.data);
      console.log('Chart response:', chartResponse.data);
      setSummary(summaryResponse.data);
      setChartData(chartResponse.data);
    } catch (err) {
      setError('Failed to load analytics data');
      console.error('Analytics error:', err);
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ['#0ea5e9', '#22c55e', '#f59e0b', '#ef4444', '#a855f7', '#06b6d4', '#f97316', '#84cc16'];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 dark:border-primary-400"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <div className="card-gradient max-w-md mx-auto">
          <div className="text-danger-600 dark:text-danger-400 mb-4">{error}</div>
          <button
            onClick={fetchAnalyticsData}
            className="btn btn-primary"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center space-x-3 mb-2">
            <div className="p-2 bg-gradient-to-r from-orange-500 to-red-500 rounded-xl">
              <BarChart3 className="h-5 w-5 text-white" />
            </div>
            <h1 className="text-3xl font-bold gradient-text">Analytics</h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400 text-lg">Detailed insights into your spending patterns</p>
        </div>
        
        <div className="flex items-center space-x-4 mt-4 sm:mt-0">
          <div className="analytics-filter">
            <select
              value={chartType}
              onChange={(e) => setChartType(e.target.value)}
            >
              <option value="category">Category Breakdown</option>
              <option value="monthly">Monthly Trends</option>
            </select>
            <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
              <Filter className="h-4 w-4 text-gray-500 dark:text-gray-400" />
            </div>
          </div>
          
          <div className="analytics-filter">
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
            >
              <option value="month">This Month</option>
              <option value="quarter">This Quarter</option>
              <option value="year">This Year</option>
            </select>
            <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
              <Calendar className="h-4 w-4 text-gray-500 dark:text-gray-400" />
            </div>
          </div>
        </div>
      </div>

      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-primary-100 dark:bg-primary-900/20 rounded-lg">
                <DollarSign className="h-6 w-6 text-primary-600 dark:text-primary-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Expenses</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  ${summary.total_expenses?.toFixed(2) || '0.00'}
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-success-100 dark:bg-success-900/20 rounded-lg">
                <Receipt className="h-6 w-6 text-success-600 dark:text-success-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Transactions</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {summary.total_count || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-warning-100 dark:bg-warning-900/20 rounded-lg">
                <TrendingUp className="h-6 w-6 text-warning-600 dark:text-warning-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Average Amount</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  ${typeof summary.average_amount === 'number' ? summary.average_amount.toFixed(2) : '0.00'}
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-info-100 dark:bg-info-900/20 rounded-lg">
                <Calendar className="h-6 w-6 text-info-600 dark:text-info-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Categories Used</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {summary.category_breakdown?.length || 0}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {chartData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Chart */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              {chartType === 'category' ? 'Category Breakdown' : 'Monthly Trends'}
            </h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                {chartType === 'category' ? (
                  <PieChart>
                    <Pie
                      data={chartData.labels?.map((label, index) => ({
                        name: label,
                        value: chartData.datasets[0].data[index]
                      })) || []}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {chartData.labels?.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                ) : (
                  <BarChart data={chartData.labels?.map((label, index) => ({
                    name: label,
                    amount: chartData.datasets[0].data[index]
                  })) || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="amount" fill="#3B82F6" />
                  </BarChart>
                )}
              </ResponsiveContainer>
            </div>
          </div>

          {/* Category Breakdown Table */}
          {summary?.category_breakdown && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                Category Details
              </h3>
              <div className="space-y-3">
                {summary.category_breakdown.map((category, index) => (
                  <div key={category.id} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl border border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-300">
                    <div className="flex items-center space-x-3">
                      <div
                        className="category-color-indicator"
                        style={{ 
                          backgroundColor: category.color || COLORS[index % COLORS.length],
                          boxShadow: `0 0 0 2px ${category.color || COLORS[index % COLORS.length]}20`
                        }}
                      ></div>
                      <div>
                        <p className="font-semibold text-gray-900 dark:text-gray-100">{category.name}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{category.count} transactions</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-gray-900 dark:text-gray-100 text-lg">
                        ${typeof category.total === 'number' ? category.total.toFixed(2) : '0.00'}
                      </p>
                      <p className="text-sm font-medium text-primary-600 dark:text-primary-400">
                        {typeof category.percentage === 'number' ? category.percentage.toFixed(1) : '0'}%
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {!summary && !chartData && (
        <div className="text-center py-12">
          <div className="text-gray-400 dark:text-gray-500 mb-4">
            <BarChart3 className="h-12 w-12 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No analytics data available</h3>
          <p className="text-gray-600 dark:text-gray-400">
            Start adding expenses to see detailed analytics and insights.
          </p>
        </div>
      )}
    </div>
  );
};

export default Analytics; 