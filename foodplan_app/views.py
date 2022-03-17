from django import views

from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .forms import RegisterUserForm, LoginUserForm


class BaseViews(views.View):
    def get(self, request, *args, **kwargs):
        title = 'План питания на неделю, меню, рецепты, список покупок. Классическое меню, безуглеводное меню'
        context = {'title': title}
        return render(request, 'base.html', context)


class OrderViews(views.View):
    def get(self, request, *args, **kwargs):
        title = 'Foodplan 2021 - Меню на неделю FOODPLAN'
        context = {'title': title}
        return render(request, 'order.html', context)


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
    title = 'Foodplan 2021 - Меню на неделю FOODPLAN'
    if request.method == "POST":
        form = RegisterUserForm(request.POST, instance=user)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('order')
    else:
        form = RegisterUserForm(instance=user)
    return render(request, 'account.html', {'form': form, 'title': title})
