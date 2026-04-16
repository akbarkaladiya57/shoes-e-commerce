"""
URL configuration for snakesole project.

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

from django.conf import settings
from django.conf.urls.static import static

from cart_app.urls import cart_urlpatterns
from user_app.urls import url_patterns
from product_app.urls import url_patterns as product_app
from order_app.urls import urlpatterns as order_app

urlpatterns = [
    path("admin/", admin.site.urls),
    path("",include(url_patterns)),
    path("",include(product_app)),
    path("",include(cart_urlpatterns)),
    path("",include(order_app)),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)