# Логика страниц. Каждая функция получает запрос, достаёт данные из БД и возвращает HTML. Мозг приложения.
from django.shortcuts import render, get_object_or_404, redirect
from .models import Country, City, Location
from .forms import LocationSubmissionForm
from django.views.decorators.cache import never_cache


def home(request):
    # только страны у которых есть хотя бы одна локация (не показываем пустые)
    countries = Country.objects.filter(
        cities__locations__isnull=False
    ).distinct().order_by("name")

    query = request.GET.get("q", "").strip()
    results = []

    # последняя добавленная локация для плитки "Last added" на главной
    latest_location = Location.objects.select_related(
        "city", "city__country"
    ).order_by("-created_at").first()

    location_count = Location.objects.count()
    country_count = countries.count()

    if query:
        # ищем по вхождению строки в название города или страны (case-insensitive)
        cities = City.objects.filter(
            name__icontains=query
        ).select_related("country")

        countries_found = Country.objects.filter(
            name__icontains=query
        )

        results = {
            "cities": cities,
            "countries": countries_found,
            "query": query,
        }

    return render(request, "locations/home.html", {
        "countries": countries,
        "results": results,
        "query": query,
        "latest_location": latest_location,
        "location_count": location_count,
        "country_count": country_count,
    })


def about(request):
    return render(request, "locations/about.html")


def country_detail(request, country_slug):
    # 404 если страна не найдена
    country = get_object_or_404(Country, slug=country_slug)
    cities = City.objects.filter(country=country).order_by("name")
    return render(request, "locations/country_detail.html", {
        "country": country,
        "cities": cities,
        "page_country_slug": country.slug,
    })


def city_detail(request, country_slug, city_slug):
    # slug города уникален в рамках страны, поэтому ищем по обоим
    country = get_object_or_404(Country, slug=country_slug)
    city = get_object_or_404(City, slug=city_slug, country=country)
    locations = Location.objects.filter(city=city)
    return render(request, "locations/city_detail.html", {
        "city": city,
        "locations": locations,
        "page_country_slug": country.slug,
    })

@never_cache  # форма не должна кешироваться — иначе браузер может показать старые данные после сабмита
def submit_location(request):
    if request.method == "POST":
        form = LocationSubmissionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("locations:submit_success")
    else:
        form = LocationSubmissionForm()

    return render(request, "locations/submit_location.html", {"form": form})


@never_cache  # аналогично — страница успеха не должна открываться повторно из кеша
def submit_success(request):
    return render(request, "locations/submit_success.html")