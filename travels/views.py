from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView,\
    FormMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q, Count
# from django.http import HttpResponse

from dal.autocomplete import Select2QuerySetView

from .models import Travel, Place, Journey, Flight, Country, Airport, Airline
from .forms import (PlaceForm, TravelForm, JourneyForm,
                    FlightSearchForm, FlightForm)

import datetime


class IndexView(ListView):
    """ list of travels """

    model = Travel
    paginate_by = 40

    def get_queryset(self):
        qs = Travel.objects.all().prefetch_related('country')

        if self.request.method == 'GET':
            country = self.request.GET.get('country', None)
            try:
                country = int(country)
            except Exception:  # FIXME
                pass
            else:
                qs = qs.filter(country=country)

        return qs


class CountryView(TemplateView):
    """ country statistics """

    template_name = 'travels/country.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['countries'] = Country.objects.filter(
            countries__in=Travel.objects.all()).annotate(
                Count('countries')).order_by('continent_name',
                                             'country_name')
        context['total'] = context['countries'].count()
        return context


class TravelDetailView(TemplateView):

    template_name = 'travels/travel_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        travel = self.kwargs['pk']

        context['travel'] = get_object_or_404(Travel, pk=travel)
        context['places'] = Place.objects\
                                 .filter(travel__pk=travel)\
                                 .prefetch_related('country')
        context['journeys'] = Journey.objects\
                                     .filter(travel__pk=travel)\
                                     .prefetch_related('transport_type')
        context['flights'] = Flight.objects\
                                   .filter(travel__pk=travel)\
                                   .prefetch_related('orig', 'dest', 'airline')
        return context


class TravelCreate(LoginRequiredMixin, CreateView):
    """ add a travel """

    model = Travel
    form_class = TravelForm


class TravelUpdate(LoginRequiredMixin, UpdateView):
    """ edit travel """

    model = Travel
    form_class = TravelForm


class PlaceCreate(LoginRequiredMixin, CreateView):
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
            country = queryset.country

        return {'start_date': start_date,
                'end_date': end_date,
                'country': country}


class PlaceUpdate(LoginRequiredMixin, UpdateView):
    """ edit place """

    model = Place
    form_class = PlaceForm

    def get_form_kwargs(self):  # FIXME repeated
        travel = Place.objects.get(pk=self.kwargs.get('pk')).travel.pk
        kwargs = super().get_form_kwargs()
        kwargs.update(session_data={'travel': travel})
        return kwargs


class PlaceDelete(LoginRequiredMixin, DeleteView):
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


class JourneyCreate(LoginRequiredMixin, CreateView):
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


class JourneyUpdate(LoginRequiredMixin, UpdateView):
    """ edit journey """

    model = Journey
    form_class = JourneyForm


class JourneyDelete(LoginRequiredMixin, DeleteView):
    """ delete a journey """

    model = Journey

    def get_success_url(self):
        travel = self.object.travel
        return reverse_lazy('travels:travel-detail',
                            kwargs={'pk': travel.pk})


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
        if self.airline:
            query = query.filter(airline=self.airline)
        if self.flight_number:
            query = query.filter(flight_number__icontains=self.flight_number)

        query = query.prefetch_related('orig', 'dest', 'airline')

        return query.order_by('-date', '-time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['count'] = self.object_list.count()

        from django.db.models import Sum
        context['total_distance'] = Flight.objects.all()\
                                                  .aggregate(Sum('distance'))
        return context

    def get_initial(self):
        initials = {}

        if self.orig:
            initials['orig'] = self.orig
        if self.dest:
            initials['dest'] = self.dest
        if self.airline:
            initials['airline'] = self.airline
        if self.flight_number:
            initials['flight_number'] = self.flight_number

        return initials

    def dispatch(self, request, *args, **kwargs):

        self.orig = request.GET.get('orig', None)
        self.dest = request.GET.get('dest', None)
        self.airline = request.GET.get('airline', None)
        self.flight_number = request.GET.get('flight_number', None)
        return super().dispatch(request, *args, **kwargs)


class FlightDetailView(DetailView):
    """ flight details """

    model = Flight


class FlightCreate(LoginRequiredMixin, CreateView):
    """ create a flight """

    model = Flight
    form_class = FlightForm

    def form_valid(self, form):  # FIXME repeated
        form.instance.travel_id = self.kwargs.get('travel')
        return super().form_valid(form)

    def get_initial(self):
        return {'travel': self.kwargs.get('travel')}


class FlightUpdate(LoginRequiredMixin, UpdateView):
    """ update a flight """

    model = Flight
    form_class = FlightForm


class FlightDelete(LoginRequiredMixin, DeleteView):
    """ delete a flight """

    model = Flight

    def get_success_url(self):
        travel = self.object.travel
        return reverse_lazy('travels:travel-detail',
                            kwargs={'pk': travel.pk})


class FlightStatsView(TemplateView):

    template_name = 'travels/flight_stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['airlines'] = Flight.objects.values('airline__name')\
                                            .annotate(count=Count('airline'))\
                                            .order_by('-count')[:15]
        context['origs'] = Flight.objects.values('orig__city', 'orig__name')\
                                         .annotate(count=Count('orig'))\
                                         .order_by('-count')[:15]
        context['longest'] = Flight.objects.order_by('-distance').first()
        context['shortest'] = Flight.objects.order_by('distance').first()

        return context


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
            qs = qs.filter(Q(iata__contains=self.q) |
                           Q(city__startswith=self.q))

        return qs


class AirlineAutocomplete(Select2QuerySetView):

    def get_queryset(self):

        qs = Airline.objects.all()

        if self.q:
            qs = qs.filter(Q(name__istartswith=self.q))

        return qs
