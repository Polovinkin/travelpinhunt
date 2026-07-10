# Таблица маршрутов. Связывает URL адреса с функциями из views.py. Грубо говоря "какой адрес → какая функция".
from django.urls import path
from . import views

app_name = "locations"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("submit/", views.submit_location, name="submit_location"),
    path("submit/success/", views.submit_success, name="submit_success"),
    path("contributors/", views.contributors, name="contributors"),
    path("<slug:country_slug>/", views.country_detail, name="country_detail"),
    path("<slug:country_slug>/<slug:city_slug>/", views.city_detail, name="city_detail"),
]