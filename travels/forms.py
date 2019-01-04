from django import forms

from .models import Place, Country, Travel


class PlaceForm(forms.ModelForm):

    def __init__(self, *args, session_data=None, **kwargs):
        super().__init__(*args, **kwargs)

        country_ids = []
        
        for country in Travel.objects.get(pk=19).country.all():
            country_ids.append(country.pk)

        # get counties only for that travel
        self.fields['country'].queryset = self.fields['country']\
                                              .queryset\
                                              .filter(pk__in=country_ids)\
                                              .order_by('pk')

    start_date = forms.DateField(widget=forms.DateInput(format='%Y-%m-%d'),
                                 input_formats=['%Y-%m-%d'])
    end_date = forms.DateField(initial="",
                               widget=forms.DateInput(format='%Y-%m-%d'),
                               input_formats=['%Y-%m-%d'])
    country = forms.ModelChoiceField(Country.objects.all(), empty_label=None)
    notes = forms.CharField(widget=forms.Textarea(attrs={'cols': 35,
                                                         'rows': 4,
                                                         'maxlength': 150}))
    
    class Meta:
        model = Place
        fields = ['start_date', 'end_date', 'country', 'city',
                  'place', 'gps', 'notes']
