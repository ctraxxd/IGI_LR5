import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from .models import Exhibit, Hall, ArtType, Employee, Client, Ticket, Review, PromoCode, Tour


class RegistrationForm(UserCreationForm):
    """User registration form"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=20, required=True)
    date_of_birth = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        phone_pattern = r'^\+375\s?\(\d{2}\)\s?\d{3}-\d{2}-\d{2}$'
        if not re.match(phone_pattern, phone):
            raise ValidationError('Phone must be in format: +375 (XX) XXX-XX-XX')
        return phone

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        age = (timezone.now().date() - dob).days // 365
        if age < 18:
            raise ValidationError('You must be 18 years or older to register')
        return dob


class LoginForm(AuthenticationForm):
    """User login form"""
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class ClientForm(forms.ModelForm):
    """Client form"""
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'middle_name', 'phone', 'email', 'date_of_birth', 'address']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+375 (XX) XXX-XX-XX'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        phone_pattern = r'^\+375\s?\(\d{2}\)\s?\d{3}-\d{2}-\d{2}$'
        if not re.match(phone_pattern, phone):
            raise ValidationError('Phone must be in format: +375 (XX) XXX-XX-XX')
        return phone

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        age = (timezone.now().date() - dob).days // 365
        if age < 18:
            raise ValidationError('Client must be 18 years or older')
        return dob


class TicketForm(forms.ModelForm):
    """Ticket purchase form"""
    class Meta:
        model = Ticket
        fields = ['tour', 'visit_date', 'ticket_type', 'base_price', 'discount', 'promo_code']
        widgets = {
            'tour': forms.Select(attrs={'class': 'form-control'}),
            'visit_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ticket_type': forms.Select(attrs={'class': 'form-control'}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'max': '100'}),
            'promo_code': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_visit_date(self):
        visit_date = self.cleaned_data.get('visit_date')
        if visit_date and visit_date < timezone.now().date():
            raise ValidationError('Visit date cannot be in the past')
        return visit_date

    def clean_discount(self):
        discount = self.cleaned_data.get('discount')
        if discount < 0 or discount > 100:
            raise ValidationError('Discount must be between 0 and 100')
        return discount


class ReviewForm(forms.ModelForm):
    """Review form"""
    class Meta:
        model = Review
        fields = ['rating', 'text', 'visit_date']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}, choices=Review.RATING_CHOICES),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'visit_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not 1 <= rating <= 5:
            raise ValidationError('Rating must be between 1 and 5')
        return rating


class PromoCodeForm(forms.ModelForm):
    """Promo code form"""
    class Meta:
        model = PromoCode
        fields = ['code', 'description', 'discount_percent', 'min_purchase', 'is_active', 'valid_from', 'valid_until']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'discount_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'min_purchase': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'valid_from': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'valid_until': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def clean_valid_until(self):
        valid_until = self.cleaned_data.get('valid_until')
        valid_from = self.cleaned_data.get('valid_from')
        if valid_from and valid_until and valid_until <= valid_from:
            raise ValidationError('Valid until must be after valid from')
        return valid_until


class ExhibitForm(forms.ModelForm):
    """Exhibit form for staff"""
    class Meta:
        model = Exhibit
        fields = ['name', 'art_type', 'acquisition_date', 'year_created', 'author', 'description', 'hall', 'assigned_employee', 'is_displayed']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'art_type': forms.Select(attrs={'class': 'form-control'}),
            'acquisition_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'year_created': forms.NumberInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'hall': forms.Select(attrs={'class': 'form-control'}),
            'assigned_employee': forms.Select(attrs={'class': 'form-control'}),
            'is_displayed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TourForm(forms.ModelForm):
    """Tour form for staff"""
    class Meta:
        model = Tour
        fields = ['code', 'name', 'description', 'date', 'group_size', 'season', 'guide', 'price']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'group_size': forms.NumberInput(attrs={'class': 'form-control'}),
            'season': forms.Select(attrs={'class': 'form-control'}),
            'guide': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
