from django import forms

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from foodplan_app.models import MenuType, Allergen, Meal, Subscription


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput)
    email = forms.EmailField(label='Email', widget=forms.EmailInput)
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Повтор пароля',
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)


MONTHS_COUNT_CHOICES = Subscription.MonthCount.choices

PERSONS_COUNT_CHOICES = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
)

MENU_TYPE_CHOICES = MenuType.choices

MEAL_CHOICES = Meal.choices


def get_order_form():
    allergen_choices = [
        (allergen.id, allergen.name) for allergen in Allergen.objects.all()
    ]

    class OrderForm(forms.Form):
        months_count = forms.ChoiceField(
            label="Срок",
            choices=MONTHS_COUNT_CHOICES,
            widget=forms.RadioSelect
        )
        menu_type = forms.ChoiceField(
            label="Тип меню",
            choices=MENU_TYPE_CHOICES,
            widget=forms.RadioSelect
        )
        meals = forms.MultipleChoiceField(
            label="Меню",
            choices=MEAL_CHOICES,
            widget=forms.CheckboxSelectMultiple,
        )
        persons_count = forms.ChoiceField(
            label="Кол-во персон",
            choices=PERSONS_COUNT_CHOICES,
            widget=forms.RadioSelect
        )

        allergens = forms.MultipleChoiceField(
            label="Аллергии", choices=allergen_choices,
            widget=forms.CheckboxSelectMultiple,
            required=False
        )
        promo_code = forms.CharField(label='Промкод', required=False)

        def clean_promo_code(self):
            promo_code = self.cleaned_data['promo_code']
            # промокод желательно из бд достать
            if promo_code and promo_code != '2022':
                raise forms.ValidationError('Промкод не верный')
            return promo_code

    return OrderForm
