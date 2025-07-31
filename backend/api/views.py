from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import os

from .models import UserProfile, Category, Expense, PhonePeTransaction, Transaction
from .serializers import (
    UserSerializer, CategorySerializer, ExpenseSerializer, PhonePeTransactionSerializer,
    TransactionSerializer, ExpenseSummarySerializer, ChartDataSerializer
)
from .permissions import IsOwnerOrReadOnly, IsOwner, IsAuthenticatedOrReadOnly
from .pdf_processor import PhonePePDFProcessor
from .pdf_table_parser import PDFTableParser


class RegisterView(generics.CreateAPIView):
    """User registration view"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Category model"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]  # Allow anyone to view categories

    def get_queryset(self):
        """Return all categories"""
        return Category.objects.all()


class TransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for Transaction model"""
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """Filter transactions by current user"""
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Set the user when creating a transaction"""
        serializer.save(user=self.request.user)


class PhonePeTransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for PhonePeTransaction model"""
    serializer_class = PhonePeTransactionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """Filter transactions by current user"""
        return PhonePeTransaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Set the user when creating a transaction"""
        serializer.save(user=self.request.user)


class ExpenseViewSet(viewsets.ModelViewSet):
    """ViewSet for Expense model"""
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """Filter expenses by current user"""
        queryset = Expense.objects.filter(user=self.request.user)
        # Debug: Check expense 23
        expense23 = queryset.filter(id=23).first()
        if expense23:
            print(f"Expense 23 category: {expense23.category}")
            print(f"Expense 23 category name: {expense23.category.name if expense23.category else 'None'}")
        return queryset

    def perform_create(self, serializer):
        """Set the user when creating an expense"""
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        """Update expense"""
        return serializer.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_pdf_transactions(request):
    """Upload and process PDF file for transaction extraction"""
    try:
        # Debug logging
        print(f"Request method: {request.method}")
        print(f"Request content type: {request.content_type}")
        print(f"Request FILES keys: {list(request.FILES.keys())}")
        print(f"Request data keys: {list(request.data.keys())}")
        
        if 'pdf_file' not in request.FILES:
            print("No pdf_file in request.FILES")
            return Response(
                {'error': 'No PDF file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pdf_file = request.FILES['pdf_file']
        print(f"PDF file name: {pdf_file.name}")
        print(f"PDF file size: {pdf_file.size}")
        print(f"PDF file content type: {pdf_file.content_type}")
        
        # Validate file type
        if not pdf_file.name.lower().endswith('.pdf'):
            return Response(
                {'error': 'File must be a PDF'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process PDF using table parser
        parser = PDFTableParser()
        extracted_transactions = parser.extract_transactions(pdf_file)
        
        print(f"Extracted transactions count: {len(extracted_transactions)}")
        
        if not extracted_transactions:
            return Response(
                {
                    'error': 'No transactions found in the PDF. Please ensure the PDF contains transaction data in a recognizable format.',
                    'suggestion': 'The PDF should contain transaction lines with date, description, and amount information.'
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create categories
        categories = {}
        for transaction in extracted_transactions:
            category_name = categorize_transaction(transaction['description'])
            if category_name not in categories:
                category, created = Category.objects.get_or_create(
                    name=category_name,
                    defaults={
                        'description': f'Category for {category_name}',
                        'color': '#3B82F6',
                        'icon': 'receipt'
                    }
                )
                categories[category_name] = category
        
        # Save transactions to database
        saved_transactions = []
        skipped_transactions = []
        
        for transaction_data in extracted_transactions:
            category_name = categorize_transaction(transaction_data['description'])
            category = categories[category_name]
            
            # Check if transaction already exists
            existing_transaction = Transaction.objects.filter(
                user=request.user,
                date=transaction_data['date'],
                description=transaction_data['description'],
                amount=transaction_data['amount']
            ).first()
            
            if existing_transaction:
                skipped_transactions.append({
                    'transaction_id': transaction_data.get('transaction_id'),
                    'date': transaction_data['date'],
                    'description': transaction_data['description'],
                    'amount': transaction_data['amount'],
                    'reason': 'Duplicate transaction'
                })
                continue
            
            # Create new transaction
            transaction = Transaction.objects.create(
                user=request.user,
                transaction_id=transaction_data.get('transaction_id'),
                date=transaction_data['date'],
                description=transaction_data['description'],
                amount=transaction_data['amount'],
                transaction_type=transaction_data['transaction_type'],
                status=transaction_data['status'],
                payment_method=transaction_data['payment_method'],
                category=category,
                source_file=pdf_file.name,
                raw_data=transaction_data.get('raw_data', {})
            )
            saved_transactions.append(transaction)
        
        # Serialize saved transactions
        serializer = TransactionSerializer(saved_transactions, many=True)
        
        return Response({
            'message': f'Successfully processed {len(saved_transactions)} transactions',
            'transactions': serializer.data,
            'total_extracted': len(extracted_transactions),
            'total_saved': len(saved_transactions),
            'total_skipped': len(skipped_transactions),
            'skipped_transactions': skipped_transactions
        }, status=status.HTTP_201_CREATED)
        
    except ValueError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def categorize_transaction(description: str) -> str:
    """Categorize transaction based on description"""
    description_lower = description.lower()
    
    # Food & Dining
    food_keywords = ['swiggy', 'zomato', 'dominos', 'pizza', 'restaurant', 'cafe', 'food', 'dining', 'hotel']
    if any(keyword in description_lower for keyword in food_keywords):
        return 'Food & Dining'
    
    # Shopping
    shopping_keywords = ['amazon', 'flipkart', 'myntra', 'shop', 'store', 'mall', 'retail', 'purchase']
    if any(keyword in description_lower for keyword in shopping_keywords):
        return 'Shopping'
    
    # Transportation
    transport_keywords = ['uber', 'ola', 'metro', 'bus', 'train', 'fuel', 'petrol', 'diesel', 'cab']
    if any(keyword in description_lower for keyword in transport_keywords):
        return 'Transportation'
    
    # Entertainment
    entertainment_keywords = ['netflix', 'prime', 'hotstar', 'movie', 'cinema', 'theatre', 'game', 'entertainment']
    if any(keyword in description_lower for keyword in entertainment_keywords):
        return 'Entertainment'
    
    # Utilities
    utility_keywords = ['electricity', 'water', 'gas', 'internet', 'mobile', 'phone', 'bill', 'recharge']
    if any(keyword in description_lower for keyword in utility_keywords):
        return 'Utilities'
    
    # Healthcare
    health_keywords = ['pharmacy', 'medical', 'hospital', 'doctor', 'clinic', 'health', 'medicine']
    if any(keyword in description_lower for keyword in health_keywords):
        return 'Healthcare'
    
    # Education
    education_keywords = ['school', 'college', 'university', 'course', 'training', 'education', 'book']
    if any(keyword in description_lower for keyword in education_keywords):
        return 'Education'
    
    # Default category
    return 'Other'


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_phonepe_pdf(request):
    """Upload and process PhonePe PDF file"""
    try:
        # Debug logging
        print(f"Request method: {request.method}")
        print(f"Request content type: {request.content_type}")
        print(f"Request FILES keys: {list(request.FILES.keys())}")
        print(f"Request data keys: {list(request.data.keys())}")
        
        if 'pdf_file' not in request.FILES:
            print("No pdf_file in request.FILES")
            return Response(
                {'error': 'No PDF file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pdf_file = request.FILES['pdf_file']
        print(f"PDF file name: {pdf_file.name}")
        print(f"PDF file size: {pdf_file.size}")
        print(f"PDF file content type: {pdf_file.content_type}")
        
        # Validate file type
        if not pdf_file.name.lower().endswith('.pdf'):
            return Response(
                {'error': 'File must be a PDF'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process PDF using the new table parser
        parser = PDFTableParser()
        extracted_transactions = parser.extract_transactions(pdf_file)
        
        print(f"Extracted transactions count: {len(extracted_transactions)}")
        
        if not extracted_transactions:
            return Response(
                {
                    'error': 'No transactions found in the PDF. Please ensure the PDF contains transaction data in a recognizable format.',
                    'suggestion': 'The PDF should contain transaction lines with date, merchant name, and amount information.'
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create categories
        categories = {}
        for transaction in extracted_transactions:
            category_name = categorize_transaction(transaction['description'])
            if category_name not in categories:
                category, created = Category.objects.get_or_create(
                    name=category_name,
                    defaults={
                        'description': f'Category for {category_name}',
                        'color': '#3B82F6',
                        'icon': 'receipt'
                    }
                )
                categories[category_name] = category
        
        # Save transactions to database as expenses
        saved_transactions = []
        for transaction_data in extracted_transactions:
            category_name = categorize_transaction(transaction_data['description'])
            category = categories[category_name]
            
            # Check if transaction already exists
            existing_transaction = Expense.objects.filter(
                user=request.user,
                date=transaction_data['date'],
                title=transaction_data['description'],
                amount=transaction_data['amount']
            ).first()
            
            if not existing_transaction:
                transaction = Expense.objects.create(
                    user=request.user,
                    title=transaction_data['description'],
                    description=f"PhonePe transaction on {transaction_data['date']}",
                    amount=transaction_data['amount'],
                    category=category,
                    date=transaction_data['date'],
                    payment_method='phonepe'
                )
                saved_transactions.append(transaction)
        
        # Serialize saved transactions
        serializer = ExpenseSerializer(saved_transactions, many=True)
        
        return Response({
            'message': f'Successfully processed {len(saved_transactions)} transactions',
            'transactions': serializer.data,
            'total_extracted': len(extracted_transactions),
            'total_saved': len(saved_transactions)
        }, status=status.HTTP_201_CREATED)
        
    except ValueError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def phonepe_analytics(request):
    """Get analytics for PhonePe transactions"""
    user = request.user
    date_range = request.query_params.get('date_range', 'month')
    
    queryset = PhonePeTransaction.objects.filter(user=user)
    
    # Apply date filtering
    now = timezone.now()
    if date_range == 'month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif date_range == 'quarter':
        quarter_start_month = ((now.month - 1) // 3) * 3 + 1
        start_date = now.replace(month=quarter_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif date_range == 'year':
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    else:
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    
    queryset = queryset.filter(transaction_date__gte=start_date, transaction_date__lte=end_date)
    
    # Calculate summary statistics
    total_amount = queryset.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_count = queryset.count()
    average_amount = queryset.aggregate(avg=Avg('amount'))['avg'] or Decimal('0.00')
    
    # Top merchants
    top_merchants = queryset.values('merchant_name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')[:5]
    
    # Category breakdown
    category_breakdown = []
    categories = Category.objects.filter(phonepe_transactions__in=queryset).distinct()
    
    for category in categories:
        category_total = queryset.filter(category=category).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        category_count = queryset.filter(category=category).count()
        percentage = (category_total / total_amount * 100) if total_amount > 0 else 0
        
        category_breakdown.append({
            'id': category.id,
            'name': category.name,
            'color': category.color,
            'icon': category.icon,
            'total': float(category_total),
            'count': category_count,
            'percentage': round(percentage, 2)
        })
    
    # Daily expenses for line chart
    daily_expenses = queryset.values('transaction_date').annotate(
        total=Sum('amount')
    ).order_by('transaction_date')
    
    daily_data = [
        {
            'date': item['transaction_date'].strftime('%Y-%m-%d'),
            'total': float(item['total'])
        }
        for item in daily_expenses
    ]
    
    analytics_data = {
        'total_amount': float(total_amount),
        'total_count': total_count,
        'average_amount': float(average_amount),
        'top_merchants': list(top_merchants),
        'category_breakdown': category_breakdown,
        'daily_expenses': daily_data
    }
    
    return Response(analytics_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def convert_to_expense(request, transaction_id):
    """Convert a PhonePe transaction to an expense"""
    try:
        transaction = PhonePeTransaction.objects.get(
            id=transaction_id, 
            user=request.user
        )
        
        if transaction.is_processed:
            return Response(
                {'error': 'Transaction already converted to expense'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create expense from transaction
        expense = Expense.objects.create(
            user=request.user,
            title=transaction.merchant_name,
            description=f'PhonePe transaction on {transaction.transaction_date}',
            amount=transaction.amount,
            category=transaction.category or Category.objects.get(name='Other'),
            date=transaction.transaction_date,
            payment_method='phonepe',
            phonepe_transaction=transaction
        )
        
        # Mark transaction as processed
        transaction.is_processed = True
        transaction.save()
        
        serializer = ExpenseSerializer(expense)
        return Response({
            'message': 'Transaction converted to expense successfully',
            'expense': serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except PhonePeTransaction.DoesNotExist:
        return Response(
            {'error': 'Transaction not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def expense_summary(request):
    """Get expense summary for the current user"""
    user = request.user
    print(f"User: {user.username}")
    
    # Get date filters from query parameters
    date_range = request.query_params.get('date_range', 'month')
    
    queryset = Expense.objects.filter(user=user)
    print(f"Total expenses for user: {queryset.count()}")
    
    # Apply date filtering based on the date_range parameter
    now = timezone.now()
    if date_range == 'month':
        # This month
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif date_range == 'quarter':
        # This quarter
        quarter_start_month = ((now.month - 1) // 3) * 3 + 1
        start_date = now.replace(month=quarter_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif date_range == 'year':
        # This year
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    else:
        # Default to this month
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    
    queryset = queryset.filter(date__gte=start_date, date__lte=end_date)
    print(f"Filtered expenses: {queryset.count()}")
    
    # Calculate summary statistics
    total_expenses = queryset.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_count = queryset.count()
    average_amount = queryset.aggregate(avg=Avg('amount'))['avg'] or Decimal('0.00')
    
    # Category breakdown
    category_breakdown = []
    categories = Category.objects.filter(expense__in=queryset).distinct()
    
    for category in categories:
        category_total = queryset.filter(category=category).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        category_count = queryset.filter(category=category).count()
        percentage = (category_total / total_expenses * 100) if total_expenses > 0 else 0
        
        category_breakdown.append({
            'id': category.id,
            'name': category.name,
            'color': category.color,
            'icon': category.icon,
            'total': float(category_total),
            'count': category_count,
            'percentage': round(percentage, 2)
        })
    
    # Monthly data for the last 6 months
    monthly_data = []
    for i in range(6):
        month_date = timezone.now().date() - timedelta(days=30*i)
        month_start = month_date.replace(day=1)
        if i == 0:
            month_end = timezone.now().date()
        else:
            next_month = month_start.replace(day=28) + timedelta(days=4)
            month_end = next_month.replace(day=1) - timedelta(days=1)
        
        month_expenses = queryset.filter(date__gte=month_start, date__lte=month_end)
        month_total = month_expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        monthly_data.append({
            'month': month_start.strftime('%B %Y'),
            'total': float(month_total),
            'count': month_expenses.count()
        })
    
    summary_data = {
        'total_expenses': float(total_expenses),
        'total_count': total_count,
        'average_amount': float(average_amount),
        'category_breakdown': category_breakdown,
        'monthly_data': monthly_data
    }
    
    print(f"Summary data: {summary_data}")
    serializer = ExpenseSummarySerializer(summary_data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chart_data(request):
    """Get chart data for the current user"""
    user = request.user
    chart_type = request.query_params.get('type', 'category')
    date_range = request.query_params.get('date_range', 'month')
    print(f"Chart data request for user: {user.username}, type: {chart_type}, date_range: {date_range}")
    
    # Apply date filtering
    now = timezone.now()
    if date_range == 'month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif date_range == 'quarter':
        quarter_start_month = ((now.month - 1) // 3) * 3 + 1
        start_date = now.replace(month=quarter_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif date_range == 'year':
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    else:
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    
    if chart_type == 'category':
        # Category breakdown chart
        categories = Category.objects.filter(expense__user=user).distinct()
        labels = []
        data = []
        colors = []
        
        for category in categories:
            total = Expense.objects.filter(
                user=user, 
                category=category,
                date__gte=start_date,
                date__lte=end_date
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            if total > 0:
                labels.append(category.name)
                data.append(float(total))
                colors.append(category.color)
        
        chart_data = {
            'labels': labels,
            'datasets': [{
                'data': data,
                'backgroundColor': colors,
                'borderWidth': 2,
                'borderColor': '#ffffff'
            }]
        }
        print(f"Chart data: {chart_data}")
    
    elif chart_type == 'monthly':
        # Monthly trend chart
        months = []
        totals = []
        
        for i in range(6):
            month_date = timezone.now().date() - timedelta(days=30*i)
            month_start = month_date.replace(day=1)
            if i == 0:
                month_end = timezone.now().date()
            else:
                next_month = month_start.replace(day=28) + timedelta(days=4)
                month_end = next_month.replace(day=1) - timedelta(days=1)
            
            total = Expense.objects.filter(
                user=user,
                date__gte=month_start,
                date__lte=month_end
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            months.insert(0, month_start.strftime('%b'))
            totals.insert(0, float(total))
        
        chart_data = {
            'labels': months,
            'datasets': [{
                'label': 'Monthly Expenses',
                'data': totals,
                'backgroundColor': 'rgba(59, 130, 246, 0.2)',
                'borderColor': 'rgba(59, 130, 246, 1)',
                'borderWidth': 2,
                'tension': 0.4
            }]
        }
    
    else:
        return Response({'error': 'Invalid chart type'}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = ChartDataSerializer(chart_data)
    return Response(serializer.data) 