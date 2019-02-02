from django import forms
from django.contrib.admin import widgets

from dal.autocomplete import ModelSelect2Multiple, ModelSelect2

from .models import Place, Country, Travel, Journey, Airport,\
    Flight, Airline


class TravelForm(forms.ModelForm):

    start_date = forms.DateField(widget=widgets.AdminDateWidget(),
                                 localize=False)
    end_date = forms.DateField(widget=widgets.AdminDateWidget(),
                               localize=False)
    
    class Meta:
        model = Travel
        fields = ['country', 'start_date', 'end_date', 'notes', 'key_photo']
        widgets = {'country': ModelSelect2Multiple(
            url='travels:country-autocomplete',
            attrs={'class': 'form-control'})
        }

    class Media:
        js = ('admin/js/vendor/jquery/jquery.js',
              'admin/js/core.js')
        css = {'all': ('admin/css/forms.css',)}
        

class PlaceForm(forms.ModelForm):

    def __init__(self, *args, session_data=None, **kwargs):
        super().__init__(*args, **kwargs)

        country_ids = []

        for country in Travel.objects.get(pk=session_data['travel'])\
                                     .country.all():
            country_ids.append(country.pk)

        # get counties only for that travel
        self.fields['country'].queryset = self.fields['country']\
                                              .queryset\
                                              .filter(pk__in=country_ids)\
                                              .order_by('pk')

    start_date = forms.DateField(widget=widgets.AdminDateWidget(),
                                 localize=False)
    end_date = forms.DateField(widget=widgets.AdminDateWidget(),
                               localize=False)
    country = forms.ModelChoiceField(Country.objects.all(), empty_label=None)
    notes = forms.CharField(required=False,
                            widget=forms.Textarea(attrs={'cols': 35,
                                                         'rows': 4,
                                                         'maxlength': 150}))
    
    class Meta:
        model = Place
        fields = ['start_date', 'end_date', 'country', 'city',
                  'place', 'gps', 'notes']

    class Media:
        js = ('admin/js/vendor/jquery/jquery.js',
              'admin/js/core.js')
        css = {'all': ('admin/css/forms.css',)}


class JourneyForm(forms.ModelForm):

    start_date = forms.DateField(widget=widgets.AdminDateWidget(),
                                 localize=False)
    end_date = forms.DateField(widget=widgets.AdminDateWidget(),
                               localize=False,
                               required=False)
    start_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M'),
                                 input_formats=['%H:%M'],
                                 required=False)
    notes = forms.CharField(required=False,
                            widget=forms.Textarea(attrs={'cols': 35,
                                                         'rows': 4,
                                                         'maxlength': 150}))

    field_order = ['start_date', 'start_time', 'end_date', 'transport_type',
                   'orig', 'dest', 'notes']
    
    class Meta:
        model = Journey
        fields = ['start_date', 'start_time', 'end_date', 'orig', 'dest',
                  'notes', 'transport_type']

    class Media:
        js = ('admin/js/vendor/jquery/jquery.js',
              'admin/js/core.js')
        css = {'all': ('admin/css/forms.css',)}


class FlightForm(forms.ModelForm):

    purchased = forms.DateField(
        widget=widgets.AdminDateWidget(), localize=False, required=False)
    date = forms.DateField(
        widget=widgets.AdminDateWidget(), localize=False)
    time = forms.TimeField(widget=forms.TimeInput(format='%H:%M'),
                           input_formats=['%H:%M'],
                           required=False)

    field_order = ['travel', 'date', 'time', 'orig', 'dest', 'airline',
                   'flight_number', 'plane', 'registration',
                   'seat', 'distance', 'duration', 'currency',
                   'price', 'purchased', 'note']
    
    class Meta:
        model = Flight
        fields = '__all__'
        widgets = {'orig': ModelSelect2(url='travels:airport-autocomplete',
                                        attrs={'class': 'form-control'}),
                   'dest': ModelSelect2(url='travels:airport-autocomplete',
                                        attrs={'class': 'form-control'}),
                   'airline': ModelSelect2(url='travels:airline-autocomplete',
                                           attrs={'class': 'form-control'})}

    class Media:
        js = ('admin/js/vendor/jquery/jquery.js',
              'admin/js/core.js')
        css = {'all': ('admin/css/forms.css',)}


class FlightSearchForm(forms.ModelForm):
    """ flight search form """

    # def __init__(self, *args, session_data=None, **kwargs):
        # super().__init__(*args, **kwargs)

        # orig_ids = Flight.objects.values_list('orig', flat=True)
        # dest_ids = Flight.objects.values_list('dest', flat=True)
        # airline_ids = Flight.objects.values_list('airline', flat=True)
        
        # self.fields['orig'] = forms.ModelChoiceField(
            # queryset=Airport.objects.filter(pk__in=set(orig_ids)),
            # label="from",
            # required=False)

        # self.fields['dest'] = forms.ModelChoiceField(
            # queryset=Airport.objects.filter(pk__in=set(dest_ids)),
            # label="to",
            # required=False)

        # self.fields['airline'] = forms.ModelChoiceField(
            # queryset=Airline.objects.filter(pk__in=set(airline_ids)),
            # label="airline",
            # required=False)

    flight_number = forms.CharField(required=False,
                                    widget=forms.TextInput(attrs={
                                        'autofocus': True,
                                        'tabindex': 1}))

    class Meta:
        model = Flight
        fields = ['orig', 'dest', 'airline', 'flight_number']
        widgets = {'orig': ModelSelect2(url='travels:airport-autocomplete',
                                        attrs={'class': 'form-control',
                                               'tabindex': 2}),
                   'dest': ModelSelect2(url='travels:airport-autocomplete',
                                        attrs={'class': 'form-control',
                                               'tabindex': 3}),
                   'airline': ModelSelect2(url='travels:airline-autocomplete',
                                           attrs={'class': 'form-control',
                                                  'tabindex': 4})}

    class Media:
        js = ('admin/js/vendor/jquery/jquery.js',
              'admin/js/core.js')
        css = {'all': ('admin/css/forms.css',)}
