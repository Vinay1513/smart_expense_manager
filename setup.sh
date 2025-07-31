#!/bin/bash

# Smart Expense Manager Setup Script
# This script sets up both the Django backend and React frontend

set -e

echo "🚀 Setting up Smart Expense Manager..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 16+ and try again."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm and try again."
    exit 1
fi

print_status "Checking system requirements..."
print_success "All system requirements met!"

# Backend Setup
print_status "Setting up Django backend..."

cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file..."
    cp env.example .env
    print_warning "Please update the .env file with your configuration."
fi

# Run Django migrations
print_status "Running Django migrations..."
python manage.py makemigrations
python manage.py migrate

# Create default categories and superuser
print_status "Setting up default data..."
python setup.py

print_success "Backend setup completed!"

# Frontend Setup
print_status "Setting up React frontend..."

cd ../frontend

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
npm install

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file..."
    cp env.example .env
fi

print_success "Frontend setup completed!"

# Return to root directory
cd ..

print_success "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Start the Django backend:"
echo "   cd backend"
echo "   source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "   python manage.py runserver"
echo ""
echo "2. Start the React frontend (in a new terminal):"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "3. Open your browser and navigate to:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000/api"
echo "   Django Admin: http://localhost:8000/admin"
echo ""
echo "📚 Documentation:"
echo "   - Backend API docs: http://localhost:8000/api/"
echo "   - Read the README.md file for more information"
echo ""
print_warning "Remember to update the .env files with your specific configuration!" 