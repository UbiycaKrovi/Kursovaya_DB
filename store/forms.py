from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import User, Supplier, Product

User = get_user_model()

class UserRegistrationForm(forms.Form):
    USER_TYPE_CHOICES = [
        ('customer', 'Покупатель'), 
        ('supplier', 'Поставщик')
    ]
    
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES, 
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label=''
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Адрес эл. почты'})
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg'})
    )
    password2 = forms.CharField(
        label='Подтвердите пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg'})
    )
    
    username = forms.CharField(
        max_length=150,
        required=False,
        label='Имя/Никнейм',
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Ваше имя'})
    )
    phone_customer = forms.CharField(
        max_length=20,
        required=False,
        label='Телефон',
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Номер телефона'})
    )
    address = forms.CharField(
        max_length=255,
        required=False,
        label='Адрес доставки',
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Адрес доставки'})
    )
    
    company_name = forms.CharField(
        max_length=100,
        required=False,
        label='Название компании',
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Наименование'})
    )
    inn = forms.CharField(
        max_length=12,
        required=False,
        label='ИНН',
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'ИНН'})
    )
    phone_supplier = forms.CharField(
        max_length=20,
        required=False,
        label='Телефон компании',
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Номер телефона'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_type'].widget.attrs.update({'onchange': 'toggleFields(this.value)'})

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        
        if user_type == 'customer':
            if not cleaned_data.get('username'):
                self.add_error('username', 'Имя обязательно для покупателя')
            if not cleaned_data.get('phone_customer'):
                self.add_error('phone_customer', 'Телефон обязателен')
            if not cleaned_data.get('address'):
                self.add_error('address', 'Адрес обязателен')
                
        elif user_type == 'supplier':
            if not cleaned_data.get('company_name'):
                self.add_error('company_name', 'Название компании обязательно')
            if not cleaned_data.get('inn'):
                self.add_error('inn', 'ИНН обязателен')
            if not cleaned_data.get('phone_supplier'):
                self.add_error('phone_supplier', 'Телефон обязателен')
        
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            self.add_error('password2', 'Пароли не совпадают')
            
        return cleaned_data

    def save(self):
        cleaned_data = self.cleaned_data
        user_type = cleaned_data['user_type']
        
        phone = cleaned_data['phone_customer'] if user_type == 'customer' else cleaned_data['phone_supplier']
        user = User.objects.create_user(
            email=cleaned_data['email'],
            username=cleaned_data['username'] if user_type == 'customer' else cleaned_data['company_name'],
            role=user_type,
            phone=phone,
            address=cleaned_data.get('address', '')
        )
        user.set_password(cleaned_data['password1'])
        user.save()
        
        if user_type == 'supplier':
            Supplier.objects.create(
                company_name=cleaned_data['company_name'],
                inn=cleaned_data['inn'],
                phone=cleaned_data['phone_supplier'],
                email=cleaned_data['email']
            )
            
        return user

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'warehouse', 'quantity']
        
    widgets = {
        'name': forms.TextInput(attrs={'placeholder': 'Введите название товара'}),
        'description': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Опишите товар подробнее...'}),
        'price': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
        'quantity': forms.NumberInput(attrs={'min': 1, 'placeholder': '10'}),
    }
    
    labels = {
        'name': '',
        'description': '',
        'category': '',
        'price': '',
        'warehouse': '',
        'quantity': '',
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control form-control-lg',
            })
