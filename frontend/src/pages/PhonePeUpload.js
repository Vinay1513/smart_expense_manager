import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Upload, FileText, DollarSign, Calendar, Tag, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import api from '../services/api';

const PhonePeUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const navigate = useNavigate();

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setError('');
    } else {
      setError('Please select a valid PDF file');
      setSelectedFile(null);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setError('');
    } else {
      setError('Please drop a valid PDF file');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a PDF file first');
      return;
    }

    setUploading(true);
    setError('');
    setUploadResult(null);

    try {
      const formData = new FormData();
      formData.append('pdf_file', selectedFile);

      const response = await api.post('/phonepe/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setUploadResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to upload PDF file');
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
    }
  };

  const formatAmount = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate(-1)}
            className="btn btn-secondary"
          >
            <ArrowLeft className="h-4 w-4" />
            Back
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              PhonePe PDF Upload
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Upload your PhonePe transaction PDF to automatically extract expenses
            </p>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="card-gradient max-w-2xl">
          <div className="flex items-center space-x-3 text-danger-600 dark:text-danger-400">
            <AlertCircle className="h-5 w-5" />
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Upload Section */}
      <div className="card-gradient max-w-2xl">
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Upload PhonePe PDF
            </h2>
            
            {/* File Upload Area */}
            <div
              className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 ${
                dragActive
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                  : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileSelect}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              
              <div className="space-y-4">
                <Upload className="h-12 w-12 mx-auto text-gray-400 dark:text-gray-500" />
                <div>
                  <p className="text-lg font-medium text-gray-900 dark:text-white">
                    {selectedFile ? selectedFile.name : 'Drop your PhonePe PDF here'}
                  </p>
                  <p className="text-gray-500 dark:text-gray-400 mt-1">
                    {selectedFile 
                      ? 'Click to change file' 
                      : 'or click to browse files'
                    }
                  </p>
                </div>
              </div>
            </div>

            {/* Selected File Info */}
            {selectedFile && (
              <div className="mt-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                <div className="flex items-center space-x-3">
                  <FileText className="h-5 w-5 text-green-600 dark:text-green-400" />
                  <div>
                    <p className="font-medium text-green-900 dark:text-green-100">
                      {selectedFile.name}
                    </p>
                    <p className="text-sm text-green-700 dark:text-green-300">
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={!selectedFile || uploading}
            className="w-full btn btn-primary"
          >
            {uploading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Processing PDF...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4" />
                Upload and Process
              </>
            )}
          </button>
        </div>
      </div>

      {/* Upload Results */}
      {uploadResult && (
        <div className="card-gradient max-w-4xl">
          <div className="space-y-6">
            <div className="flex items-center space-x-3">
              <CheckCircle className="h-6 w-6 text-green-600 dark:text-green-400" />
              <div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Upload Successful!
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  {uploadResult.message}
                </p>
              </div>
            </div>

            {/* Summary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div className="flex items-center space-x-2">
                  <FileText className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                  <span className="font-medium text-blue-900 dark:text-blue-100">
                    Total Extracted
                  </span>
                </div>
                <p className="text-2xl font-bold text-blue-900 dark:text-blue-100 mt-1">
                  {uploadResult.total_extracted}
                </p>
              </div>
              
              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400" />
                  <span className="font-medium text-green-900 dark:text-green-100">
                    New Transactions
                  </span>
                </div>
                <p className="text-2xl font-bold text-green-900 dark:text-green-100 mt-1">
                  {uploadResult.total_saved}
                </p>
              </div>
              
              <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <div className="flex items-center space-x-2">
                  <DollarSign className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                  <span className="font-medium text-purple-900 dark:text-purple-100">
                    Total Amount
                  </span>
                </div>
                <p className="text-2xl font-bold text-purple-900 dark:text-purple-100 mt-1">
                  {formatAmount(
                    uploadResult.transactions.reduce((sum, t) => sum + parseFloat(t.amount), 0)
                  )}
                </p>
              </div>
            </div>

            {/* Transactions List */}
            {uploadResult.transactions.length > 0 && (
              <div>
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Extracted Transactions
                </h4>
                <div className="space-y-3">
                  {uploadResult.transactions.map((transaction, index) => (
                    <div
                      key={index}
                      className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3">
                            <div className="flex items-center space-x-2">
                              <Tag className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                              <span className="text-sm text-gray-500 dark:text-gray-400">
                                {transaction.category?.name || 'Other'}
                              </span>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Calendar className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                              <span className="text-sm text-gray-500 dark:text-gray-400">
                                {formatDate(transaction.transaction_date)}
                              </span>
                            </div>
                          </div>
                          <p className="font-medium text-gray-900 dark:text-white mt-1">
                            {transaction.merchant_name}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-lg font-bold text-gray-900 dark:text-white">
                            {formatAmount(transaction.amount)}
                          </p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            {transaction.payment_method}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex space-x-4">
              <button
                onClick={() => {
                  setSelectedFile(null);
                  setUploadResult(null);
                  setError('');
                }}
                className="btn btn-secondary"
              >
                Upload Another PDF
              </button>
              <button
                onClick={() => navigate('/expenses')}
                className="btn btn-primary"
              >
                View All Expenses
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PhonePeUpload; 