import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { format } from 'date-fns';
import { Plus, Search, Edit, Trash2, Calendar, Receipt, Sparkles } from 'lucide-react';
import AnimatedGif from '../components/AnimatedGif';
import api from '../services/api';

const Expenses = () => {
  const [expenses, setExpenses] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedDate, setSelectedDate] = useState('');
  const location = useLocation();

  useEffect(() => {
    fetchData();
  }, []);

  // Refresh data when component comes into focus (e.g., after editing)
  useEffect(() => {
    const handleFocus = () => {
      fetchData();
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, []);

  // Refresh data when location changes (e.g., navigating back from edit page)
  useEffect(() => {
    fetchData();
  }, [location.pathname]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [expensesResponse, categoriesResponse] = await Promise.all([
        api.get('/expenses/'),
        api.get('/categories/')
      ]);
      
      const expensesData = expensesResponse.data.results || expensesResponse.data;
      setExpenses(Array.isArray(expensesData) ? expensesData : []);
      // Handle paginated response from DRF
      const categoriesData = categoriesResponse.data.results || categoriesResponse.data;
      setCategories(Array.isArray(categoriesData) ? categoriesData : []);
      
      // Debug: Check expense 23 data
      const expense23 = expensesData.find(e => e.id === 23);
      if (expense23) {
        console.log('Expense 23 loaded:', expense23);
        console.log('Expense 23 category:', expense23.category);
      }
    } catch (err) {
      setError('Failed to load expenses');
      console.error('Expenses error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this expense?')) {
      try {
        await api.delete(`/expenses/${id}/`);
        setExpenses(expenses.filter(expense => expense.id !== id));
      } catch (err) {
        setError('Failed to delete expense');
        console.error('Delete error:', err);
      }
    }
  };

  const filteredExpenses = expenses.filter(expense => {
    const matchesSearch = expense.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         expense.description.toLowerCase().includes(searchTerm.toLowerCase());
    
    // Handle both category objects and category IDs
    const categoryId = expense.category?.id || expense.category;
    const matchesCategory = !selectedCategory || categoryId === parseInt(selectedCategory);
    
    const matchesDate = !selectedDate || expense.date === selectedDate;
    
    // Debug logging for category filtering
    if (selectedCategory && expense.id === 23) { // Debug for expense ID 23
      console.log('Filtering expense 23:', {
        expenseId: expense.id,
        category: expense.category,
        categoryId: categoryId,
        selectedCategory: selectedCategory,
        matchesCategory: matchesCategory
      });
    }
    
    return matchesSearch && matchesCategory && matchesDate;
  });

  const getPaymentMethodIcon = (method) => {
    switch (method) {
      case 'card':
        return '💳';
      case 'cash':
        return '💵';
      case 'bank_transfer':
        return '🏦';
      case 'digital_wallet':
        return '📱';
      default:
        return '💰';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AnimatedGif 
            src="https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif"
            alt="Loading animation"
            className="w-16 h-16 mx-auto mb-4"
          />
          <p className="text-gray-600 dark:text-gray-400">Loading your expenses...</p>
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
            <div className="p-2 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl">
              <Receipt className="h-5 w-5 text-white" />
            </div>
            <h1 className="text-3xl font-bold gradient-text">Expenses</h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400 text-lg">Manage and track your expenses</p>
        </div>
        <Link
          to="/expenses/add"
          className="btn btn-primary flex items-center space-x-2 mt-4 sm:mt-0"
        >
          <Plus className="h-4 w-4" />
          <span>Add Expense</span>
        </Link>
      </div>

      {error && (
        <div className="bg-danger-50 border border-danger-200 text-danger-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search expenses..."
                className="input pl-10"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
          
          <div className="flex gap-4">
            <select
              className="input"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              <option value="">All Categories</option>
              {Array.isArray(categories) && categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
            
            <input
              type="date"
              className="input"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Expenses List */}
      <div className="space-y-4">
        {filteredExpenses.length === 0 ? (
          <div className="text-center py-12 bounce-in">
            <div className="text-gray-400 dark:text-gray-500 mb-4">
              <AnimatedGif 
                src="https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif"
                alt="No expenses found"
                className="w-16 h-16 mx-auto"
              />
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No expenses found</h3>
            <p className="text-gray-600 dark:text-gray-400">
              {expenses.length === 0 ? 'Start by adding your first expense.' : 'Try adjusting your filters.'}
            </p>
            {expenses.length === 0 && (
              <Link to="/expenses/add" className="btn btn-primary mt-4 pulse-glow">
                Add Your First Expense
              </Link>
            )}
          </div>
        ) : (
          filteredExpenses.map((expense, index) => {
            // Handle both category objects and category IDs
            const category = expense.category;
            const categoryName = category?.name || 'Unknown';
            const categoryColor = category?.color || '#6B7280';
            const categoryId = category?.id || category;
            
            // Debug logging for expense 23
            if (expense.id === 23) {
              console.log('Displaying expense 23:', {
                expenseId: expense.id,
                category: category,
                categoryName: categoryName,
                categoryColor: categoryColor,
                categoryId: categoryId
              });
            }
            
            return (
              <div 
                key={expense.id} 
                className="card hover:shadow-md transition-shadow slide-in-left"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: categoryColor }}
                    ></div>
                    <div>
                      <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">{expense.title}</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{expense.description}</p>
                      <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500 dark:text-gray-400">
                        <span className="flex items-center">
                          <Calendar className="h-4 w-4 mr-1" />
                          {format(new Date(expense.date), 'MMM dd, yyyy')}
                        </span>
                        <span className="flex items-center">
                          {getPaymentMethodIcon(expense.payment_method)}
                          {expense.payment_method.replace('_', ' ')}
                        </span>
                        <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded-full text-gray-700 dark:text-gray-300">
                          {categoryName}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                        ${parseFloat(expense.amount).toFixed(2)}
                      </p>
                    </div>
                    
                    <div className="flex space-x-2">
                      <Link
                        to={`/expenses/${expense.id}/edit`}
                        className="p-2 text-gray-400 hover:text-primary-600 transition-colors"
                      >
                        <Edit className="h-4 w-4" />
                      </Link>
                      <button
                        onClick={() => handleDelete(expense.id)}
                        className="p-2 text-gray-400 hover:text-danger-600 transition-colors"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Summary */}
      {filteredExpenses.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Expenses</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                ${filteredExpenses.reduce((sum, expense) => sum + parseFloat(expense.amount), 0).toFixed(2)}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600 dark:text-gray-400">Showing {filteredExpenses.length} of {expenses.length} expenses</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Expenses; 