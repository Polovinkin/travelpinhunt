from django.shortcuts import render, get_object_or_404
from .models import Country, City, Location

def home(request):
    countries = Country.objects.all().order_by("name")
    return render(request, "locations/home.html", {"countries": countries})

def country_detail(request, country_slug):
    country = get_object_or_404(Country, slug=country_slug)
    cities = City.objects.filter(country=country).order_by("name")
    return render(request, "locations/country_detail.html", {"country": country, "cities": cities})

def city_detail(request, country_slug, city_slug):
    country = get_object_or_404(Country, slug=country_slug)
    city = get_object_or_404(City, slug=city_slug, country=country)
    locations = Location.objects.filter(city=city)
    return render(request, "locations/city_detail.html", {"city": city, "locations": locations})