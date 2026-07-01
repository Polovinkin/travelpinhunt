"""
URL configuration for travelpinhunt project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('boss/', admin.site.urls),
    path("", include("locations.urls")),
]

# заголовок самой админки в header
admin.site.site_header = " TPH Django Admin Panel"
# название сайта во вкладке, что после |
admin.site.site_title = "TPH Django Admin"
# название главной страницы во вкладке
admin.site.index_title = "Main Admin"
