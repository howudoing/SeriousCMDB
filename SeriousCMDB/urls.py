"""SeriousCMDB URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
# from django.conf.urls import url,include
from django.urls import path, include
from django.contrib import admin
from cmdb import views
from cmdb import rest_urls, urls as cmdb_urls
urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'', views.index),
    path(r'login/', views.acc_login, name='login'),
    path(r'logout/', views.acc_logout),
    path(r'cmdb/', include(cmdb_urls)),
    path(r'api/',  include(rest_urls)),
]
