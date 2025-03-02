from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Perfume, Review, Brand, Note, UserProfile, Celebrity

# Define UserSerializer first since it's used by other serializers
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = ['reviewID', 'user', 'perfume', 'rating', 'reviewTitle', 'reviewComment']
        read_only_fields = ['reviewID', 'user']

    def validate_rating(self, value):
        try:
            rating = float(value)
            if rating < 1 or rating > 10:
                raise serializers.ValidationError("Rating must be between 1 and 10")
            return rating
        except (TypeError, ValueError):
            raise serializers.ValidationError("Rating must be a number")

class PerfumeSerializer(serializers.ModelSerializer):
    avg_rating = serializers.FloatField(read_only=True)
    brand = serializers.SlugRelatedField(
        queryset=Brand.objects.all(),
        slug_field='name'
    )
    base_notes = NoteSerializer(many=True, read_only=True)
    middle_notes = NoteSerializer(many=True, read_only=True)
    top_notes = NoteSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    # Add these fields for write operations
    base_notes_ids = serializers.ListField(write_only=True, required=False)
    middle_notes_ids = serializers.ListField(write_only=True, required=False)
    top_notes_ids = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = Perfume
        fields = ['perfumeID', 'name', 'brand', 'description', 'image', 
                 'gender', 'top_notes', 'middle_notes', 'base_notes',
                 'base_notes_ids', 'middle_notes_ids', 'top_notes_ids', 
                 'reviews', 'avg_rating', 'recommended_price',
                 'concentration', 'quantity']

    def create(self, validated_data):
        base_notes_ids = validated_data.pop('base_notes_ids', [])
        middle_notes_ids = validated_data.pop('middle_notes_ids', [])
        top_notes_ids = validated_data.pop('top_notes_ids', [])
        
        perfume = Perfume.objects.create(**validated_data)
        
        if base_notes_ids:
            perfume.base_notes.set(base_notes_ids)
        if middle_notes_ids:
            perfume.middle_notes.set(middle_notes_ids)
        if top_notes_ids:
            perfume.top_notes.set(top_notes_ids)
        
        return perfume

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email-ul este deja folosit.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Numele de utilizator este deja folosit.")
        return value

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['favoritePerfumes', 'favoriteNotes']

# Extended UserSerializer with profile
class UserWithProfileSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']

class CelebritySerializer(serializers.ModelSerializer):
    perfumes = PerfumeSerializer(many=True, read_only=True)
    
    class Meta:
        model = Celebrity
        fields = ['celebrityID', 'name', 'image', 'description', 'occupation', 'perfumes']
