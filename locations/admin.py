# Настройка встроенной админки Django. Регистрирую модели, настраиваю как они выглядят и редактируются в /admin.
from django.contrib import admin
from django import forms
from .models import Country, City, PinType, Location, LocationSubmission
from django.utils.text import slugify


# --- COUNTRIES ---

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "slug", "city_count"]
    search_fields = ["name", "code"]
    readonly_fields = ["slug"]  # slug генерируется автоматически из name, руками не редактируется

    def city_count(self, obj):
        # считает сколько городов есть внутри каждой страны
        return obj.cities.count()
    city_count.short_description = "Cities"


# --- CITIES ---

class CityAdminForm(forms.ModelForm):
    """Кастомная форма города: запрещает добавить дубликат города в ту же страну"""

    class Meta:
        model = City
        fields = "__all__"
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "off"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        country = cleaned_data.get("country")
        name = cleaned_data.get("name")
        slug = slugify(name) if name else ""

        # проверяем уникальность по паре country+slug (не глобально)
        if country and slug:
            exists = City.objects.filter(country=country, slug=slug).exclude(pk=self.instance.pk).exists()
            if exists:
                self.add_error("name", f"Oops, {name} was already added to {country.name}!")

        return cleaned_data

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    form = CityAdminForm
    list_display = ["name", "country", "slug", "is_capital", "location_count"]
    search_fields = ["name"]
    list_filter = ["country"]
    readonly_fields = ["slug"]  # slug генерируется автоматически из name
    autocomplete_fields = ["country"]  # поиск страны по названию вместо огромного дропдауна

    def get_queryset(self, request):
        # select_related избегает N+1: достаём города сразу с их странами одним JOIN запросом
        return super().get_queryset(request).select_related("country")

    def location_count(self, obj):
        # показывает сколько pin locations добавлено в этом городе
        return obj.locations.count()
    location_count.short_description = "Locations"


# --- LOCATIONS ---

class LocationAdminForm(forms.ModelForm):
    """Кастомная форма локации: поле coordinates парсит lat/lng из формата Google Maps"""

    coordinates = forms.CharField(
        required=False,
        help_text="Paste coordinates from Google Maps, e.g. 47.18706, 9.32250",
        widget=forms.TextInput(attrs={"autocomplete": "off"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # при редактировании существующей локации показываем текущие координаты в поле
        if self.instance and self.instance.lat and self.instance.lng:
            self.fields["coordinates"].initial = f"{self.instance.lat}, {self.instance.lng}"

    class Meta:
        model = Location
        fields = "__all__"
        exclude = ["lat", "lng"]  # скрываем сырые поля, координаты вводятся через поле coordinates выше
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "off"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        coordinates = cleaned_data.get("coordinates")
        if coordinates:
            try:
                # парсим строку "lat, lng" → два отдельных float
                lat, lng = [c.strip() for c in coordinates.split(",")]
                cleaned_data["lat"] = round(float(lat), 5)  # 5 знаков после запятой достаточно
                cleaned_data["lng"] = round(float(lng), 5)
            except (ValueError, AttributeError):
                self.add_error("coordinates", "Invalid format. Use: 47.18706, 9.32250")
        return cleaned_data

    def save(self, commit=True):
        # записываем распарсенные lat/lng в инстанс вручную (они exclude'd из Meta.fields)
        instance = super().save(commit=False)
        instance.lat = self.cleaned_data.get("lat")
        instance.lng = self.cleaned_data.get("lng")
        if commit:
            instance.save()
        return instance

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    form = LocationAdminForm
    list_display = ["name", "city", "created_at"]
    search_fields = ["name", "description"]
    list_filter = ["pin_types"]
    filter_horizontal = ["pin_types"]  # удобный двойной список для выбора типов пинов
    readonly_fields = ["lat", "lng", "created_at", "updated_at"]  # координаты редактируются только через поле coordinates
    autocomplete_fields = ["city"]
    fieldsets = [
        (None, {"fields": ["city", "name", "description"]}),
        ("Location", {"fields": ["google_maps_url", "coordinates", "lat", "lng"]}),
        ("Pin types", {"fields": ["pin_types"]}),
        ("Meta", {"fields": ["created_at", "updated_at"]}),
    ]

    def get_fieldsets(self, request, obj=None):
        # поле yandex_maps_url нужно только для локаций в России, поэтому не показываем
        # его в форме для всех остальных стран, чтобы не захламлять админку
        fieldsets = super().get_fieldsets(request, obj)
        if obj and obj.city.country.code == "RU":
            fieldsets = [
                (title, {**opts, "fields": (
                    [*opts["fields"], "yandex_maps_url"] if title == "Location" else opts["fields"]
                )})
                for title, opts in fieldsets
            ]
        return fieldsets

    def get_queryset(self, request):
        # select_related избегает N+1: достаём локации сразу с их городами одним JOIN запросом
        return super().get_queryset(request).select_related("city", "city__country")


# --- PIN TYPES ---

@admin.register(PinType)
class PinTypeAdmin(admin.ModelAdmin):
    list_display = ["name"]


# --- SUBMISSIONS (заявки от пользователей) ---

@admin.register(LocationSubmission)
class LocationSubmissionAdmin(admin.ModelAdmin):
    list_display = ["location_name", "city_name", "country_name", "status", "created_at"]
    list_filter = ["status", "has_city_pins", "has_country_pins", "has_place_pins"]
    search_fields = ["location_name", "city_name", "country_name"]
    readonly_fields = ["created_at"]
    list_editable = ["status"]  # статус можно менять прямо в списке без захода в каждую запись