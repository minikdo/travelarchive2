from django.urls import path
# from django.contrib.auth.views import LoginView, LogoutView

from . import views

app_name = 'travels'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.TravelDetailView.as_view(), name='travel-detail'),
    # path('', views.FlightIndexView.as_view(), name='flight-index'),
    path('flight/<int:pk>/', views.FlightDetailView.as_view(), name='flight-detail'),
    path('place/<int:pk>/', views.PlaceUpdate.as_view(), name='place-update'),
]
