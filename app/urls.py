from django.urls import path
from .views import EnterPoint


urlpatterns = [
    path('api/V1/deals', EnterPoint.as_view()),
]
