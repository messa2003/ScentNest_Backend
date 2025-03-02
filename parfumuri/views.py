from rest_framework import viewsets
from .models import Perfume, Review, Brand, Note, Celebrity
from .serializers import PerfumeSerializer, ReviewSerializer, BrandSerializer, NoteSerializer, CelebritySerializer
from django.http import HttpResponse
from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.db.models import Avg
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Perfume
from .serializers import PerfumeSerializer
from rest_framework import generics
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

# View pentru pagina principală
def index(request):
    return HttpResponse("Bine ai venit pe platforma noastră de parfumuri!")

# ViewSets pentru API

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

from rest_framework import generics
from .serializers import RegisterSerializer
from rest_framework.permissions import AllowAny

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

from rest_framework.permissions import IsAuthenticated

class PerfumeViewSet(viewsets.ModelViewSet):
    queryset = Perfume.objects.all()
    serializer_class = PerfumeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Perfume.objects.annotate(
            avg_rating=Avg('reviews__rating')
        ).all()

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

from rest_framework.permissions import IsAuthenticated

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

from django.db.models import Avg
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Perfume
from .serializers import PerfumeSerializer

@api_view(['GET'])
def popular_perfumes(request):
    """
    Returnează parfumurile sortate după rating mediu, în ordine descrescătoare.
    """
    perfumes = Perfume.objects.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')[:10]
    serializer = PerfumeSerializer(perfumes, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def perfume_detail(request, pk):
    """
    Returnează detaliile unui parfum specific, inclusiv ratingul mediu.
    """
    try:
        # Adaugă calculul pentru avg_rating
        perfume = Perfume.objects.annotate(avg_rating=Avg('reviews__rating')).get(pk=pk)
        serializer = PerfumeSerializer(perfume)
        return Response(serializer.data)
    except Perfume.DoesNotExist:
        return Response({'error': 'Parfum nu a fost găsit'}, status=404)



class AdvancedSearchPerfumeView(generics.ListAPIView):
    """
    Endpoint pentru căutare avansată de parfumuri.
    """
    serializer_class = PerfumeSerializer

    def get_queryset(self):
        queryset = Perfume.objects.all()
        brand = self.request.query_params.get('brand', None)
        note = self.request.query_params.get('note', None)
        gender = self.request.query_params.get('gender', None)

        if brand:
            queryset = queryset.filter(brand__name__icontains=brand)
        if note:
            queryset = queryset.filter(notes__name__icontains=note)
        if gender:
            queryset = queryset.filter(gender=gender)

        return queryset.distinct()

from rest_framework import viewsets
from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import UserSerializer, UserProfileSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from parfumuri.models import Perfume, UserProfile

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, perfume_id):
    user_profile = UserProfile.objects.get(user=request.user)
    try:
        # Găsește parfumul specific folosind `perfumeID`
        perfume = Perfume.objects.get(perfumeID=perfume_id)

        # Verifică dacă parfumul este deja în lista de favorite
        if perfume in user_profile.favoritePerfumes.all():
            user_profile.favoritePerfumes.remove(perfume)
            return Response({'message': 'Parfumul a fost eliminat din favorite.'}, status=200)
        else:
            user_profile.favoritePerfumes.add(perfume)
            return Response({'message': 'Parfumul a fost adăugat la favorite.'}, status=200)

    except Perfume.DoesNotExist:
        return Response({'error': 'Parfumul nu există.'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def is_favorite(request, perfume_id):
    try:
        user_profile = request.user.profile  # Profile-ul utilizatorului autentificat
        perfume = Perfume.objects.get(perfumeID=perfume_id)  # Parfumul specificat prin ID
        is_favorite = user_profile.favoritePerfumes.filter(perfumeID=perfume_id).exists()
        return Response({'is_favorite': is_favorite}, status=200)
    except Perfume.DoesNotExist:
        return Response({'error': 'Parfumul nu există.'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    try:
        print(f"User: {request.user}")
        if not hasattr(request.user, 'profile'):
            print("Profilul utilizatorului nu există.")
            return Response({'error': 'Profilul utilizatorului nu există.'}, status=404)
        user_profile = request.user.profile
        serializer = UserProfileSerializer(user_profile)
        print("Serializer data:", serializer.data)
        return Response(serializer.data, status=200)
    except Exception as e:
        print("Eroare:", str(e))
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def list_perfumes(request):
    try:
        # Add the annotation for avg_rating
        perfumes = Perfume.objects.annotate(
            avg_rating=Avg('reviews__rating')
        ).all()
        
        serializer = PerfumeSerializer(perfumes, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from parfumuri.models import Perfume, Review
from parfumuri.serializers import ReviewSerializer
from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request, perfume_id):
    try:
        print("Received data:", request.data)  # Debug print
        
        perfume = Perfume.objects.get(perfumeID=perfume_id)
        
        # Check if user already has a review for this perfume
        existing_review = Review.objects.filter(perfume=perfume, user=request.user).first()
        if existing_review:
            return Response(
                {'error': 'Ai adăugat deja o recenzie pentru acest parfum.'}, 
                status=400
            )

        # Create the review data
        review_data = {
            'reviewTitle': request.data.get('reviewTitle'),
            'reviewComment': request.data.get('reviewComment'),
            'rating': request.data.get('rating'),
            'perfume': perfume_id,
            'user': request.user.id
        }
        
        print("Review data:", review_data)  # Debug print
        
        serializer = ReviewSerializer(data=review_data)
        if serializer.is_valid():
            print("Serializer is valid")  # Debug print
            review = serializer.save(user=request.user, perfume=perfume)
            return Response(serializer.data, status=201)
        
        print("Serializer errors:", serializer.errors)  # Debug print
        return Response(serializer.errors, status=400)
        
    except Perfume.DoesNotExist:
        return Response({'error': 'Parfumul nu există.'}, status=404)
    except Exception as e:
        print("Error:", str(e))  # Debug print
        return Response({'error': str(e)}, status=500)

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_review(request, review_id):
    try:
        review = Review.objects.get(reviewID=review_id, user=request.user)
        
        if request.method == 'DELETE':
            review.delete()
            return Response({'message': 'Recenzia a fost ștearsă cu succes.'}, status=204)
            
        elif request.method == 'PUT':
            data = {
                'reviewTitle': request.data.get('reviewTitle', review.reviewTitle),
                'reviewComment': request.data.get('reviewComment', review.reviewComment),
                'rating': request.data.get('rating', review.rating),
                'user': request.user.id,
                'perfume': review.perfume.perfumeID
            }
            
            serializer = ReviewSerializer(review, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
            
    except Review.DoesNotExist:
        return Response(
            {'error': 'Recenzia nu există sau nu aparține utilizatorului.'}, 
            status=404
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite_note(request, note_id):
    user_profile = UserProfile.objects.get(user=request.user)
    try:
        note = Note.objects.get(noteID=note_id)
        
        if note in user_profile.favoriteNotes.all():
            user_profile.favoriteNotes.remove(note)
            return Response({'message': 'Nota a fost eliminată din favorite.'}, status=200)
        else:
            user_profile.favoriteNotes.add(note)
            return Response({'message': 'Nota a fost adăugată la favorite.'}, status=200)
            
    except Note.DoesNotExist:
        return Response({'error': 'Nota nu există.'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def is_note_favorite(request, note_id):
    try:
        user_profile = request.user.profile
        is_favorite = user_profile.favoriteNotes.filter(noteID=note_id).exists()
        return Response({'is_favorite': is_favorite}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_favorite_notes(request):
    try:
        user_profile = request.user.profile
        favorite_notes = user_profile.favoriteNotes.all()
        serializer = NoteSerializer(favorite_notes, many=True)
        return Response(serializer.data, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    try:
        user = request.user
        return Response({
            'username': user.username,
            'id': user.id,
            'email': user.email,
            'profile': {
                'favoritePerfumes': [p.perfumeID for p in user.profile.favoritePerfumes.all()],
                'favoriteNotes': [n.noteID for n in user.profile.favoriteNotes.all()]
            }
        })
    except Exception as e:
        print("Error getting user info:", str(e))
        return Response({'error': str(e)}, status=500)

class CelebrityViewSet(viewsets.ModelViewSet):
    queryset = Celebrity.objects.all()
    serializer_class = CelebritySerializer
    permission_classes = [IsAuthenticated]