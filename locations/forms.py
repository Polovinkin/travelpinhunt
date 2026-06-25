from django import forms
from .models import LocationSubmission

INPUT_CLASS = "w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"
TEXTAREA_CLASS = "w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400 resize-none"

class LocationSubmissionForm(forms.ModelForm):
    class Meta:
        model = LocationSubmission
        fields = [
            "country_name",
            "city_name",
            "location_name",
            "google_maps_url",
            "description",
            "photo_url",
            "has_city_pins",
            "has_country_pins",
            "has_place_pins",
            "submitter_email",
        ]
        widgets = {
            "country_name": forms.TextInput(attrs={
                "placeholder": "e.g. Thailand",
                "autocomplete": "off",
                "maxlength": "30",
                "class": INPUT_CLASS,
            }),
            "city_name": forms.TextInput(attrs={
                "placeholder": "e.g. Chiang Mai",
                "autocomplete": "off",
                "maxlength": "50",
                "class": INPUT_CLASS,
            }),
            "location_name": forms.TextInput(attrs={
                "placeholder": "e.g. Night Bazaar Souvenir Shop",
                "autocomplete": "off",
                "maxlength": "100",
                "class": INPUT_CLASS,
            }),
            "google_maps_url": forms.URLInput(attrs={
                "placeholder": "https://maps.app.goo.gl/...",
                "maxlength": "500",
                "class": INPUT_CLASS,
            }),
            "description": forms.Textarea(attrs={
                "placeholder": "What pins are available here? Any useful details for fellow collectors.",
                "rows": 4,
                "maxlength": "1000",
                "class": TEXTAREA_CLASS,
            }),
            "photo_url": forms.URLInput(attrs={
                "placeholder": "Link to a photo of the pins (Google Photos, Imgur, etc.)",
                "class": INPUT_CLASS,
            }),
            "submitter_email": forms.EmailInput(attrs={
                "placeholder": "your@email.com",
                "class": INPUT_CLASS,
            }),
        }
        labels = {
            "country_name": "Country",
            "city_name": "City",
            "location_name": "Location name",
            "google_maps_url": "Google Maps link",
            "description": "Description",
            "photo_url": "Photo link",
            "has_city_pins": "City pins",
            "has_country_pins": "Country pins",
            "has_place_pins": "Place pins",
            "submitter_email": "Your email",
        }

    def clean(self):
        cleaned_data = super().clean()
        has_city = cleaned_data.get("has_city_pins")
        has_country = cleaned_data.get("has_country_pins")
        has_place = cleaned_data.get("has_place_pins")
        
        if not any([has_city, has_country, has_place]):
            raise forms.ValidationError("Please select at least one pin type.")
        
        return cleaned_data