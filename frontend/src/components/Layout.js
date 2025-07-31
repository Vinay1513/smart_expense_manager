import React, { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import {
  Home,
  Receipt,
  Plus,
  BarChart3,
  LogOut,
  Menu,
  X,
  User,
  Sun,
  Moon,
  Sparkles,
  Upload,
} from 'lucide-react';

const Layout = () => {
  const { user, logout } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: Home, gradient: 'from-blue-500 to-cyan-500' },
    { name: 'Expenses', href: '/expenses', icon: Receipt, gradient: 'from-green-500 to-emerald-500' },
    { name: 'Add Expense', href: '/expenses/add', icon: Plus, gradient: 'from-purple-500 to-pink-500' },
    { name: 'PhonePe Upload', href: '/phonepe-upload', icon: Upload, gradient: 'from-indigo-500 to-purple-500' },
    { name: 'Analytics', href: '/analytics', icon: BarChart3, gradient: 'from-orange-500 to-red-500' },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 transition-all duration-300">
      {/* Mobile sidebar */}
      <div className={`fixed inset-0 z-50 lg:hidden ${sidebarOpen ? 'block' : 'hidden'}`}>
        <div className="fixed inset-0 bg-black/20 backdrop-blur-sm dark:bg-black/40" onClick={() => setSidebarOpen(false)} />
        <div className="fixed inset-y-0 left-0 flex w-80 flex-col bg-white/90 dark:bg-gray-800/90 backdrop-blur-md border-r border-white/20 dark:border-gray-700/50 shadow-2xl">
          <div className="flex h-20 items-center justify-between px-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-r from-primary-500 to-purple-500 rounded-xl">
                <Sparkles className="h-6 w-6 text-white" />
              </div>
              <h1 className="text-xl font-bold gradient-text">Expenso</h1>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="p-2 rounded-xl bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 transition-all duration-300"
            >
              <X size={20} />
            </button>
          </div>
          <nav className="flex-1 space-y-2 px-4 py-6">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`sidebar-item ${isActive ? 'active' : ''}`}
                  onClick={() => setSidebarOpen(false)}
                >
                  <div className={`p-2 rounded-xl ${isActive ? `bg-gradient-to-r ${item.gradient}` : 'bg-gray-100 dark:bg-gray-700'}`}>
                    <item.icon size={20} className={isActive ? 'text-white' : 'text-gray-600 dark:text-gray-300'} />
                  </div>
                  <span className="ml-3 font-medium">{item.name}</span>
                </Link>
              );
            })}
          </nav>
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between p-3 bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 rounded-xl">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-gradient-to-r from-primary-500 to-purple-500 rounded-lg">
                  <User className="h-4 w-4 text-white" />
                </div>
                <span className="text-sm font-medium text-gray-700 dark:text-gray-200">
                  {user?.username || 'User'}
                </span>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 text-gray-400 hover:text-gray-600 dark:text-gray-300 dark:hover:text-gray-100 transition-colors duration-200"
              >
                <LogOut size={16} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-80 lg:flex-col">
        <div className="flex flex-col flex-grow bg-white/90 dark:bg-gray-800/90 backdrop-blur-md border-r border-white/20 dark:border-gray-700/50 shadow-2xl">
          <div className="flex h-20 items-center px-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-r from-primary-500 to-purple-500 rounded-xl">
                <Sparkles className="h-6 w-6 text-white" />
              </div>
              <h1 className="text-xl font-bold gradient-text">Expenso</h1>
            </div>
          </div>
          <nav className="flex-1 space-y-2 px-4 py-6">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`sidebar-item ${isActive ? 'active' : ''}`}
                >
                  <div className={`p-2 rounded-xl ${isActive ? `bg-gradient-to-r ${item.gradient}` : 'bg-gray-100 dark:bg-gray-700'}`}>
                    <item.icon size={20} className={isActive ? 'text-white' : 'text-gray-600 dark:text-gray-300'} />
                  </div>
                  <span className="ml-3 font-medium">{item.name}</span>
                </Link>
              );
            })}
          </nav>
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between p-3 bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 rounded-xl">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-gradient-to-r from-primary-500 to-purple-500 rounded-lg">
                  <User className="h-4 w-4 text-white" />
                </div>
                <span className="text-sm font-medium text-gray-700 dark:text-gray-200">
                  {user?.username || 'User'}
                </span>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 text-gray-400 hover:text-gray-600 dark:text-gray-300 dark:hover:text-gray-100 transition-colors duration-200"
              >
                <LogOut size={16} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-80">
        {/* Top header */}
        <div className="sticky top-0 z-40 bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border-b border-white/20 dark:border-gray-700/50">
          <div className="flex h-20 items-center justify-between px-6 sm:px-8 lg:px-10">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-3 rounded-xl bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 transition-all duration-300"
            >
              <Menu size={20} />
            </button>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={toggleTheme}
                className="p-3 rounded-xl bg-gradient-to-r from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-800 text-gray-600 dark:text-gray-300 hover:from-gray-200 hover:to-gray-300 dark:hover:from-gray-600 dark:hover:to-gray-700 transition-all duration-300 shadow-lg hover:shadow-xl"
                title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                {isDark ? <Sun size={20} /> : <Moon size={20} />}
              </button>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="p-6 sm:p-8 lg:p-10">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout; 