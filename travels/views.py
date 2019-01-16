from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView,\
    FormMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.db.models import Q

from dal.autocomplete import Select2QuerySetView

from .models import Travel, Place, Journey, Flight, Country, Airport, Airline
from .forms import (PlaceForm, TravelForm, JourneyForm,
                    FlightSearchForm, FlightForm)

import datetime


class IndexView(ListView):

    model = Travel
    paginate_by = 40
    
    def get_queryset(self):
        qs = Travel.objects.all().prefetch_related('country')
        return qs
    
    
class TravelDetailView(TemplateView):

    template_name = 'travels/travel_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        travel = self.kwargs['pk']
        
        context['travel'] = Travel.objects.get(pk=travel)
        context['places'] = Place.objects\
                                 .filter(travel__pk=travel)\
                                 .prefetch_related('country')
        context['journeys'] = Journey.objects\
                                     .filter(travel__pk=travel)\
                                     .prefetch_related('transport_type')
        context['flights'] = Flight.objects\
                                   .filter(travel__pk=travel)\
                                   .prefetch_related('orig', 'dest')
        return context


class TravelCreate(CreateView):
    """ add a travel """

    model = Travel
    form_class = TravelForm

    
class TravelUpdate(UpdateView):
    """ edit travel """

    model = Travel
    form_class = TravelForm
    

class PlaceCreate(CreateView):
    """ add a place """

    model = Place
    form_class = PlaceForm

    def get_success_url(self):
        return super().get_success_url()
        
    def form_valid(self, form):
        form.instance.travel_id = self.kwargs.get('travel')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(session_data={'travel': self.kwargs.get('travel')})
        return kwargs

    def get_initial(self):
        country = Travel.objects.get(pk=self.kwargs.get('travel'))

        try:
            queryset = Place.objects.filter(travel=self.kwargs.get('travel'))\
                                    .latest('start_date')
        except Place.DoesNotExist:
            start_date = country.start_date
            end_date = start_date + datetime.timedelta(days=1)
        else:
            start_date = queryset.end_date
            end_date = start_date + datetime.timedelta(days=1)

        return {'start_date': start_date,
                'end_date': end_date,
                'country': country}
    

class PlaceUpdate(UpdateView):
    """ edit place """

    model = Place
    form_class = PlaceForm

    def get_form_kwargs(self):  # FIXME repeated
        travel = Place.objects.get(pk=self.kwargs.get('pk')).travel.pk
        kwargs = super().get_form_kwargs()
        kwargs.update(session_data={'travel': travel})
        return kwargs


class PlaceDelete(DeleteView):
    """ delete a place """

    model = Place

    def get_success_url(self):
        travel = self.object.travel
        return reverse_lazy('travels:travel-detail',
                            kwargs={'pk': travel.pk})


def place_duplicate(request, pk):
    """ duplicate a place """

    if isinstance(pk, int):
        obj = Place.objects.get(pk=pk)

        last_date_obj = Place.objects\
                             .filter(travel=obj.travel.pk)\
                             .latest('end_date')

        obj.pk = None
        obj.start_date = last_date_obj.end_date
        obj.end_date = last_date_obj.end_date
        obj.save()

    return redirect(obj)  # FIXME verify this
    
    
class JourneyCreate(CreateView):
    """ add a journey """

    model = Journey
    form_class = JourneyForm
    
    def form_valid(self, form):  # FIXME repeated
        form.instance.travel_id = self.kwargs.get('travel')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context['last_journey'] = Journey.objects.filter(
                travel=self.kwargs.get('travel')).latest(
                    'start_date', 'pk')
        except Journey.DoesNotExist:
            context['last_journey'] = ''
            
        return context

    def get_initial(self):
        country = Travel.objects.get(pk=self.kwargs.get('travel'))
        orig = ''
        transport = ''
        
        try:
            queryset = Journey.objects\
                              .filter(travel=self.kwargs.get('travel'))\
                              .latest('start_date', 'pk')
        except Journey.DoesNotExist:
            start_date = country.start_date
        else:
            if queryset.end_date:
                start_date = queryset.end_date
            else:
                start_date = queryset.start_date
            if queryset.dest:
                orig = queryset.dest
            if queryset.transport_type:
                transport = queryset.transport_type
                
        return {'start_date': start_date,
                'orig': orig,
                'transport_type': transport,
                'country': country}


class JourneyUpdate(UpdateView):
    """ edit journey """

    model = Journey
    form_class = JourneyForm


class JourneyDelete(DeleteView):
    """ delete a journey """

    model = Journey

    def get_success_url(self):
        travel = self.object.travel
        return reverse_lazy('travels:travel-detail',
                            kwargs={'pk': travel.pk})


class FlightDetailView(DetailView):
    """ flight details """
    
    model = Flight


class CountryAutocomplete(Select2QuerySetView):
    
    def get_queryset(self):

        qs = Country.objects.all()
        
        if self.q:
            qs = qs.filter(country_name__istartswith=self.q)
            
        return qs


class AirportAutocomplete(Select2QuerySetView):
    
    def get_queryset(self):

        qs = Airport.objects.all()
        
        if self.q:
            qs = qs.filter(Q(city__istartswith=self.q) |
                           Q(iata__icontains=self.q))
            
        return qs


class AirlineAutocomplete(Select2QuerySetView):

    def get_queryset(self):

        qs = Airline.objects.all()
        
        if self.q:
            qs = qs.filter(Q(name__istartswith=self.q))
            
        return qs


class FlightIndexView(FormMixin, ListView):
    """ list of flights """

    model = Flight
    form_class = FlightSearchForm
    paginate_by = 50

    def get_queryset(self):
        query = Flight.objects.all()

        if self.orig:
            query = query.filter(orig=self.orig)
        if self.dest:
            query = query.filter(dest=self.dest)

        query = query.prefetch_related('orig', 'dest', 'airline')
            
        return query.order_by('-date')
    
    def dispatch(self, request, *args, **kwargs):
    
        self.orig = request.GET.get('orig', None)
        self.dest = request.GET.get('dest', None)
        return super().dispatch(request, *args, **kwargs)


class FlightCreate(CreateView):
    """ create a flight """

    model = Flight
    form_class = FlightForm

    def form_valid(self, form):  # FIXME repeated
        form.instance.travel_id = self.kwargs.get('travel')
        return super().form_valid(form)

    # def get_form_kwargs(self):
        # kwargs = super().get_form_kwargs()
        # kwargs.update(session_data={'travel': self.kwargs.get('travel')})
        # return kwargs
    

class FlightUpdate(UpdateView):
    """ update a flight """

    model = Flight
    form_class = FlightForm
