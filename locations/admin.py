# Настройка встроенной админки Django. Регистрирую модели, настраиваю как они выглядят и редактируются в /admin.
from django.contrib import admin
from django import forms
from .models import Country, City, PinType, Location
from django.utils.text import slugify


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "slug"]
    search_fields = ["name", "code"]
    readonly_fields = ["slug"]

class CityAdminForm(forms.ModelForm):
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
        
        if country and slug:
            exists = City.objects.filter(country=country, slug=slug).exclude(pk=self.instance.pk).exists()
            if exists:
                self.add_error("name", f"Oops, {name} was already added to {country.name}!")
                #raise forms.ValidationError(f"City {name}' already exists in {country.name}")
        
        return cleaned_data

"""     def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["country"].choices = [
            ("", "<Select country>")
        ] + [
            (c.id, f"{c.flag} {c.name}")
            for c in Country.objects.all()
        ]

    class Meta:
        model = City
        fields = "__all__" """

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    form = CityAdminForm
    list_display = ["name", "country", "slug"]
    search_fields = ["name"]
    list_filter = ["country"]
    readonly_fields = ["slug"]
    autocomplete_fields = ["country"]


@admin.register(PinType)
class PinTypeAdmin(admin.ModelAdmin):
    list_display = ["name"]

class LocationAdminForm(forms.ModelForm):
    coordinates = forms.CharField(
        required=False,
        help_text="Paste coordinates from Google Maps, e.g. 47.18706, 9.32250",
        widget=forms.TextInput(attrs={"autocomplete": "off"})
    )

    class Meta:
        model = Location
        fields = "__all__"
        exclude = ["lat", "lng"]
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "off"}),
            "address": forms.TextInput(attrs={"autocomplete": "off"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        coordinates = cleaned_data.get("coordinates")
        if coordinates:
            try:
                lat, lng = [c.strip() for c in coordinates.split(",")]
                cleaned_data["lat"] = round(float(lat), 5) # 5 precision is plenty
                cleaned_data["lng"] = round(float(lng), 5)
            except (ValueError, AttributeError):
                self.add_error("coordinates", "Invalid format. Use: 47.18706, 9.32250")
        return cleaned_data
    
    def save(self, commit=True):
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
    search_fields = ["name", "description", "address"]
    list_filter = ["city__country", "pin_types"]
    filter_horizontal = ["pin_types"]
    readonly_fields = ["lat", "lng", "created_at", "updated_at"]
    autocomplete_fields = ["city"]
    fieldsets = [
        (None, {"fields": ["city", "name", "description", "address"]}),
        ("Location", {"fields": ["coordinates", "lat", "lng", "google_maps_url"]}),
        ("Pin types", {"fields": ["pin_types"]}),
        ("Meta", {"fields": ["created_at", "updated_at"]}),
    ]