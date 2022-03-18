from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    BaseViews, LoginUserView,
    RegistrationView, order,
    account, PaymentView
)

urlpatterns = [
    path('', BaseViews.as_view(), name='base'),
    path('order/', order, name='order'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('account/', account, name='account'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('payment/', PaymentView.as_view(), name='payment')
]
