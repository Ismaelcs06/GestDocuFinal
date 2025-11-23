from django.urls import path
from .views import PanelView

app_name = "dashboard"

urlpatterns = [
    path("", PanelView.as_view(), name="panel"),
] 
