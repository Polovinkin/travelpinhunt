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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["country"].choices = [
            ("", "<Select country>")
        ] + [
            (c.id, f"{c.flag} {c.name}")
            for c in Country.objects.all()
        ]

    class Meta:
        model = City
        fields = "__all__"

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    form = CityAdminForm
    list_display = ["name", "country", "slug"]
    search_fields = ["name"]  # это обязательно для autocomplete
    list_filter = ["country"]
    readonly_fields = ["slug"]


@admin.register(PinType)
class PinTypeAdmin(admin.ModelAdmin):
    list_display = ["name"]

class LocationAdminForm(forms.ModelForm):
    coordinates = forms.CharField(
        required=False,
        help_text="Paste coordinates from Google Maps, e.g. 13.744752, 100.530031"
    )

    class Meta:
        model = Location
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        coordinates = cleaned_data.get("coordinates")
        if coordinates:
            try:
                lat, lng = [c.strip() for c in coordinates.split(",")]
                cleaned_data["lat"] = float(lat)
                cleaned_data["lng"] = float(lng)
            except (ValueError, AttributeError):
                self.add_error("coordinates", "Invalid format. Use: 13.744752, 100.530031")
        return cleaned_data


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    form = LocationAdminForm
    list_display = ["name", "city", "verified", "created_at"]
    search_fields = ["name", "description", "address"]
    list_filter = ["verified", "city__country", "pin_types"]
    filter_horizontal = ["pin_types"]
    readonly_fields = ["lat", "lng"]
    autocomplete_fields = ["city"]