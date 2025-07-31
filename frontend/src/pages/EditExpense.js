import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Save, Edit, DollarSign, Calendar, Tag, CreditCard, FileText } from 'lucide-react';
import api from '../services/api';

const EditExpense = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    amount: '',
    category_id: '',
    date: '',
    payment_method: 'cash',
  });
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [error, setError] = useState('');

  const fetchData = useCallback(async () => {
    try {
      setFetching(true);
      const [expenseResponse, categoriesResponse] = await Promise.all([
        api.get(`/expenses/${id}/`),
        api.get('/categories/')
      ]);
      
      const expense = expenseResponse.data;
      setFormData({
        title: expense.title,
        description: expense.description || '',
        amount: expense.amount,
        category_id: expense.category.id,
        date: expense.date,
        payment_method: expense.payment_method,
      });
      
      // Handle paginated response from DRF
      const categoriesData = categoriesResponse.data.results || categoriesResponse.data;
      setCategories(Array.isArray(categoriesData) ? categoriesData : []);
    } catch (err) {
      setError('Failed to load expense data');
      console.error('Fetch expense error:', err);
    } finally {
      setFetching(false);
    }
  }, [id]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleChange = (e) => {
    const newFormData = {
      ...formData,
      [e.target.name]: e.target.value,
    };
    setFormData(newFormData);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Convert category_id to category for the API
      const submitData = {
        ...formData,
        category: formData.category_id
      };
      delete submitData.category_id;
      
      await api.put(`/expenses/${id}/`, submitData);
      navigate('/expenses');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update expense');
      console.error('Update expense error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (fetching) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error && !formData.title) {
    return (
      <div className="text-center py-8">
        <div className="card-gradient max-w-md mx-auto">
          <div className="text-danger-600 dark:text-danger-400 mb-4">{error}</div>
          <button
            onClick={() => navigate('/expenses')}
            className="btn btn-primary"
          >
            Back to Expenses
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/expenses')}
          className="p-3 rounded-xl bg-gradient-to-r from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-800 text-gray-600 dark:text-gray-300 hover:from-gray-200 hover:to-gray-300 dark:hover:from-gray-600 dark:hover:to-gray-700 transition-all duration-300 shadow-lg hover:shadow-xl"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div>
          <div className="flex items-center space-x-3 mb-2">
            <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl">
              <Edit className="h-5 w-5 text-white" />
            </div>
            <h1 className="text-3xl font-bold gradient-text">Edit Expense</h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400 text-lg">Update your expense details</p>
        </div>
      </div>

      {error && (
        <div className="card-gradient max-w-2xl">
          <div className="bg-gradient-to-r from-danger-50 to-red-50 dark:from-danger-900/20 dark:to-red-900/20 border border-danger-200 dark:border-danger-700 text-danger-700 dark:text-danger-400 px-4 py-3 rounded-xl backdrop-blur-sm">
            {error}
          </div>
        </div>
      )}

      <div className="card-gradient max-w-2xl">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="title" className="label">
              <div className="flex items-center space-x-2">
                <FileText className="h-4 w-4 text-primary-500" />
                <span>Expense Title *</span>
              </div>
            </label>
            <input
              id="title"
              name="title"
              type="text"
              required
              className="w-full px-4 py-3 bg-white/90 dark:bg-gray-800/90 border-2 border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-4 focus:ring-primary-500/50 focus:border-transparent backdrop-blur-sm text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 transition-all duration-300 hover:border-gray-300 dark:hover:border-gray-500"
              placeholder="e.g., Grocery shopping, Gas station, Restaurant"
              value={formData.title}
              onChange={handleChange}
            />
          </div>

          <div>
            <label htmlFor="description" className="label">
              <div className="flex items-center space-x-2">
                <FileText className="h-4 w-4 text-primary-500" />
                <span>Description</span>
              </div>
            </label>
            <textarea
              id="description"
              name="description"
              rows="3"
              className="w-full px-4 py-3 bg-white/90 dark:bg-gray-800/90 border-2 border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-4 focus:ring-primary-500/50 focus:border-transparent backdrop-blur-sm text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 transition-all duration-300 hover:border-gray-300 dark:hover:border-gray-500 resize-none"
              placeholder="Add more details about this expense..."
              value={formData.description}
              onChange={handleChange}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="amount" className="label">
                <div className="flex items-center space-x-2">
                  <DollarSign className="h-4 w-4 text-primary-500" />
                  <span>Amount *</span>
                </div>
              </label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-500 dark:text-gray-400 font-semibold">
                  $
                </span>
                <input
                  id="amount"
                  name="amount"
                  type="number"
                  step="0.01"
                  min="0.01"
                  required
                  className="w-full px-4 py-3 pl-8 bg-white/90 dark:bg-gray-800/90 border-2 border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-4 focus:ring-primary-500/50 focus:border-transparent backdrop-blur-sm text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 transition-all duration-300 hover:border-gray-300 dark:hover:border-gray-500"
                  placeholder="0.00"
                  value={formData.amount}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div>
              <label htmlFor="date" className="label">
                <div className="flex items-center space-x-2">
                  <Calendar className="h-4 w-4 text-primary-500" />
                  <span>Date *</span>
                </div>
              </label>
              <input
                id="date"
                name="date"
                type="date"
                required
                className="w-full px-4 py-3 bg-white/90 dark:bg-gray-800/90 border-2 border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-4 focus:ring-primary-500/50 focus:border-transparent backdrop-blur-sm text-gray-900 dark:text-gray-100 transition-all duration-300 hover:border-gray-300 dark:hover:border-gray-500"
                value={formData.date}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="category_id" className="label">
                <div className="flex items-center space-x-2">
                  <Tag className="h-4 w-4 text-primary-500" />
                  <span>Category *</span>
                </div>
              </label>
              <div className="analytics-filter">
                <select
                  id="category_id"
                  name="category_id"
                  required
                  value={formData.category_id}
                  onChange={handleChange}
                >
                  <option value="">Select a category</option>
                  {Array.isArray(categories) && categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                  <Tag className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                </div>
              </div>
            </div>

            <div>
              <label htmlFor="payment_method" className="label">
                <div className="flex items-center space-x-2">
                  <CreditCard className="h-4 w-4 text-primary-500" />
                  <span>Payment Method *</span>
                </div>
              </label>
              <div className="analytics-filter">
                <select
                  id="payment_method"
                  name="payment_method"
                  required
                  value={formData.payment_method}
                  onChange={handleChange}
                >
                  <option value="cash">Cash</option>
                  <option value="card">Card</option>
                  <option value="bank_transfer">Bank Transfer</option>
                  <option value="digital_wallet">Digital Wallet</option>
                  <option value="other">Other</option>
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                  <CreditCard className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                </div>
              </div>
            </div>
          </div>

          <div className="flex justify-end space-x-4 pt-6">
            <button
              type="button"
              onClick={() => navigate('/expenses')}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary flex items-center space-x-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Saving...</span>
                </>
              ) : (
                <>
                  <Save className="h-4 w-4" />
                  <span>Save Changes</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditExpense; 