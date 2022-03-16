from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    BaseViews, LoginUserView,
    RegistrationView
)







urlpatterns = [
    path('', BaseViews.as_view(), name='base'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('registration/', RegistrationView.as_view(), name='registration')
]