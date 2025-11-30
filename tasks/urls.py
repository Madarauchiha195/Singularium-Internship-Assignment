from django.urls import path
from .views import AnalyzeView, suggest_view

urlpatterns = [
    path('analyze/', AnalyzeView.as_view(), name='analyze'),
    path('suggest/', suggest_view, name='suggest'),
]
