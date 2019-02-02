from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

import os


CURRENCY_CHOICES = (
    ('PLN', 'PLN Polish Złoty'),
    ('USD', 'USD Dollar'),
    ('EUR', 'EUR Euro'),
    ('GBP', 'GBP British Pound')
)

MAX_TRAVEL_DAYS = 70


def travel_upload_location(instance, filename):
    fname, ext = os.path.splitext(filename)
    return "travels/{id}{ext}".format(id=instance.id, ext=ext)


def flight_upload_location(instance, filename):
    fname, ext = os.path.splitext(filename)
    flight = instance.flight_number.replace(" ", "")
    return "flight/{id}_{flight}{ext}".format(id=instance.id,
                                              flight=flight,
                                              ext=ext)


class Travel(models.Model):
    """ main travels model """

    country = models.ManyToManyField('Country', related_name='countries')
    start_date = models.DateField()
    end_date = models.DateField()
    key_photo = models.ImageField(upload_to=travel_upload_location,
                                  blank=True, null=True)
    notes = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        str = "#{} {} -> {}".format(self.pk, self.start_date, self.end_date)
        return str

    @property
    def time_delta(self):
        delta = self.end_date - self.start_date
        return delta.days

    def get_absolute_url(self):
        return reverse('travels:travel-detail', kwargs={'pk': self.pk})
    
    def save(self, *args, **kwargs):
        if self.pk:
            this_record = Travel.objects.get(pk=self.pk)
            if this_record.key_photo != self.key_photo:
                this_record.key_photo.delete(save=False)
        super(Travel, self).save(*args, **kwargs)

    def clean(self):
        delta = self.end_date - self.start_date
        
        if self.start_date > self.end_date:
            raise ValidationError({'start_date':
                                   _("start later than end")})
        if delta.days > MAX_TRAVEL_DAYS:
            raise ValidationError({'start_date':
                                   _("travel time exceeded")})
    

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
                                   _('start later than end')})


class Journey(models.Model):
    """ journeys """

    travel = models.ForeignKey('Travel', on_delete=models.CASCADE)
    start_date = models.DateField()
    start_time = models.TimeField(blank=True, null=True)
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
        return reverse('travels:travel-detail',
                       kwargs={'pk': self.travel.pk}) + '#jrn'


class Flight(models.Model):
    """ flights """

    travel = models.ForeignKey('Travel', blank=True,
                               null=True, on_delete=models.SET_NULL)
    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    orig = models.ForeignKey('Airport',
                             related_name='orig',
                             blank=True, null=True,
                             on_delete=models.SET_NULL)
    dest = models.ForeignKey('Airport',
                             related_name='dest',
                             blank=True, null=True,
                             on_delete=models.SET_NULL)
    flight_number = models.CharField(max_length=20, blank=True, null=True)
    airline = models.ForeignKey('Airline', blank=True, null=True,
                                related_name='airline',
                                on_delete=models.SET_NULL)
    distance = models.IntegerField(blank=True, null=True)
    duration = models.TimeField(blank=True, null=True)
    seat = models.CharField(max_length=6, blank=True, null=True)
    plane = models.CharField(max_length=40, blank=True, null=True)
    registration = models.CharField(max_length=20, blank=True, null=True)
    note = models.TextField(max_length=200, blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    currency = models.CharField(max_length=3, blank=True, null=True,
                                choices=CURRENCY_CHOICES)
    purchased = models.DateField(blank=True, null=True)
    boarding_pass = models.ImageField(upload_to=flight_upload_location,
                                      blank=True, null=True)

    def get_absolute_url(self):
        return reverse('travels:flight-detail',
                       kwargs={'pk': self.pk}) + '#fl'

    class Meta:
        ordering = ['date', 'time']
        
    def save(self, *args, **kwargs):
        if self.pk:
            this_record = Flight.objects.get(pk=self.pk)
            if this_record.boarding_pass != self.boarding_pass:
                this_record.boarding_pass.delete(save=False)
        super(Flight, self).save(*args, **kwargs)

    @property
    def purchase_delta(self):
        """ time difference between purchase and departure """

        if self.purchased:
            diff = self.date - self.purchased
            return diff.days

    def __str__(self):
        str = "{}, {} -> {}".format(self.date, self.orig, self.dest)
        return str

    def clean(self):
        if self.purchased and self.purchased > self.date:
            raise ValidationError({'purchased':
                                   _('purchase date later than fligth date')})


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


class Airline(models.Model):
    """ list of airlines """

    name = models.CharField(max_length=150)
    alias = models.CharField(max_length=50, blank=True, null=True)
    iata = models.CharField(max_length=3, blank=True, null=True)
    icao = models.CharField(max_length=5, blank=True, null=True)
    callsign = models.CharField(max_length=80, blank=True, null=True)
    country = models.CharField(max_length=80, blank=True, null=True)
    active = models.CharField(max_length=1, blank=True, null=True)

    def __str__(self):
        return "{} {}".format(self.name, self.country)
