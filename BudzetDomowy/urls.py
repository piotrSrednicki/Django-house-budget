from django.contrib import admin
from django.urls import path,include
from django.views.generic.base import TemplateView
urlpatterns = [
    path('budzetapp/', include('budzetapp.urls')),
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path('', TemplateView.as_view(template_name='budzetapp/userInterface.html'), name='userInterface')

]
