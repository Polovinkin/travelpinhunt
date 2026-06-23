# Таблица маршрутов. Связывает URL адреса с функциями из views.py. Грубо говоря "какой адрес → какая функция".
from django.urls import path
from . import views

app_name = "locations"

urlpatterns = [
    path("", views.home, name="home"),
    path("<slug:country_slug>/", views.country_detail, name="country_detail"),
    path("<slug:country_slug>/<slug:city_slug>/", views.city_detail, name="city_detail"),
]