from django import views

from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from annoying.functions import get_object_or_None
from .forms import RegisterUserForm, LoginUserForm, OrderForm
from .models import Subscription

from django.conf import settings
from yookassa import Configuration, Payment


class BaseViews(views.View):
    def get(self, request, *args, **kwargs):
        title = 'План питания на неделю, меню, рецепты, список покупок. Классическое меню, безуглеводное меню'
        context = {'title': title}
        return render(request, 'base.html', context)


def order(request):
    title = 'Foodplan 2021 - Меню на неделю FOODPLAN'
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            print(form.cleaned_data['lunch'])
            return redirect('payment')
    else:
        form = OrderForm()
    return render(request, 'order.html', {'form': form, 'title': title})


class RegistrationView(CreateView):
    form_class = RegisterUserForm
    template_name = 'registration.html'
    success_url = reverse_lazy('base')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Foodplan 2021 - Меню на неделю FOODPLAN'
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('order')


class LoginUserView(LoginView):
    form_class = LoginUserForm
    template_name = 'login.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Foodplan 2021 - Меню на неделю FOODPLAN'
        return context

    def get_success_url(self):
        return reverse_lazy('account')


@csrf_exempt
def account(request):
    user = get_object_or_404(User, username=request.user)
    subscription = get_object_or_None(Subscription, user__username=str(user))
    title = 'Foodplan 2021 - Меню на неделю FOODPLAN'
    if request.method == "POST":
        form = RegisterUserForm(request.POST, instance=user)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('base')
    else:
        form = RegisterUserForm(instance=user)
    context = {'form': form, 'title': title, 'subscription': subscription}
    return render(request, 'account.html', context)


class PaymentView(views.View):
    def get(self, request, *args, **kwargs):
        Configuration.account_id = settings.YOOKASSA_ACCOUNT_ID
        Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

        payment = Payment.create({
            "amount": {
                "value": "100.00",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "http://127.0.0.1:8000/account/"
            },
            "capture": True,
            "description": "Заказ №1"
        })
        return redirect(payment.confirmation.confirmation_url)
