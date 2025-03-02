from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter
from parfumuri.views import (
    PerfumeViewSet, ReviewViewSet, BrandViewSet, NoteViewSet, UserViewSet, RegisterView,
    popular_perfumes, AdvancedSearchPerfumeView, perfume_detail, toggle_favorite, is_favorite, get_user_profile,
    list_perfumes, toggle_favorite_note, is_note_favorite, get_favorite_notes, create_review, manage_review,
    get_current_user, CelebrityViewSet
)

# Router pentru API
router = DefaultRouter()
router.register(r'parfumuri', PerfumeViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'branduri', BrandViewSet)
router.register(r'note', NoteViewSet)
router.register(r'users', UserViewSet)
router.register(r'celebrities', CelebrityViewSet)

urlpatterns = [
    # Rute specifice
    path('api/users/me/', get_current_user, name='get_current_user'),
    path('api/perfumes/<int:perfume_id>/toggle-favorite/', toggle_favorite, name='toggle_favorite'),
    path('api/perfumes/<int:perfume_id>/is-favorite/', is_favorite, name='is_favorite'),
    path('api/perfumes/popular/', popular_perfumes, name='popular_perfumes'),
    path('api/perfumes/', list_perfumes, name='list_perfumes'),
    path('api/perfumes/search/', AdvancedSearchPerfumeView.as_view(), name='advanced_search_perfumes'),
    path('api/perfumes/<int:pk>/', perfume_detail, name='perfume_detail'),

    # Rute generale
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),  # Rutele generate de router

    path('', include('parfumuri.urls_parfumuri')),

    # Admin și fișiere media
    path('admin/', admin.site.urls),

    path('api/notes/<int:note_id>/toggle-favorite/', toggle_favorite_note, name='toggle_favorite_note'),
    path('api/notes/<int:note_id>/is-favorite/', is_note_favorite, name='is_note_favorite'),
    path('api/notes/favorites/', get_favorite_notes, name='get_favorite_notes'),

    path('api/perfumes/<int:perfume_id>/reviews/', create_review, name='create_review'),
    path('api/reviews/<int:review_id>/', manage_review, name='manage_review'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
