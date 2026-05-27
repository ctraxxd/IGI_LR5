import logging
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Position, ArtType, Hall, Employee, Exhibit, Exposition,
    Exhibition, Tour, Client, Ticket, PromoCode, Review,
    Vacancy, CompanyHistory, CompanyInfo
)

logger = logging.getLogger('museum')


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(ArtType)
class ArtTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ['number', 'name', 'floor', 'area', 'has_water_feature', 'has_heating']
    list_filter = ['floor', 'has_water_feature', 'has_heating']
    search_fields = ['name', 'number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'position', 'hall', 'phone', 'hire_date']
    list_filter = ['position', 'hall', 'hire_date']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    list_select_related = ['position', 'hall']


@admin.register(Exhibit)
class ExhibitAdmin(admin.ModelAdmin):
    list_display = ['name', 'art_type', 'acquisition_date', 'hall', 'assigned_employee', 'is_displayed']
    list_filter = ['art_type', 'hall', 'is_displayed', 'acquisition_date']
    search_fields = ['name', 'author', 'description']
    readonly_fields = ['created_at', 'updated_at']
    list_select_related = ['art_type', 'hall', 'assigned_employee']
    date_hierarchy = 'acquisition_date'
    
    actions = ['mark_as_displayed', 'mark_as_not_displayed']
    
    def mark_as_displayed(self, request, queryset):
        queryset.update(is_displayed=True)
        logger.info(f'Exhibits {list(queryset.values_list("id", flat=True))} marked as displayed')
    mark_as_displayed.short_description = 'Mark selected exhibits as displayed'
    
    def mark_as_not_displayed(self, request, queryset):
        queryset.update(is_displayed=False)
        logger.info(f'Exhibits {list(queryset.values_list("id", flat=True))} marked as not displayed')
    mark_as_not_displayed.short_description = 'Mark selected exhibits as not displayed'


@admin.register(Exposition)
class ExpositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'hall', 'exhibits_count']
    list_filter = ['hall']
    search_fields = ['name', 'description']
    filter_horizontal = ['exhibits']
    readonly_fields = ['created_at', 'updated_at']
    
    def exhibits_count(self, obj):
        return obj.exhibits.count()
    exhibits_count.short_description = 'Number of Exhibits'


@admin.register(Exhibition)
class ExhibitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_active', 'exhibits_count']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['name', 'description']
    filter_horizontal = ['exhibits']
    readonly_fields = ['created_at', 'updated_at']
    
    def exhibits_count(self, obj):
        return obj.exhibits.count()
    exhibits_count.short_description = 'Number of Exhibits'


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'date', 'season', 'group_size', 'guide', 'price']
    list_filter = ['season', 'date', 'guide']
    search_fields = ['code', 'name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    
    actions = ['mark_as_spring', 'mark_as_summer', 'mark_as_autumn', 'mark_as_winter']
    
    def mark_as_spring(self, request, queryset):
        queryset.update(season='spring')
    mark_as_spring.short_description = 'Mark selected tours as Spring'
    
    def mark_as_summer(self, request, queryset):
        queryset.update(season='summer')
    mark_as_summer.short_description = 'Mark selected tours as Summer'
    
    def mark_as_autumn(self, request, queryset):
        queryset.update(season='autumn')
    mark_as_autumn.short_description = 'Mark selected tours as Autumn'
    
    def mark_as_winter(self, request, queryset):
        queryset.update(season='winter')
    mark_as_winter.short_description = 'Mark selected tours as Winter'


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'phone', 'email', 'age', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    list_filter = ['created_at']
    readonly_fields = ['age', 'created_at', 'updated_at']
    
    def age(self, obj):
        return obj.age
    age.short_description = 'Age'


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'tour', 'visit_date', 'ticket_type', 'base_price', 'discount', 'final_price']
    list_filter = ['ticket_type', 'visit_date', 'purchase_date']
    search_fields = ['client__last_name', 'client__first_name', 'promo_code']
    readonly_fields = ['purchase_date', 'final_price', 'created_at', 'updated_at']
    date_hierarchy = 'visit_date'
    
    def save_model(self, request, obj, form, change):
        obj.calculate_price()
        super().save_model(request, obj, form, change)


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percent', 'min_purchase', 'is_active', 'valid_from', 'valid_until']
    list_filter = ['is_active', 'valid_from', 'valid_until']
    search_fields = ['code', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['client', 'rating', 'visit_date', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['client__last_name', 'text']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ['title', 'salary_range', 'is_active', 'posted_date']
    list_filter = ['is_active', 'posted_date']
    search_fields = ['title', 'description', 'requirements']
    readonly_fields = ['posted_date', 'created_at', 'updated_at']


@admin.register(CompanyHistory)
class CompanyHistoryAdmin(admin.ModelAdmin):
    list_display = ['year', 'event', 'created_at']
    list_filter = ['year']
    search_fields = ['event']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']


# Customize admin site
admin.site.site_header = 'Museum Administration'
admin.site.site_title = 'Museum Admin Portal'
admin.site.index_title = 'Welcome to the Museum Administration'
