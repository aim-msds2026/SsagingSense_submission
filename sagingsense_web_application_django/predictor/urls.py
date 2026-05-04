from django.urls import path
from . import views

app_name = "predictor"

urlpatterns = [
    path("", views.home, name="home"),
    path("scan/<str:module_key>/", views.scanner, name="scanner"),
    path("predict/<str:module_key>/", views.predict_module, name="predict_module"),
]
