from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class ResourceCategory(models.Model):
    """
    Catégorie de ressources (salles, équipements, services)
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Resource Categories"

class Resource(models.Model):
    """
    Modèle représentant une ressource à réserver
    """
    name = models.CharField(max_length=200, unique=True)
    category = models.ForeignKey(ResourceCategory, on_delete=models.CASCADE, related_name='resources')
    description = models.TextField(blank=True)
    
    # Caractéristiques de la ressource
    capacity = models.PositiveIntegerField()
    equipment = models.TextField(blank=True, help_text="Liste des équipements disponibles")
    usage_conditions = models.TextField(blank=True, help_text="Conditions particulières d'utilisation")
    
    # État de la ressource
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Reservation(models.Model):
    """
    Modèle de réservation sans utilisateur
    """
    STATUS_CHOICES = [
        ('pending', 'En Attente'),
        ('confirmed', 'Confirmée'),
        ('cancelled', 'Annulée'),
    ]

    # Informations de réservation
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='reservations')
    
    # Identifiant de réservation pour le client
    reservation_code = models.CharField(max_length=50, unique=True)
    
    # Informations du demandeur
    contact_name = models.CharField(max_length=200)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)

    # Plage horaire de réservation
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    # Statut et priorité de réservation
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.IntegerField(default=0, help_text="Priorité de réservation")
    
    # Horodatages
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.contact_name} - {self.resource.name} ({self.start_time})"

    def clean(self):
        """
        Validation personnalisée pour :
        1. Vérifier la cohérence des dates
        2. Détecter les conflits de réservation
        """
        # Vérifier que la date de début est avant la date de fin
        if self.start_time >= self.end_time:
            raise ValidationError("La date de début doit être antérieure à la date de fin.")

        # Vérifier qu'il n'y a pas de chevauchement avec d'autres réservations
        conflicting_reservations = Reservation.objects.filter(
            resource=self.resource,
            status__in=['pending', 'confirmed'],
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(pk=self.pk)
        
        if conflicting_reservations.exists():
            raise ValidationError("Cette réservation entre en conflit avec une réservation existante.")

    def save(self, *args, **kwargs):
        """
        Surcharge de la méthode save pour :
        1. Validation
        2. Génération du code de réservation si non existant
        """
        if not self.reservation_code:
            # Générer un code de réservation unique
            from uuid import uuid4
            self.reservation_code = str(uuid4())[:8].upper()

        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        unique_together = ['resource', 'start_time', 'end_time']
        ordering = ['-created_at']