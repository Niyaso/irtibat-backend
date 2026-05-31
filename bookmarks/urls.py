from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, MeView,
    BookmarkViewSet, CollectionViewSet,
    TagViewSet, PublicCollectionView,
    QuickSaveView,
)

router = DefaultRouter()
router.register(r"bookmarks", BookmarkViewSet, basename="bookmark")
router.register(r"collections", CollectionViewSet, basename="collection")
router.register(r"tags", TagViewSet, basename="tag")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("quick-save/", QuickSaveView.as_view(), name="quick-save"),
    path(
        "public/<str:username>/<slug:slug>/",
        PublicCollectionView.as_view(),
        name="public-collection",
    ),
]