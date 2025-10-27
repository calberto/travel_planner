# Configuração do admin Django
from django.contrib import admin
from django.utils.html import format_html


from .models import(
    # Accommodation,
    # Activity,
    # AreaOption,
    # Checklist,
    # ChecklistItem,
    # City,
    # Country,
    Destination,
    # LearningEntry,
    # LocalTransport,
    # TransportOption,
    Trip,
    # TripCity,
    # TripNote,
)
# admin.site.register(Accommodation)
# admin.site.register(Activity)
# admin.site.register(AreaOption)
# admin.site.register(Checklist)
# admin.site.register(ChecklistItem)
# admin.site.register(City)
# admin.site.register(Country)
admin.site.register(Destination)
# admin.site.register(LearningEntry)
# admin.site.register(LocalTransport)
# admin.site.register(TransportOption)
admin.site.register(Trip)
# admin.site.register(TripCity)
# admin.site.register(TripNote)


# @admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    """
    Configuração do admin para Trip
    """
    list_display = ['name', 'start_date', 'end_date', 'destinations_count', 'created_at']
    list_filter = ['start_date', 'end_date', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {}
    date_hierarchy = 'start_date'
    
    def destinations_count(self, obj):
        return obj.destinations.count()
    destinations_count.short_description = 'Destinos'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('destinations')


# @admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    """
    Configuração do admin para Destination
    """
    list_display = [
        'name', 'city', 'country', 'trip', 'arrival_date', 
        'departure_date', 'has_image', 'has_coordinates', 'created_at'
    ]
    list_filter = [
        'trip', 'country', 'arrival_date', 'departure_date', 
        'created_at', 'updated_at'
    ]
    search_fields = ['name', 'city', 'country', 'description']
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'arrival_date'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'slug', 'city', 'country', 'trip')
        }),
        ('Datas', {
            'fields': ('arrival_date', 'departure_date'),
            'classes': ('collapse',)
        }),
        ('Localização', {
            'fields': ('longitude', 'latitude'),
            'classes': ('collapse',)
        }),
        ('Mídia e Descrição', {
            'fields': ('image', 'description'),
            'classes': ('collapse',)
        }),
    )
    
    def has_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;">',
                obj.image.url
            )
        return "Sem imagem"
    has_image.short_description = 'Imagem'
    
    def has_coordinates(self, obj):
        if obj.has_coordinates:
            return format_html(
                '<span style="color: green;">✓ Sim</span>'
            )
        return format_html(
            '<span style="color: red;">✗ Não</span>'
        )
    has_coordinates.short_description = 'Coordenadas'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('trip')
    
    actions = ['duplicate_destinations']
    
    def duplicate_destinations(self, request, queryset):
        """
        Ação para duplicar destinos selecionados
        """
        for destination in queryset:
            destination.pk = None
            destination.name = f"Cópia de {destination.name}"
            destination.slug = None  # Será auto-gerado
            destination.save()
        
        self.message_user(request, f"{queryset.count()} destino(s) duplicado(s) com sucesso.")
    
    duplicate_destinations.short_description = "Duplicar destinos selecionados"