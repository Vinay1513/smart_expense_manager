import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Eye, EyeOff, UserPlus, Sparkles, User, Mail, Lock, UserCheck } from 'lucide-react';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    password2: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showPassword2, setShowPassword2] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (formData.password !== formData.password2) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    const result = await register(formData);
    
    if (result.success) {
      navigate('/dashboard');
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 via-white to-gray-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto h-16 w-16 flex items-center justify-center rounded-2xl bg-gradient-to-r from-primary-500 to-purple-500 shadow-xl">
            <Sparkles className="h-8 w-8 text-white" />
          </div>
          <h2 className="mt-6 text-center text-3xl font-bold gradient-text">
            Join Expenso
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
            Create your account to start managing expenses
          </p>
          <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
            Already have an account?{' '}
            <Link
              to="/login"
              className="font-semibold text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300 transition-colors duration-200"
            >
              Sign in here
            </Link>
          </p>
        </div>
        
        {/* Form */}
        <div className="card-gradient">
          <form className="space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="bg-gradient-to-r from-danger-50 to-red-50 dark:from-danger-900/20 dark:to-red-900/20 border border-danger-200 dark:border-danger-700 text-danger-700 dark:text-danger-400 px-4 py-3 rounded-xl backdrop-blur-sm">
                {error}
              </div>
            )}
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="first_name" className="label">
                    <div className="flex items-center space-x-2">
                      <User className="h-4 w-4 text-primary-500" />
                      <span>First Name</span>
                    </div>
                  </label>
                  <input
                    id="first_name"
                    name="first_name"
                    type="text"
                    required
                    className="input-gradient"
                    placeholder="John"
                    value={formData.first_name}
                    onChange={handleChange}
                  />
                </div>
                <div>
                  <label htmlFor="last_name" className="label">
                    <div className="flex items-center space-x-2">
                      <User className="h-4 w-4 text-primary-500" />
                      <span>Last Name</span>
                    </div>
                  </label>
                  <input
                    id="last_name"
                    name="last_name"
                    type="text"
                    required
                    className="input-gradient"
                    placeholder="Doe"
                    value={formData.last_name}
                    onChange={handleChange}
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="username" className="label">
                  <div className="flex items-center space-x-2">
                    <UserCheck className="h-4 w-4 text-primary-500" />
                    <span>Username</span>
                  </div>
                </label>
                <input
                  id="username"
                  name="username"
                  type="text"
                  required
                  className="input-gradient"
                  placeholder="johndoe"
                  value={formData.username}
                  onChange={handleChange}
                />
              </div>
              
              <div>
                <label htmlFor="email" className="label">
                  <div className="flex items-center space-x-2">
                    <Mail className="h-4 w-4 text-primary-500" />
                    <span>Email</span>
                  </div>
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  className="input-gradient"
                  placeholder="john@example.com"
                  value={formData.email}
                  onChange={handleChange}
                />
              </div>
              
              <div>
                <label htmlFor="password" className="label">
                  <div className="flex items-center space-x-2">
                    <Lock className="h-4 w-4 text-primary-500" />
                    <span>Password</span>
                  </div>
                </label>
                <div className="relative">
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    required
                    className="input-gradient pr-12"
                    placeholder="Enter your password"
                    value={formData.password}
                    onChange={handleChange}
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors duration-200"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5" />
                    ) : (
                      <Eye className="h-5 w-5" />
                    )}
                  </button>
                </div>
              </div>
              
              <div>
                <label htmlFor="password2" className="label">
                  <div className="flex items-center space-x-2">
                    <Lock className="h-4 w-4 text-primary-500" />
                    <span>Confirm Password</span>
                  </div>
                </label>
                <div className="relative">
                  <input
                    id="password2"
                    name="password2"
                    type={showPassword2 ? 'text' : 'password'}
                    required
                    className="input-gradient pr-12"
                    placeholder="Confirm your password"
                    value={formData.password2}
                    onChange={handleChange}
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors duration-200"
                    onClick={() => setShowPassword2(!showPassword2)}
                  >
                    {showPassword2 ? (
                      <EyeOff className="h-5 w-5" />
                    ) : (
                      <Eye className="h-5 w-5" />
                    )}
                  </button>
                </div>
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="btn btn-primary w-full flex justify-center items-center space-x-2"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Creating account...</span>
                  </>
                ) : (
                  <>
                    <UserPlus className="h-5 w-5" />
                    <span>Create Account</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Footer */}
        <div className="text-center">
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Join thousands of users managing their expenses with Expenso
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register; 