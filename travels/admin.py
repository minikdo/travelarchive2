from django.contrib import admin
from .models import Travel, Place, Country, Journey, Transport,\
    Flight, Airport

# Register your models here.
admin.site.register(Travel)
admin.site.register(Place)
admin.site.register(Country)
admin.site.register(Journey)
admin.site.register(Transport)
admin.site.register(Flight)
admin.site.register(Airport)
