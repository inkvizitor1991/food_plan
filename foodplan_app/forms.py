from django import forms

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


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


MOUNTHS_COUNT_CHOICES = (
    ('12', 'год'),
    ('3', 'три месяца'),
)

PERSONS_COUNT_CHOICES = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
)

ALLERGY_CHOICES = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
)
MENU_TYPE_CHOICES = (
    ('classic', 'классическое'),
    ('low_carb', 'низкоуглеводное'),
    ('vegetarian', 'вегетарианское'),
    ('keto', 'кето')
)

MENU_CHOICES = (
    ('breakfast', 'завтрак'),
    ('lunch', 'обед'),
    ('dinner', 'ужин'),
    ('dessert', 'десерт'),
    ('new_year', 'новогоднее меню 🎁')
)

class OrderForm(forms.Form):
    months_count = forms.ChoiceField(
        label="Срок",
        choices=MOUNTHS_COUNT_CHOICES,
        widget=forms.RadioSelect
    )
    menu_types = forms.ChoiceField(
        label="Тип меню",
        choices=MENU_TYPE_CHOICES,
        widget=forms.RadioSelect
    )
    menu = forms.ChoiceField(
        label="Меню",
        choices=MENU_CHOICES,
        widget=forms.RadioSelect
    )
    persons_count = forms.ChoiceField(
        label="Кол-во персон",
        choices=PERSONS_COUNT_CHOICES,
        widget=forms.RadioSelect
    )

    allergy = forms.MultipleChoiceField(
        label="Аллергии", choices=ALLERGY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
