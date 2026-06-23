from django.db import models
from django.utils.text import slugify


class Country(models.Model):
    name = models.CharField(max_length=30, help_text="Country name in English")
    code = models.CharField(max_length=2, unique=True, help_text="ISO country code, for flags")  # ISO код: RU, FR, JP, TH
    slug = models.SlugField(unique=True, blank=True, help_text="Generated automatically from the name")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Countries"

    @property
    def flag(self):
        return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in self.code.upper())


class City(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="cities")
    name = models.CharField(max_length=50, help_text="City name in English")
    slug = models.SlugField(unique=True, blank=True, help_text="Generated automatically from the name")


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}, {self.country.name}"
    
    class Meta:
        verbose_name_plural = "Cities"


class PinType(models.Model):
    CITY = "city"
    PLACE = "place"
    COUNTRY = "country"

    PIN_TYPE_CHOICES = [
        (CITY, "City pin"),
        (PLACE, "Place pin"),
        (COUNTRY, "Country pin"),
    ]

    name = models.CharField(max_length=50, choices=PIN_TYPE_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()


class Location(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="locations")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=300, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    google_maps_url = models.URLField(blank=True)
    pin_types = models.ManyToManyField(PinType, blank=True)
    verified = models.BooleanField(default=False)
    added_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="locations"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} — {self.city.name}"