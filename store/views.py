import logging
import json
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Avg, F, Q
from django.db.models.functions import ExtractMonth, ExtractQuarter, ExtractYear
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta, date
from .models import (
    Position, ArtType, Hall, Employee, Exhibit, Exposition,
    Exhibition, Tour, Client, Ticket, PromoCode, Review
)
from .forms import (
    RegistrationForm, LoginForm, ClientForm, TicketForm,
    ReviewForm, PromoCodeForm
)

logger = logging.getLogger('museum')


# External API helpers
def get_currency_rates():
    """Get currency rates from external API"""
    try:
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('rates', {})
    except Exception as e:
        logger.error(f'Error fetching currency rates: {e}')
    return {'BYN': 3.26, 'EUR': 0.92, 'RUB': 90.5}


def get_random_art_fact():
    """Get random art fact (simulated)"""
    facts = [
        "The Mona Lisa has no eyebrows.",
        "Van Gogh only sold one painting in his lifetime.",
        "The Louvre is the world's largest art museum.",
        "Picasso painted 'Guernica' in response to the Spanish Civil War.",
        "The Scream by Edvard Munch has been stolen twice.",
    ]
    import random
    return random.choice(facts)


# Main views
def home(request):
    """Home page - shows latest exhibit"""
    latest_exhibit = Exhibit.objects.select_related('art_type', 'hall').first()
    currency_rates = get_currency_rates()
    art_fact = get_random_art_fact()
    
    context = {
        'latest_exhibit': latest_exhibit,
        'currency_rates': currency_rates,
        'art_fact': art_fact,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    logger.info('Home page accessed')
    return render(request, 'museum/home.html', context)


def about(request):
    """About museum page"""
    from .models import CompanyInfo, CompanyHistory
    company_info = CompanyInfo.objects.first()
    history = CompanyHistory.objects.all()
    context = {
        'company_info': company_info,
        'history': history,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'museum/about.html', context)


def news(request):
    """News page - shows current exhibitions"""
    exhibitions = Exhibition.objects.filter(
        is_active=True,
        end_date__gte=timezone.now().date()
    )[:10]
    context = {
        'exhibitions': exhibitions,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'museum/news.html', context)


def glossary(request):
    """Glossary/FAQ page - art types"""
    art_types = ArtType.objects.annotate(exhibit_count=Count('exhibits'))
    context = {
        'art_types': art_types,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'museum/glossary.html', context)


def contacts(request):
    """Contacts page - shows employees"""
    employees = Employee.objects.select_related('position', 'hall').all()
    context = {
        'employees': employees,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'museum/contacts.html', context)


def privacy(request):
    """Privacy policy page"""
    return render(request, 'museum/privacy.html')


def vacancies(request):
    """Vacancies page"""
    from .models import Vacancy
    vacancies = Vacancy.objects.filter(is_active=True)
    context = {
        'vacancies': vacancies,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'museum/vacancies.html', context)


# Hall and Exhibit views
def hall_list(request):
    """Hall list"""
    halls = Hall.objects.annotate(
        exhibit_count=Count('exhibits'),
        employee_count=Count('employees')
    )
    context = {
        'halls': halls,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'museum/hall_list.html', context)


def exhibit_list(request):
    """Exhibit list with search, sorting, and filtering"""
    exhibits = Exhibit.objects.select_related('art_type', 'hall', 'assigned_employee').all()
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        exhibits = exhibits.filter(
            Q(name__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by art type
    art_type_id = request.GET.get('art_type')
    if art_type_id:
        exhibits = exhibits.filter(art_type_id=art_type_id)
    
    # Filter by hall
    hall_id = request.GET.get('hall')
    if hall_id:
        exhibits = exhibits.filter(hall_id=hall_id)
    
    # Filter by acquisition date (last 6 months)
    recent = request.GET.get('recent')
    if recent:
        six_months_ago = timezone.now().date() - timedelta(days=180)
        exhibits = exhibits.filter(acquisition_date__gte=six_months_ago)
    
    # Filter by employee floor
    floor = request.GET.get('floor')
    if floor:
        exhibits = exhibits.filter(hall__floor=floor)
    
    # Sort
    sort_by = request.GET.get('sort', 'name')
    if sort_by in ['name', 'acquisition_date', 'year_created']:
        exhibits = exhibits.order_by(sort_by)
    elif sort_by == '-acquisition_date':
        exhibits = exhibits.order_by('-acquisition_date')
    
    # Pagination
    paginator = Paginator(exhibits, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    art_types = ArtType.objects.all()
    halls = Hall.objects.all()
    
    context = {
        'page_obj': page_obj,
        'art_types': art_types,
        'halls': halls,
        'search_query': search_query,
        'current_sort': sort_by,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'museum/exhibit_list.html', context)


def exhibit_detail(request, pk):
    """Exhibit detail page"""
    exhibit = get_object_or_404(
        Exhibit.objects.select_related('art_type', 'hall', 'assigned_employee'), 
        pk=pk
    )
    context = {
        'exhibit': exhibit,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'museum/exhibit_detail.html', context)


# Tour views
def tour_list(request):
    """Tour list"""
    tours = Tour.objects.select_related('guide').all()
    
    # Filter by season
    season = request.GET.get('season')
    if season:
        tours = tours.filter(season=season)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    if date_from:
        tours = tours.filter(date__date__gte=date_from)
    
    paginator = Paginator(tours, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'seasons': Tour.SEASON_CHOICES,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'museum/tour_list.html', context)


def tour_detail(request, pk):
    """Tour detail page"""
    tour = get_object_or_404(Tour.objects.select_related('guide'), pk=pk)
    tickets = tour.tickets.all()[:10]
    context = {
        'tour': tour,
        'tickets': tickets,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'museum/tour_detail.html', context)


# Statistics views
@login_required
def statistics(request):
    """Statistics dashboard"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    # Basic statistics
    total_exhibits = Exhibit.objects.count()
    total_halls = Hall.objects.count()
    total_employees = Employee.objects.count()
    total_tours = Tour.objects.count()
    total_tickets = Ticket.objects.count()
    total_revenue = Ticket.objects.aggregate(total=Sum('final_price'))['total'] or 0
    
    # Exhibits by art type
    exhibits_by_type = ArtType.objects.annotate(
        exhibit_count=Count('exhibits')
    ).order_by('-exhibit_count')
    
    # Exhibits by hall
    exhibits_by_hall = Hall.objects.annotate(
        exhibit_count=Count('exhibits')
    ).order_by('-exhibit_count')
    
    # Tours by season
    tours_by_season = Tour.objects.values('season').annotate(
        tour_count=Count('id'),
        total_participants=Sum('group_size')
    ).order_by('season')
    
    # Tickets by month
    tickets_by_month = Ticket.objects.annotate(
        year=ExtractYear('purchase_date'),
        month=ExtractMonth('purchase_date')
    ).values('year', 'month').annotate(
        ticket_count=Count('id'),
        total_revenue=Sum('final_price')
    ).order_by('-year', '-month')[:12]
    
    # Employees by floor
    employees_by_floor = Employee.objects.filter(hall__isnull=False).annotate(
        floor=F('hall__floor')
    ).values('floor').annotate(
        employee_count=Count('id')
    ).order_by('floor')
    
    context = {
        'total_exhibits': total_exhibits,
        'total_halls': total_halls,
        'total_employees': total_employees,
        'total_tours': total_tours,
        'total_tickets': total_tickets,
        'total_revenue': total_revenue,
        'exhibits_by_type': exhibits_by_type,
        'exhibits_by_hall': exhibits_by_hall,
        'tours_by_season': tours_by_season,
        'tickets_by_month': list(tickets_by_month),
        'employees_by_floor': employees_by_floor,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'museum/statistics.html', context)


# Employee views
@login_required
def employee_dashboard(request):
    """Employee dashboard - shows assigned exhibits and tours"""
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, 'You are not registered as an employee')
        return redirect('home')
    
    assigned_exhibits = employee.assigned_exhibits.all()
    guided_tours = employee.tours.all()
    
    context = {
        'employee': employee,
        'assigned_exhibits': assigned_exhibits,
        'guided_tours': guided_tours,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'museum/employee_dashboard.html', context)


# Ticket views
@login_required
def ticket_create(request):
    """Create new ticket"""
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            try:
                ticket.client = request.user.client
                ticket.calculate_price()
                ticket.save()
                logger.info(f'Ticket created: #{ticket.id} by {request.user.username}')
                messages.success(request, 'Ticket purchased successfully')
                return redirect('ticket_detail', pk=ticket.pk)
            except Client.DoesNotExist:
                messages.error(request, 'You need to complete your profile first')
                return redirect('profile')
    else:
        form = TicketForm()
    
    return render(request, 'museum/ticket_form.html', {'form': form})


def ticket_detail(request, pk):
    """Ticket detail page"""
    ticket = get_object_or_404(Ticket.objects.select_related('client', 'tour'), pk=pk)
    context = {
        'ticket': ticket,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'museum/ticket_detail.html', context)


@login_required
def ticket_list(request):
    """Ticket list for current user or all tickets for staff"""
    if request.user.is_staff:
        tickets = Ticket.objects.select_related('client', 'tour').all()
    else:
        try:
            client = request.user.client
            tickets = Ticket.objects.filter(client=client)
        except Client.DoesNotExist:
            tickets = Ticket.objects.none()
    
    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'museum/ticket_list.html', context)


# Review views
@login_required
def review_create(request):
    """Create new review"""
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            try:
                review.client = request.user.client
                review.save()
                logger.info(f'Review created by {request.user.username}')
                messages.success(request, 'Review submitted successfully')
                return redirect('home')
            except Client.DoesNotExist:
                messages.error(request, 'You need to complete your profile first')
                return redirect('profile')
    else:
        form = ReviewForm()
    
    return render(request, 'museum/review_form.html', {'form': form})


# API views
def api_currency_rates(request):
    """API endpoint for currency rates"""
    rates = get_currency_rates()
    return JsonResponse({'rates': rates})


def api_statistics(request):
    """API endpoint for statistics"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    stats = {
        'total_exhibits': Exhibit.objects.count(),
        'total_halls': Hall.objects.count(),
        'total_tours': Tour.objects.count(),
        'total_revenue': float(Ticket.objects.aggregate(total=Sum('final_price'))['total'] or 0),
    }
    return JsonResponse(stats)


# Authentication views
def register(request):
    """User registration"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Client.objects.create(
                user=user,
                first_name=user.first_name,
                last_name=user.last_name,
                phone=form.cleaned_data['phone'],
                email=user.email,
                date_of_birth=form.cleaned_data['date_of_birth'],
            )
            login(request, user)
            logger.info(f'New user registered: {user.username}')
            messages.success(request, 'Registration successful')
            return redirect('home')
    else:
        form = RegistrationForm()
    
    return render(request, 'museum/register.html', {'form': form})


def user_login(request):
    """User login"""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info(f'User logged in: {user.username}')
            messages.success(request, 'Login successful')
            return redirect('home')
    else:
        form = LoginForm()
    
    return render(request, 'museum/login.html', {'form': form})


@login_required
def user_logout(request):
    """User logout"""
    logout(request)
    logger.info('User logged out')
    messages.info(request, 'You have been logged out')
    return redirect('home')


@login_required
def profile(request):
    """User profile"""
    try:
        client = request.user.client
    except Client.DoesNotExist:
        client = None
    
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profile')
    else:
        form = ClientForm(instance=client)
    
    return render(request, 'museum/profile.html', {'form': form, 'client': client})


# Calendar view
def calendar(request):
    """Text calendar view"""
    from calendar import TextCalendar
    now = timezone.now()
    cal = TextCalendar()
    calendar_text = cal.formatmonth(now.year, now.month)

    context = {
        'calendar_text': calendar_text,
        'current_month': now.strftime('%B %Y'),
        'current_time_utc': now,
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'museum/calendar.html', context)
