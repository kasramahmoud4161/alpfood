from django.urls import path
from .views import (
    GenerateWeeklyPlanView, 
    CurrentPlanView, 
    TodayMealsView, 
    MyPlansView
)

urlpatterns = [
    path('generate/', GenerateWeeklyPlanView.as_view(), name='generate-plan'),
    path('current/', CurrentPlanView.as_view(), name='current-plan'),
    path('today/', TodayMealsView.as_view(), name='today-meals'),
    path('my-plans/', MyPlansView.as_view(), name='my-plans'),
]