from django.urls import path
from . import views

urlpatterns = [
    path('',views.visual_home,name="raster_visual"),
]
