# models.py
from django.utils import timezone 
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from PIL import Image
import os


class Trip(models.Model):
    """
    Modelo para representar uma viagem
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Este campo pode estar faltando
    name = models.CharField(max_length=200, default="Unnamed Trip")
    description = models.TextField(blank=True, verbose_name="Descrição")
    start_date = models.DateField(null=True, blank=True, verbose_name="Data de Início")
    end_date = models.DateField(null=True, blank=True, verbose_name="Data de Fim")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Viagem"
        verbose_name_plural = "Viagens"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Destination(models.Model):
    """
    Modelo para representar um destino
    """
    name = models.CharField(max_length=200, verbose_name="Nome do Destino")
    city = models.CharField(max_length=100, blank=True, verbose_name="Cidade")
    country = models.CharField(max_length=100, blank=True, verbose_name="País")
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="Slug")
    
    # Relacionamento com viagem
    trip = models.ForeignKey(
        Trip, 
        on_delete=models.CASCADE, 
        related_name='destinations',
        null=True, 
        blank=True,
        verbose_name="Viagem"
    )
    
    # Datas
    arrival_date = models.DateField(null=True, blank=True, verbose_name="Data de Chegada")
    departure_date = models.DateField(null=True, blank=True, verbose_name="Data de Partida")
    
    # Coordenadas geográficas
    longitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        verbose_name="Longitude"
    )
    latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        verbose_name="Latitude"
    )
    
    # Imagem e descrição
    image = models.ImageField(
        upload_to='destinations/', 
        null=True, 
        blank=True,
        verbose_name="Imagem"
    )
    description = models.TextField(blank=True, verbose_name="Descrição")
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Destino"
        verbose_name_plural = "Destinos"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['city', 'country']),
            models.Index(fields=['arrival_date']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Auto-gerar slug se não fornecido
        if not self.slug:
            self.slug = slugify(self.name)
            
            # Garantir que o slug seja único
            counter = 1
            original_slug = self.slug
            while Destination.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        super().save(*args, **kwargs)
        
        # Redimensionar imagem se necessário
        if self.image:
            self.resize_image()
    
    def resize_image(self):
        """
        Redimensiona a imagem para otimizar o armazenamento
        """
        if self.image:
            img = Image.open(self.image.path)
            
            # Redimensionar se a imagem for muito grande
            max_size = (800, 600)
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                img.save(self.image.path, optimize=True, quality=85)
    
    def get_absolute_url(self):
        """
        Retorna a URL absoluta do destino
        """
        return reverse('trip:destination_detail', kwargs={'destination_id': self.id})
    
    @property
    def full_location(self):
        """
        Retorna a localização completa (cidade, país)
        """
        parts = [self.city, self.country]
        return ", ".join(filter(None, parts))
    
    @property
    def has_coordinates(self):
        """
        Verifica se o destino possui coordenadas geográficas
        """
        return self.longitude is not None and self.latitude is not None
    
    @property
    def duration_days(self):
        """
        Calcula a duração da estadia em dias
        """
        if self.arrival_date and self.departure_date:
            return (self.departure_date - self.arrival_date).days
        return None
    
    def clean(self):
        """
        Validações personalizadas
        """
        from django.core.exceptions import ValidationError
        
        # Validar datas
        if self.arrival_date and self.departure_date:
            if self.departure_date < self.arrival_date:
                raise ValidationError({'departure_date': 'A data de partida não pode ser anterior à chegada.'})
        
        # Validar coordenadas
        if (self.longitude is not None and self.latitude is None) or \
           (self.longitude is None and self.latitude is not None):
            raise ValidationError({
                'longitude': 'Longitude e latitude devem ser fornecidas juntas.',
                'latitude': 'Longitude e latitude devem ser fornecidas juntas.'
            })
    
    def delete(self, *args, **kwargs):
        """
        Remove a imagem do arquivo ao deletar o destino
        """
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)


# Sinal para limpar imagens órfãs
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

@receiver(pre_save, sender=Destination)
def delete_old_image(sender, instance, **kwargs):
    """
    Remove a imagem antiga quando uma nova é carregada
    """
    if instance.pk:
        try:
            old_instance = Destination.objects.get(pk=instance.pk)
            if old_instance.image and old_instance.image != instance.image:
                if os.path.isfile(old_instance.image.path):
                    os.remove(old_instance.image.path)
        except Destination.DoesNotExist:
            pass

class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=2)
    currency = models.CharField(max_length=3)
    language = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=2)
    currency = models.CharField(max_length=3)
    language = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='cities')
    description = models.TextField(blank=True)
    is_popular = models.BooleanField(default=False)

    # Coordenadas geográficas para mapa
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Cities'    

    def __str__(self):
        return f"{self.name}, {self.country}"

class Transportation(models.Model):
    """Opções de transporte entre cidades"""
    TRANSPORT_TYPES = [
        ('PLANE', 'Avião'),
        ('TRAIN', 'Trem'),
        ('BUS', 'Ônibus'),
        ('FERRY', 'Balsa'),
        ('OTHER', 'Outro'),
    ]      

    origin = models.ForeignKey(City, on_delete=models.CASCADE, related_name='departures')
    destination = models.ForeignKey(City, on_delete=models.CASCADE, related_name='arrival')
    transport_type = models.CharField(max_length=10, choices=TRANSPORT_TYPES)
    company = models.CharField(max_length=100, blank=True)
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2)
    price_min = models.DecimalField(max_digits=8, decimal_places=2)
    notes = models.TextField(blank=True)
    booking_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.origin} para {self.destination} via {self.get_transport_type_display()}"  


@receiver(post_delete, sender=Destination)
def delete_image_on_delete(sender, instance, **kwargs):
    """
    Remove a imagem quando o destino é deletado
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

class Itinerary(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('published', 'Publicado'),
        ('completed', 'Concluído'),
        ('cancelled', 'Cancelado'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='itineraries')
    cities = models.ManyToManyField(City, related_name='itineraries')
    start_date = models.DateField(null=True, blank=True, verbose_name="Data de Chegada")
    end_date = models.DateField(null=True, blank=True, verbose_name="Data de Chegada")
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Itineraries"
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    @property
    def total_days(self):
        return (self.end_date - self.start_date).days + 1      

class Activity(models.Model):
    """Modelo para uma atividade em um destino"""
    CATEGORY_CHOICES = [
        ('museum', 'Museu'),
        ('restaurant', 'Restaurante'),
        ('attraction', 'Atração Turística'),
        ('hotel', 'Hotel'),
        ('transport', 'Transporte'),
        ('shopping', 'Compras'),
        ('entertainment', 'Entretenimento'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='activities')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='activities')
    address = models.CharField(max_length=300, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    duration_hours = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        null=True, 
        blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.city.name}"          

class ItineraryActivity(models.Model):
    """Tabela intermediária para relacionar itinerário com atividades"""
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    day_number = models.PositiveIntegerField()  # Dia do itinerário (1, 2, 3...)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)  # Ordem no dia
    
    class Meta:
        unique_together = ['itinerary', 'activity', 'day_number']
        ordering = ['day_number', 'order']
    
    def __str__(self):
        return f"{self.itinerary.title} - Dia {self.day_number} - {self.activity.name}"
