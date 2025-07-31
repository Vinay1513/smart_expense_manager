#!/usr/bin/env python
"""
Setup script for the Smart Expense Manager backend.
This script initializes the database and creates default categories.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expense_manager.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import Category

def create_default_categories():
    """Create default expense categories"""
    default_categories = [
        {
            'name': 'Food & Dining',
            'description': 'Restaurants, groceries, and food delivery',
            'color': '#3B82F6',
            'icon': 'utensils'
        },
        {
            'name': 'Transportation',
            'description': 'Gas, public transport, and vehicle maintenance',
            'color': '#10B981',
            'icon': 'car'
        },
        {
            'name': 'Shopping',
            'description': 'Clothing, electronics, and general shopping',
            'color': '#F59E0B',
            'icon': 'shopping-bag'
        },
        {
            'name': 'Entertainment',
            'description': 'Movies, games, and leisure activities',
            'color': '#8B5CF6',
            'icon': 'gamepad-2'
        },
        {
            'name': 'Healthcare',
            'description': 'Medical expenses, prescriptions, and health services',
            'color': '#EF4444',
            'icon': 'heart'
        },
        {
            'name': 'Utilities',
            'description': 'Electricity, water, internet, and phone bills',
            'color': '#06B6D4',
            'icon': 'zap'
        },
        {
            'name': 'Housing',
            'description': 'Rent, mortgage, and home maintenance',
            'color': '#84CC16',
            'icon': 'home'
        },
        {
            'name': 'Education',
            'description': 'Tuition, books, and educational materials',
            'color': '#F97316',
            'icon': 'graduation-cap'
        },
        {
            'name': 'Travel',
            'description': 'Vacations, business trips, and travel expenses',
            'color': '#EC4899',
            'icon': 'plane'
        },
        {
            'name': 'Other',
            'description': 'Miscellaneous expenses',
            'color': '#6B7280',
            'icon': 'more-horizontal'
        }
    ]
    
    created_count = 0
    for category_data in default_categories:
        category, created = Category.objects.get_or_create(
            name=category_data['name'],
            defaults={
                'description': category_data['description'],
                'color': category_data['color'],
                'icon': category_data['icon']
            }
        )
        if created:
            created_count += 1
            print(f"Created category: {category.name}")
    
    print(f"\nCreated {created_count} new categories.")
    print(f"Total categories: {Category.objects.count()}")

def create_superuser():
    """Create a superuser if none exists"""
    if not User.objects.filter(is_superuser=True).exists():
        print("\nCreating superuser...")
        username = input("Enter username: ")
        email = input("Enter email: ")
        password = input("Enter password: ")
        
        User.objects.create_superuser(username, email, password)
        print("Superuser created successfully!")
    else:
        print("Superuser already exists.")

def main():
    """Main setup function"""
    print("Setting up Smart Expense Manager Backend...")
    
    # Create default categories
    print("\nCreating default categories...")
    create_default_categories()
    
    # Create superuser
    create_superuser()
    
    print("\nSetup completed successfully!")
    print("\nTo start the development server:")
    print("python manage.py runserver")

if __name__ == '__main__':
    main() 