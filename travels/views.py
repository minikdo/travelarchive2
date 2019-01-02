# from django.shortcuts import render
# from django.http import HttpResponse
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView

from .models import Travel, Place, Journey, Flight


class IndexView(ListView):

    model = Travel
    
    
class TravelDetailView(TemplateView):

    template_name = 'travels/travel_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        travel = self.kwargs['pk']
        
        context['travel'] = travel
        context['countries'] = Travel.objects.filter(pk=travel)
        context['places'] = Place.objects.filter(travel__pk=travel)
        context['journeys'] = Journey.objects.filter(travel__pk=travel)
        context['flights'] = Flight.objects.filter(travel__pk=travel)
        
        return context


class PlaceUpdate(UpdateView):
    """ edit place """

    model = Place
    fields = ['start_date', 'end_date', 'country', 'city',
              'place', 'gps', 'notes']


class FlightDetailView(DetailView):
    """ flight details """
    
    model = Flight

