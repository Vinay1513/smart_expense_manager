from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'phonepe-transactions', views.PhonePeTransactionViewSet, basename='phonepe-transaction')
router.register(r'expenses', views.ExpenseViewSet, basename='expense')

urlpatterns = [
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # PDF upload endpoints
    path('upload-pdf/', views.upload_pdf_transactions, name='upload-pdf-transactions'),
    path('phonepe/upload/', views.upload_phonepe_pdf, name='upload-phonepe-pdf'),
    
    # Analytics endpoints
    path('phonepe/analytics/', views.phonepe_analytics, name='phonepe-analytics'),
    path('phonepe/convert/<int:transaction_id>/', views.convert_to_expense, name='convert-to-expense'),
    path('analytics/summary/', views.expense_summary, name='expense-summary'),
    path('analytics/chart-data/', views.chart_data, name='chart-data'),
] 