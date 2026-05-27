from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from store import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('news/', views.news, name='news'),
    path('glossary/', views.glossary, name='glossary'),
    path('contacts/', views.contacts, name='contacts'),
    path('privacy/', views.privacy, name='privacy'),
    path('vacancies/', views.vacancies, name='vacancies'),
    path('calendar/', views.calendar, name='calendar'),
    
    # Halls
    path('halls/', views.hall_list, name='hall_list'),
    
    # Exhibits
    path('exhibits/', views.exhibit_list, name='exhibit_list'),
    re_path(r'^exhibits/(?P<pk>\d+)/$', views.exhibit_detail, name='exhibit_detail'),
    
    # Tours
    path('tours/', views.tour_list, name='tour_list'),
    re_path(r'^tours/(?P<pk>\d+)/$', views.tour_detail, name='tour_detail'),
    
    # Tickets
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/create/', views.ticket_create, name='ticket_create'),
    re_path(r'^tickets/(?P<pk>\d+)/$', views.ticket_detail, name='ticket_detail'),
    
    # Reviews
    path('reviews/create/', views.review_create, name='review_create'),
    
    # Employee dashboard
    path('employee/', views.employee_dashboard, name='employee_dashboard'),
    
    # Statistics
    path('statistics/', views.statistics, name='statistics'),
    
    # API endpoints
    path('api/currency-rates/', views.api_currency_rates, name='api_currency_rates'),
    path('api/statistics/', views.api_statistics, name='api_statistics'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Async Demo (Bonus)
    path('async-demo/', views.async_demo, name='async_demo'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
