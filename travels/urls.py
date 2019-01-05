from django.urls import path
# from django.contrib.auth.views import LoginView, LogoutView

from . import views

app_name = 'travels'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.TravelDetailView.as_view(), name='travel-detail'),
    path('add/', views.TravelCreate.as_view(), name='travel-create'),
    path('<int:pk>/update/', views.TravelUpdate.as_view(),
         name='travel-update'),
    # path('', views.FlightIndexView.as_view(), name='flight-index'),
    path('flight/<int:pk>/', views.FlightDetailView.as_view(),
         name='flight-detail'),
    path('<int:travel>/place/add/', views.PlaceCreate.as_view(),
         name='place-create'),
    path('place/<int:pk>/update/', views.PlaceUpdate.as_view(),
         name='place-update'),
    path('<int:travel>/journey/add/', views.JourneyCreate.as_view(),
         name='journey-create'),
    path('journey/<int:pk>/update/', views.JourneyUpdate.as_view(),
         name='journey-update'),
    path('journey/<int:pk>/delete/', views.JourneyDelete.as_view(),
         name='journey-delete'),
    path('flights/', views.FlightIndexView.as_view(), name='flight-index'),
    path('flights/<int:pk>/update/', views.FlightUpdate.as_view(),
         name='flight-update'),
    path('country-autocomplete', views.CountryAutocomplete.as_view(),
         name='country-autocomplete'),
    path('airport-autocomplete', views.AirportAutocomplete.as_view(),
         name='airport-autocomplete'),
]
