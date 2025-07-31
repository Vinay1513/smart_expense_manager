from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Category, Expense


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'color', 'icon', 'expense_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['expense_count', 'created_at', 'updated_at']
    
    def expense_count(self, obj):
        return obj.expenses.count()
    expense_count.short_description = 'Number of Expenses'


class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'amount', 'category', 'date', 'payment_method', 'created_at']
    list_filter = ['category', 'payment_method', 'date', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'category')


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register models
admin.site.register(Category, CategoryAdmin)
admin.site.register(Expense, ExpenseAdmin) 