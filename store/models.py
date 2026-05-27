import logging
import re
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

logger = logging.getLogger('museum')


class Position(models.Model):
    """Employee position"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'Positions'
    
    def __str__(self):
        return self.name


class ArtType(models.Model):
    """Type of art"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'Art Types'
        verbose_name = 'Art Type'
    
    def __str__(self):
        return self.name


class Hall(models.Model):
    """Museum hall"""
    number = models.IntegerField(unique=True)
    name = models.CharField(max_length=200)
    floor = models.IntegerField()
    area = models.DecimalField(max_digits=8, decimal_places=2)  # in square meters
    has_water_feature = models.BooleanField(default=False)
    has_heating = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['number']
    
    def __str__(self):
        return f"Hall {self.number} - {self.name}"
    
    def clean(self):
        if self.floor <= 0:
            raise ValidationError('Floor must be positive')
        if self.area <= 0:
            raise ValidationError('Area must be positive')


class Employee(models.Model):
    """Museum employee"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='employees')
    hall = models.ForeignKey(Hall, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    hire_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.last_name} {self.first_name} - {self.position.name}"
    
    def clean(self):
        phone_pattern = r'^\+375\s?\(\d{2}\)\s?\d{3}-\d{2}-\d{2}$'
        if not re.match(phone_pattern, self.phone):
            raise ValidationError('Phone must be in format: +375 (XX) XXX-XX-XX')
        if self.salary < 0:
            raise ValidationError('Salary cannot be negative')


class Exhibit(models.Model):
    """Museum exhibit"""
    name = models.CharField(max_length=200)
    art_type = models.ForeignKey(ArtType, on_delete=models.CASCADE, related_name='exhibits')
    acquisition_date = models.DateField()
    year_created = models.IntegerField(null=True, blank=True)  # Year the exhibit was created
    author = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='exhibits/', null=True, blank=True)
    hall = models.ForeignKey(Hall, on_delete=models.SET_NULL, null=True, related_name='exhibits')
    assigned_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_exhibits')
    is_displayed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def clean(self):
        if self.year_created and self.year_created <= 0:
            raise ValidationError('Year must be positive')


class Exposition(models.Model):
    """Permanent exposition"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name='expositions')
    exhibits = models.ManyToManyField(Exhibit, related_name='expositions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Expositions'
    
    def __str__(self):
        return self.name


class Exhibition(models.Model):
    """Temporary exhibition"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    exhibits = models.ManyToManyField(Exhibit, related_name='exhibitions')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Exhibitions'
    
    def __str__(self):
        return self.name
    
    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError('End date must be after start date')


class Tour(models.Model):
    """Museum tour/excursion"""
    SEASON_CHOICES = [
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('autumn', 'Autumn'),
        ('winter', 'Winter'),
    ]
    
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    group_size = models.IntegerField()
    season = models.CharField(max_length=10, choices=SEASON_CHOICES)
    guide = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='tours')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def clean(self):
        if self.group_size <= 0:
            raise ValidationError('Group size must be positive')
        if self.price < 0:
            raise ValidationError('Price cannot be negative')


class Client(models.Model):
    """Museum visitor/client"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    date_of_birth = models.DateField()
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.last_name} {self.first_name}"
    
    def clean(self):
        phone_pattern = r'^\+375\s?\(\d{2}\)\s?\d{3}-\d{2}-\d{2}$'
        if not re.match(phone_pattern, self.phone):
            raise ValidationError('Phone must be in format: +375 (XX) XXX-XX-XX')
        if self.date_of_birth:
            age = (timezone.now().date() - self.date_of_birth).days // 365
            if age < 18:
                raise ValidationError('Client must be 18 years or older')
    
    @property
    def age(self):
        if self.date_of_birth:
            return (timezone.now().date() - self.date_of_birth).days // 365
        return None


class Ticket(models.Model):
    """Museum ticket"""
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='tickets')
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='tickets', null=True, blank=True)
    purchase_date = models.DateTimeField(auto_now_add=True)
    visit_date = models.DateField()
    ticket_type = models.CharField(max_length=20, choices=[
        ('adult', 'Adult'),
        ('child', 'Child'),
        ('senior', 'Senior'),
        ('student', 'Student'),
    ], default='adult')
    base_price = models.DecimalField(max_digits=8, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=8, decimal_places=2)
    promo_code = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-purchase_date']
    
    def __str__(self):
        return f"Ticket #{self.id} - {self.client}"
    
    def calculate_price(self):
        """Calculate final price based on day of week and ticket type"""
        from decimal import Decimal
        base = Decimal(str(self.base_price))

        # Weekend surcharge
        if self.visit_date and self.visit_date.weekday() >= 5:  # Saturday or Sunday
            base *= Decimal('1.2')

        # Age-based pricing
        if self.ticket_type == 'child':
            base *= Decimal('0.5')
        elif self.ticket_type == 'senior':
            base *= Decimal('0.7')
        elif self.ticket_type == 'student':
            base *= Decimal('0.8')

        # Apply discount
        self.final_price = base * (Decimal('1') - Decimal(str(self.discount)) / Decimal('100'))
        return self.final_price
    
    @property
    def final_amount(self):
        """Alias for final_price for template compatibility"""
        return self.final_price
    
    def clean(self):
        if self.base_price < 0:
            raise ValidationError('Base price cannot be negative')
        if self.discount < 0 or self.discount > 100:
            raise ValidationError('Discount must be between 0 and 100')


class PromoCode(models.Model):
    """Promotional code"""
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-valid_until']
    
    def __str__(self):
        return f"{self.code} ({self.discount_percent}%)"
    
    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.valid_from <= now <= self.valid_until


class Review(models.Model):
    """Museum review"""
    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    text = models.TextField()
    visit_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.client} - {self.rating}/5"

    def clean(self):
        if self.rating and not 1 <= self.rating <= 5:
            raise ValidationError('Rating must be between 1 and 5')


class Vacancy(models.Model):
    """Job vacancy"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField()
    salary_range = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    posted_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-posted_date']
        verbose_name_plural = 'Vacancies'

    def __str__(self):
        return self.title


class CompanyHistory(models.Model):
    """Company history timeline"""
    year = models.IntegerField()
    event = models.TextField()
    photo = models.ImageField(upload_to='history/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['year']
        verbose_name_plural = 'Company History'

    def __str__(self):
        return f"{self.year} - {self.event[:50]}"


class CompanyInfo(models.Model):
    """Company information for About page"""
    name = models.CharField(max_length=200, default='Museum')
    logo = models.ImageField(upload_to='logo/', null=True, blank=True)
    video_url = models.URLField(blank=True, help_text='YouTube or other video URL')
    description = models.TextField()
    address = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Company Info'
        verbose_name_plural = 'Company Info'

    def __str__(self):
        return self.name
