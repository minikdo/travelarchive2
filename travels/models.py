from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Travel(models.Model):
    """ main travels model """

    country = models.ManyToManyField('Country')
    start_date = models.DateField()
    end_date = models.DateField()
    notes = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        str = "#{} {} -> {}".format(self.pk, self.start_date, self.end_date)
        return str

    def get_absolute_url(self):
        return reverse('travels:travel-detail', kwargs={'pk': self.pk})
    

class Place(models.Model):
    """ places (hotels, cities visited, etc.) """

    travel = models.ForeignKey('Travel', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    country = models.ForeignKey('Country', null=True,
                                on_delete=models.SET_NULL)
    city = models.CharField(max_length=50, blank=True, null=True)
    place = models.CharField(max_length=50, blank=True, null=True)
    gps = models.CharField(max_length=30, blank=True, null=True)
    notes = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        ordering = ['start_date']
        
    def __str__(self):
        str = "{} {} -> {}".format(self.city, self.start_date, self.end_date)
        return str

    def get_absolute_url(self):
        return reverse('travels:travel-detail', kwargs={'pk': self.travel.pk})

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError({'start_date':
                                   _('test Date not within travel dates')})


class Journey(models.Model):
    """ journeys """

    travel = models.ForeignKey('Travel', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    orig = models.CharField(max_length=50)
    dest = models.CharField(max_length=50)
    notes = models.CharField(max_length=150, blank=True, null=True)
    transport_type = models.ForeignKey('Transport', null=True,
                                       on_delete=models.SET_NULL)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        str = "{} {} {} {}".format(self.start_date, self.end_date,
                                   self.orig, self.dest)
        return str

    def get_absolute_url(self):
        return reverse('travels:travel-detail', kwargs={'pk': self.travel.pk})


class Flight(models.Model):
    """ flights """

    travel = models.ForeignKey('Travel', null=True, on_delete=models.SET_NULL)
    date = models.DateTimeField()
    orig = models.ForeignKey('Airport',
                             related_name='orig',
                             blank=True, null=True,
                             on_delete=models.SET_NULL)
    dest = models.ForeignKey('Airport',
                             related_name='dest',
                             blank=True, null=True,
                             on_delete=models.SET_NULL)
    flight_number = models.CharField(max_length=20, blank=True, null=True)
    airline = models.CharField(max_length=40, blank=True, null=True)
    distance = models.IntegerField(blank=True, null=True)
    duration = models.TimeField(blank=True, null=True)
    seat = models.CharField(max_length=6, blank=True, null=True)
    plane = models.CharField(max_length=40, blank=True, null=True)
    registration = models.CharField(max_length=10, blank=True, null=True)
    note = models.CharField(max_length=100, blank=True, null=True)
    airline_oid = models.CharField(max_length=10, blank=True, null=True)

    def get_absolute_url(self):
        return reverse('travels:flight-detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['date']
    
    @property
    def note_sign(self):
        """ display * when there is a note """

        if self.note:
            return "*"
        return ""
    
    @property
    def distance_in_km(self):
        """ convert miles to km """
        
        return round(self.distance/0.62137)
    
    def __str__(self):
        str = "{}, {} -> {}".format(self.date, self.orig, self.dest)
        return str


class Transport(models.Model):
    """ types of transport (car, train, bus, taxi, on foot) """
    
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Country(models.Model):
    """ countries """

    country_name = models.CharField(max_length=50)
    capital_name = models.CharField(max_length=25)
    capital_lat = models.CharField(max_length=20)
    capital_lon = models.CharField(max_length=20)
    country_code = models.CharField(max_length=6)
    continent_name = models.CharField(max_length=16)
    sort_order = models.IntegerField()

    class Meta:
        ordering = ['country_name']
        verbose_name_plural = "countries"

    def __str__(self):
        return self.country_name


class Airport(models.Model):
    """ list of airports """
    
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=40)
    iata = models.CharField(max_length=3)
    icao = models.CharField(max_length=4)
    lat = models.CharField(max_length=30)
    lon = models.CharField(max_length=30)
    timezone = models.CharField(max_length=7)
    dst = models.CharField(max_length=1)
    alt = models.IntegerField()

    class Meta:
        ordering = ['country', 'city']
    
    @property
    def alt_in_meters(self):
        return round(self.alt/3.2808)
    
    def __str__(self):
        str = "{}, {}, {}, {}".format(self.country, self.city,
                                      self.name, self.iata)
        return str
