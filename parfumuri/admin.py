from django.contrib import admin
from django.db.models import Avg
from .models import Brand, Note, Perfume, Review, User, Celebrity


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('brandID', 'name')
    search_fields = ('name',)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('noteID', 'name', 'image_preview')
    search_fields = ('name',)
    fields = ('name', 'image')

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="50" height="50" />'
        return "No Image"
    image_preview.allow_tags = True
    image_preview.short_description = 'Preview'


@admin.register(Perfume)
class PerfumeAdmin(admin.ModelAdmin):
    list_display = ('perfumeID', 'name', 'brand', 'recommended_price', 'get_avg_rating', 'image', 'concentration', 'quantity')
    list_filter = ('brand', 'gender')
    search_fields = ('name', 'brand__name', 'description')
    fields = ('name', 'brand', 'gender', 'description', 'base_notes', 'middle_notes', 'top_notes', 'recommended_price', 'concentration', 'quantity', 'image')
    filter_horizontal = ('base_notes', 'middle_notes', 'top_notes')  # Many-to-Many Fields pentru note

    def get_avg_rating(self, obj):
        avg_rating = obj.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg_rating, 2) if avg_rating is not None else 'N/A'
    get_avg_rating.short_description = 'Average Rating'



@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewID', 'perfume', 'user', 'rating', 'reviewTitle')
    list_filter = ('rating', 'perfume')
    search_fields = ('reviewTitle', 'reviewComment')

from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    filter_horizontal = ('favoritePerfumes', 'favoriteNotes')

@admin.register(Celebrity)
class CelebrityAdmin(admin.ModelAdmin):
    list_display = ('name', 'occupation')
    search_fields = ('name', 'occupation')
    list_filter = ('occupation',)
