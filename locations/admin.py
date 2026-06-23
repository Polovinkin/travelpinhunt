from django.contrib import admin
from django import forms
from .models import Country, City, PinType, Location


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "slug"]
    search_fields = ["name", "code"]
    readonly_fields = ["slug"]

class CityAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["country"].choices = [
            ("", "---------")
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
    search_fields = ["name"]
    list_filter = ["country"]
    readonly_fields = ["slug"]


@admin.register(PinType)
class PinTypeAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ["name", "city", "verified", "created_at"]
    search_fields = ["name", "description", "address"]
    list_filter = ["verified", "city__country", "pin_types"]
    filter_horizontal = ["pin_types"]