# Логика страниц. Каждая функция получает запрос, достаёт данные из БД и возвращает HTML. Мозг приложения.
from django.shortcuts import render, get_object_or_404, redirect
from .models import Country, State, City, Location, LocationSubmission
from .forms import LocationSubmissionForm
from django.db.models import Count
from django.views.decorators.cache import never_cache
import requests
from django.conf import settings


def home(request):
    # только страны у которых есть хотя бы одна локация (не показываем пустые)
    countries = Country.objects.filter(
        cities__locations__isnull=False
    ).distinct().order_by("name")

    query = request.GET.get("q", "").strip()
    results = []

    # последняя добавленная локация для плитки "Last added" на главной
    latest_location = Location.objects.select_related(
        "city", "city__country", "city__state"
    ).order_by("-created_at").first()

    location_count = Location.objects.count()
    country_count = countries.count()

    if query:
        # ищем по вхождению строки в название города или страны (case-insensitive)
        cities = City.objects.filter(
            name__icontains=query
        ).select_related("country", "state")

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

    if country.has_states:
        # "штатные" страны (например США): сначала показываем штаты, в которых есть
        # хотя бы один город с добавленными локациями — как на главной для стран
        states = State.objects.filter(country=country).annotate(
            location_count=Count("cities__locations", distinct=True),
        ).filter(location_count__gt=0).order_by("name")
        return render(request, "locations/country_detail.html", {
            "country": country,
            "states": states,
            "page_country_slug": country.slug,
        })

    cities = City.objects.filter(country=country).annotate(location_count=Count("locations")).order_by("name")
    return render(request, "locations/country_detail.html", {
        "country": country,
        "cities": cities,
        "page_country_slug": country.slug,
    })


def country_child_detail(request, country_slug, second_slug):
    # Второй сегмент URL — это либо штат (для стран с has_states=True), либо сразу город.
    country = get_object_or_404(Country, slug=country_slug)

    if country.has_states:
        return state_detail(request, country, second_slug)

    return city_detail(request, country, second_slug)


def state_detail(request, country, state_slug):
    state = get_object_or_404(State, slug=state_slug, country=country)
    cities = City.objects.filter(state=state).select_related("country", "state").annotate(
        location_count=Count("locations")
    ).order_by("name")
    return render(request, "locations/state_detail.html", {
        "country": country,
        "state": state,
        "cities": cities,
        "page_country_slug": country.slug,
    })


def city_detail(request, country, city_slug, state=None):
    # slug города уникален в рамках штата (если есть) или страны (если штатов нет)
    lookup = {"slug": city_slug, "country": country}
    if state is not None:
        lookup["state"] = state
    city = get_object_or_404(City, **lookup)
    locations = Location.objects.filter(city=city)
    return render(request, "locations/city_detail.html", {
        "city": city,
        "locations": locations,
        "page_country_slug": country.slug,
    })


def city_detail_in_state(request, country_slug, state_slug, city_slug):
    # Полный трёхсегментный URL /country/state/city/ — только для "штатных" стран
    country = get_object_or_404(Country, slug=country_slug)
    state = get_object_or_404(State, slug=state_slug, country=country)
    return city_detail(request, country, city_slug, state=state)

@never_cache  # форма не должна кешироваться — иначе браузер может показать старые данные после сабмита
def submit_location(request):
    if request.method == "POST":
        form = LocationSubmissionForm(request.POST)

        # Проверяем Turnstile токен через Cloudflare API
        token = request.POST.get('cf-turnstile-response', '')
        turnstile_ok = False
        if token:
            try:
                cf_response = requests.post(
                    'https://challenges.cloudflare.com/turnstile/v0/siteverify',
                    data={
                        'secret': settings.TURNSTILE_SECRET_KEY,
                        'response': token,
                        'remoteip': request.META.get('REMOTE_ADDR'),
                    },
                    timeout=5,
                )
                turnstile_ok = cf_response.json().get('success', False)
            except requests.RequestException:
                turnstile_ok = False

        if form.is_valid() and turnstile_ok:
            form.save()
            return redirect("locations:submit_success")

        if not turnstile_ok:
            form.add_error(None, 'Captcha check failed. Please try again.')

    else:
        form = LocationSubmissionForm()

    return render(request, "locations/submit_location.html", {
        "form": form,
        "TURNSTILE_SITE_KEY": settings.TURNSTILE_SITE_KEY,
    })


@never_cache  # аналогично — страница успеха не должна открываться повторно из кеша
def submit_success(request):
    return render(request, "locations/submit_success.html")


def contributors(request):
    # Никнеймы контрибьюторов, у кого хотя бы одна заявка одобрена (Approved).
    # Считаем сколько одобренных заявок у каждого никнейма, сортируем по убыванию.
    contributors_list = (
        LocationSubmission.objects
        .filter(status=LocationSubmission.APPROVED)
        .exclude(contributor_nickname="")
        .values("contributor_nickname")
        .annotate(submission_count=Count("id"))
        .order_by("-submission_count", "contributor_nickname")
    )
    return render(request, "locations/contributors.html", {
        "contributors_list": contributors_list,
    })