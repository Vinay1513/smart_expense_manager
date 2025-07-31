from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, Category, Expense, PhonePeTransaction, Transaction


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer"""
    class Meta:
        model = Category
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    """Transaction serializer"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    formatted_amount = serializers.SerializerMethodField()
    formatted_date = serializers.DateField(source='date', format='%Y-%m-%d')
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_id', 'date', 'formatted_date', 'description', 
            'amount', 'formatted_amount', 'transaction_type', 'status', 
            'category', 'category_name', 'category_color', 'payment_method', 
            'source_file', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_formatted_amount(self, obj):
        """Return formatted amount with currency symbol"""
        return f"₹{obj.amount:,.2f}"


class ExpenseSerializer(serializers.ModelSerializer):
    """Expense serializer"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    formatted_amount = serializers.SerializerMethodField()
    category_id = serializers.IntegerField(source='category.id', read_only=True)
    category = CategorySerializer(read_only=True)  # Return full category object
    
    class Meta:
        model = Expense
        fields = [
            'id', 'title', 'description', 'amount', 'formatted_amount',
            'category', 'category_id', 'category_name', 'category_color', 'date', 
            'payment_method', 'transaction', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_formatted_amount(self, obj):
        """Return formatted amount with currency symbol"""
        return f"₹{obj.amount:,.2f}"
    
    def update(self, instance, validated_data):
        """Handle category updates"""
        # If category_id is provided, convert it to category
        if 'category_id' in validated_data:
            category_id = validated_data.pop('category_id')
            try:
                from .models import Category
                category = Category.objects.get(id=category_id)
                validated_data['category'] = category
            except Category.DoesNotExist:
                raise serializers.ValidationError({'category_id': 'Category not found'})
        
        # If category is provided as an ID, convert it to category object
        if 'category' in validated_data and isinstance(validated_data['category'], int):
            category_id = validated_data['category']
            try:
                from .models import Category
                category = Category.objects.get(id=category_id)
                validated_data['category'] = category
            except Category.DoesNotExist:
                raise serializers.ValidationError({'category': 'Category not found'})
        
        return super().update(instance, validated_data)


class PhonePeTransactionSerializer(serializers.ModelSerializer):
    """PhonePe transaction serializer"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    formatted_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = PhonePeTransaction
        fields = [
            'id', 'transaction_date', 'merchant_name', 'amount', 'formatted_amount',
            'payment_method', 'category', 'category_name', 'category_color',
            'is_processed', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_formatted_amount(self, obj):
        """Return formatted amount with currency symbol"""
        return f"₹{obj.amount:,.2f}"


class ExpenseSummarySerializer(serializers.Serializer):
    """Expense summary serializer"""
    total_expenses = serializers.FloatField()
    total_count = serializers.IntegerField()
    average_amount = serializers.FloatField()
    category_breakdown = serializers.ListField()
    monthly_data = serializers.ListField()


class ChartDataSerializer(serializers.Serializer):
    """Chart data serializer"""
    labels = serializers.ListField(child=serializers.CharField())
    datasets = serializers.ListField() 