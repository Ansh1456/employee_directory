from django.urls import path
from .views import CustomLoginView, CustomLogoutView, change_password

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/change-password/', change_password, name='change_password'),
]
