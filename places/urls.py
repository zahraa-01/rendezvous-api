from django.urls import path
from places.views import PlaceListCreateView, PlaceRetrieveView

urlpatterns = [
    path('', PlaceListCreateView.as_view(), name='place-list-create'),
    path('<int:pk>/', PlaceRetrieveView.as_view(), name='place-detail'),
]
