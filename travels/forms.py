from django import forms

from dal.autocomplete import ModelSelect2Multiple, ModelSelect2
from datetime import date

from .models import Place, Country, Travel, Journey, Airport,\
    Flight


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

    start_date = forms.DateField(
        widget=forms.DateInput(format='%Y-%m-%d',
                               attrs={'autofocus': True}),
        input_formats=['%Y-%m-%d'])
    end_date = forms.DateField(initial="",
                               widget=forms.DateInput(format='%Y-%m-%d'),
                               input_formats=['%Y-%m-%d'])
    country = forms.ModelChoiceField(Country.objects.all(), empty_label=None)
    notes = forms.CharField(required=False,
                            widget=forms.Textarea(attrs={'cols': 35,
                                                         'rows': 4,
                                                         'maxlength': 150}))
    
    class Meta:
        model = Place
        fields = ['start_date', 'end_date', 'country', 'city',
                  'place', 'gps', 'notes']


class TravelForm(forms.ModelForm):

    from django.contrib.admin import widgets
    start_date = forms.DateField(widget=widgets.AdminDateWidget(),
                                 localize=False)
    end_date = forms.DateField(widget=widgets.AdminDateWidget(),
                               localize=False)
    # start_date = forms.DateField(initial=date.today(),
                                 # widget=forms.DateInput(format='%Y-%m-%d'),
                                 # input_formats=['%Y-%m-%d'])
    # end_date = forms.DateField(initial=date.today(),
                               # widget=forms.DateInput(format='%Y-%m-%d'),
                               # input_formats=['%Y-%m-%d'])
    
    class Meta:
        model = Travel
        fields = ['country', 'start_date', 'end_date', 'notes']
        widgets = {'country': ModelSelect2Multiple(
            url='travels:country-autocomplete',
            attrs={'class': 'form-control'})
        }

    class Media:
        js = ('admin/js/vendor/jquery/jquery.js',
              'admin/js/core.js')
        css = {'all': ('admin/css/forms.css',)}
        

class JourneyForm(forms.ModelForm):

    # def __init__(self, *args, session_data=None, **kwargs):
        # super().__init__(*args, **kwargs)
    
    start_date = forms.DateField(
        widget=forms.DateInput(format='%Y-%m-%d',
                               attrs={'autofocus': True}),
        input_formats=['%Y-%m-%d'])
    end_date = forms.DateField(widget=forms.DateInput(format='%Y-%m-%d'),
                               input_formats=['%Y-%m-%d'],
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


class FlightForm(forms.ModelForm):

    date = forms.DateTimeField(
        widget=forms.DateTimeInput(format='%Y-%m-%d %H:%M',
                                   attrs={'autofocus': True}),
        input_formats=['%Y-%m-%d %H:%M'])
    purchased = forms.DateField(
        widget=forms.DateInput(format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d'],
        required=False)

    field_order = ['travel', 'date', 'orig', 'dest', 'airline',
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
        

class FlightSearchForm(forms.Form):
    """ flight search form """

    orig = forms.ModelChoiceField(
        queryset=Airport.objects.exclude(orig=None).order_by('city'),
        label="from",
        required=False)
    dest = forms.ModelChoiceField(
        queryset=Airport.objects.exclude(dest=None).order_by('city'),
        label="to",
        required=False)
    # airline = forms.ModelChoiceField(
        # queryset=Flight.objects.distinct('airline')
    # )
