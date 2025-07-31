import React from 'react';
import { Sparkles } from 'lucide-react';

const LoadingSpinner = ({ size = 'default', text = 'Loading...' }) => {
  const sizes = {
    small: 'h-6 w-6',
    default: 'h-12 w-12',
    large: 'h-16 w-16',
    xlarge: 'h-20 w-20'
  };

  return (
    <div className="flex flex-col items-center justify-center space-y-4">
      <div className="relative">
        <div className={`${sizes[size]} animate-spin rounded-full border-4 border-gray-200 dark:border-gray-700`}></div>
        <div className={`${sizes[size]} animate-spin rounded-full border-4 border-transparent border-t-primary-500 absolute top-0 left-0`}></div>
        <div className="absolute inset-0 flex items-center justify-center">
          <Sparkles className="h-6 w-6 text-primary-500 animate-pulse" />
        </div>
      </div>
      {text && (
        <p className="text-gray-600 dark:text-gray-400 font-medium">{text}</p>
      )}
    </div>
  );
};

export default LoadingSpinner; 