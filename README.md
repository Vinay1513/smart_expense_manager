# Smart Expense Manager

A full-stack web application for managing personal expenses with a clean, modern interface.

## 🚀 Features

- **User Authentication**: JWT-based login/register system
- **Expense Management**: Add, edit, delete expenses with categories
- **Dashboard**: Visual summaries with charts and analytics
- **Filtering**: Filter expenses by date, category, and amount
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Export**: Export expense data to CSV (optional)

## 🛠️ Tech Stack

### Backend
- **Django 4.2+** with Django REST Framework
- **SimpleJWT** for authentication
- **SQLite** (development) / PostgreSQL (production)
- **Django CORS Headers** for cross-origin requests

### Frontend
- **React 18+** with functional components and hooks
- **TailwindCSS** for styling
- **Axios** for API communication
- **Recharts** for data visualization
- **React Router** for navigation

## 📁 Project Structure

```
Expenso/
├── backend/                 # Django backend
│   ├── expense_manager/     # Django project
│   ├── api/                # Django app
│   ├── requirements.txt     # Python dependencies
│   └── manage.py
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── context/       # React context
│   │   ├── services/      # API services
│   │   └── utils/         # Utility functions
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## 🚀 Quick Start

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server:**
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm start
   ```

## 🌐 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Refresh JWT token

### Expenses
- `GET /api/expenses/` - List all expenses
- `POST /api/expenses/` - Create new expense
- `GET /api/expenses/{id}/` - Get specific expense
- `PUT /api/expenses/{id}/` - Update expense
- `DELETE /api/expenses/{id}/` - Delete expense

### Categories
- `GET /api/categories/` - List all categories
- `POST /api/categories/` - Create new category

### Analytics
- `GET /api/analytics/summary/` - Get expense summary
- `GET /api/analytics/chart-data/` - Get chart data

## 🔧 Environment Variables

### Backend (.env)
```
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000/api
```

## 📊 Features Overview

### Dashboard
- Monthly expense overview
- Category-wise breakdown
- Recent transactions
- Interactive charts

### Expense Management
- Add new expenses with categories
- Edit existing expenses
- Delete expenses
- Filter and search functionality

### User Experience
- Clean, modern UI inspired by Splitwise
- Responsive design for all devices
- Loading states and error handling
- Intuitive navigation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For support, please open an issue in the repository or contact the development team. 