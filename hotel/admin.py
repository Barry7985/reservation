from django.contrib import admin
from .models import ResourceCategory, Resource, Reservation

@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    """
    Administration pour les catégories de ressources
    """
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    """
    Administration pour les ressources
    """
    list_display = ('name', 'category', 'capacity', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'category__name')
    ordering = ('name',)
    fieldsets = (
        ('Informations Générales', {
            'fields': ('name', 'category', 'description')
        }),
        ('Caractéristiques', {
            'fields': ('capacity', 'equipment', 'usage_conditions')
        }),
        ('État', {
            'fields': ('is_active',)
        }),
    )

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    """
    Administration pour les réservations
    """
    list_display = ('resource', 'contact_name', 'start_time', 'end_time', 'status', 'priority')
    list_filter = ('status', 'resource', 'start_time')
    search_fields = ('resource__name', 'contact_name', 'reservation_code')
    ordering = ('-created_at',)
    readonly_fields = ('reservation_code', 'created_at', 'updated_at')

    fieldsets = (
        ('Informations Générales', {
            'fields': ('resource', 'reservation_code', 'status', 'priority')
        }),
        ('Détails du Demandeur', {
            'fields': ('contact_name', 'contact_email', 'contact_phone')
        }),
        ('Plage Horaire', {
            'fields': ('start_time', 'end_time')
        }),
        ('Horodatage', {
            'fields': ('created_at', 'updated_at')
        }),
    )
