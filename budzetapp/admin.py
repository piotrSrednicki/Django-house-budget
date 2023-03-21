from django.contrib import admin
from django.contrib.auth.models import User
from .models import Transaction, Category
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms



class TransactionAdmin(admin.ModelAdmin):
    list_filter = [
        "type",
        "category",
        "trans_date",
        "user"
    ]
    list_display = ('user', 'type', 'sum', 'trans_date', 'category')
    ordering = ('trans_date',)

admin.site.register(Transaction, TransactionAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
admin.site.register(Category,CategoryAdmin)


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()
    
    class Meta:
        model = User
        fields = ('password', 'email', 'is_staff')


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('is_staff',)


class UsersAdmin(UserAdmin):
    form = UserChangeForm
    list_display = ['username', 'email', 'is_staff']
    fieldsets = (
        (None, {'fields': ('username', 'password','email')}),)
    ordering = ('username',)

admin.site.unregister(User)
admin.site.register(User, UsersAdmin)
admin.site.unregister(Group)
