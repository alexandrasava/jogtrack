from django.urls import path
from jogs.views import JogListCreateView, JogRUDView, JogReportListView


urlpatterns = [
    path('', JogListCreateView.as_view(), name="list_create"),
    path('<int:pk>/', JogRUDView.as_view(), name="jog_rud"),
    path('reports/', JogReportListView.as_view(), name='reports')
]
