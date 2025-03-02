from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Brand(models.Model):
    brandID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Note(models.Model):
    noteID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='note_images/', null=True, blank=True)


    def __str__(self):
        return self.name

class Perfume(models.Model):
    perfumeID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='perfumes')
    base_notes = models.ManyToManyField(Note, related_name='base_notes')
    middle_notes = models.ManyToManyField(Note, related_name='middle_notes')
    top_notes = models.ManyToManyField(Note, related_name='top_notes')
    gender = models.CharField(max_length=10, choices=[('M', 'Masculin'), ('F', 'Feminin'), ('U', 'Unisex')])
    description = models.TextField()
    concentration = models.CharField(max_length=50)
    quantity = models.CharField(max_length=50)
    image = models.ImageField(upload_to='perfume_images/', null=True, blank=True)
    recommended_price = models.IntegerField()

    def __str__(self):
        return f"{self.name} by {self.brand.name}"

from django.contrib.auth.models import User

class Review(models.Model):
    reviewID = models.AutoField(primary_key=True)
    perfume = models.ForeignKey(Perfume, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[
            MinValueValidator(1.0),
            MaxValueValidator(10.0)
        ]
    )
    reviewTitle = models.CharField(max_length=100)
    reviewComment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'perfume')

    def __str__(self):
        return f"{self.reviewTitle} - {self.user.username} ({self.rating})"

from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    favoritePerfumes = models.ManyToManyField('Perfume', blank=True, related_name='favorited_by')
    favoriteNotes = models.ManyToManyField('Note', blank=True, related_name='favorited_by')

    def __str__(self):
        return self.user.username


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Celebrity(models.Model):
    celebrityID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='celebrity_images/', null=True, blank=True)
    description = models.TextField()  # Brief bio or description
    perfumes = models.ManyToManyField(Perfume, related_name='worn_by_celebrities')
    occupation = models.CharField(max_length=100)  # e.g., Actor, Singer, etc.

    def __str__(self):
        return self.name