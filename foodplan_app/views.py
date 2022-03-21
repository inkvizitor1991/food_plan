import threading
import time
import uuid

from django import views

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .forms import RegisterUserForm, LoginUserForm, get_order_form
from .models import Subscription, Allergen

from django.conf import settings
from yookassa import Configuration, Payment

temped_subscriptions = {}


class BaseViews(views.View):
    def get(self, request, *args, **kwargs):
        title = 'План питания на неделю, меню, рецепты, список покупок. Классическое меню, безуглеводное меню'
        context = {'title': title}
        return render(request, 'base.html', context)


@login_required(login_url='/login/')
def order(request):
    title = 'Foodplan 2021 - Меню на неделю FOODPLAN'
    if request.method == 'POST':
        form = get_order_form()(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            request.session['subscription_data'] = form.cleaned_data
            return redirect('payment')
    else:
        form = get_order_form()
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
    subscriptions = (Subscription.objects.get_active_subscriptions()
                     .filter(user__username=str(user)))
    title = 'Foodplan 2021 - Меню на неделю FOODPLAN'
    if request.method == "POST":
        form = RegisterUserForm(request.POST, instance=user)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('base')
    else:
        form = RegisterUserForm(instance=user)
    context = {'form': form, 'title': title, 'subscriptions': subscriptions}
    return render(request, 'account.html', context)


def check_payment_until_confirm(payment_id, subscription_uuid):
    while True:
        payment = Payment.find_one(payment_id)
        if payment.status == "canceled":
            temped_subscriptions.pop(subscription_uuid)
            return
        if payment.status == "succeeded":
            subscription = temped_subscriptions[subscription_uuid]
            subscription.last_payed_at = timezone.now().date()
            subscription.save()
            return

        time.sleep(5)


def calculate_cost(subscription):
    # перенести в бд
    meal_cost = {
        'breakfast': 500, 'lunch': 400,
        'dinner': 450, 'dessert': 550, 'new_year': 1000
    }
    meal_cost_sum = 0
    for meal in subscription['meals']:
        meal_cost_sum += meal_cost[meal]
    cost = (int(subscription['months_count'])
            * meal_cost_sum
            * int(subscription['persons_count']))
    return str(cost)


class PaymentView(LoginRequiredMixin, views.View):
    raise_exception = True

    def get(self, request, *args, **kwargs):
        Configuration.account_id = settings.YOOKASSA_ACCOUNT_ID
        Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

        subscription = request.session.get('subscription_data')

        subscription_uuid = uuid.uuid4()

        payment = Payment.create({
            "amount": {
                "value": calculate_cost(subscription),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": request.build_absolute_uri(reverse('account'))
            },
            "capture": True,
            "description": None
        })

        prepared_subscription = Subscription()

        prepared_subscription.user = request.user
        prepared_subscription.menu_type = subscription['menu_type']
        prepared_subscription.meals = subscription['meals']
        prepared_subscription.months_count = int(subscription['months_count'])
        prepared_subscription.persons_count = int(
            subscription['persons_count']
        )

        allergens_ids = [
            int(allergen_id) for allergen_id in subscription['allergens']
        ]

        allergens = Allergen.objects.filter(pk__in=allergens_ids)

        for allergen in allergens:
            prepared_subscription.excluded_allergens.add(allergen)

        temped_subscriptions[subscription_uuid] = prepared_subscription

        threading.Thread(
            target=check_payment_until_confirm,
            args=[payment.id, subscription_uuid],
            daemon=True
        ).start()

        return redirect(payment.confirmation.confirmation_url)
