from django import forms
from .models import Contact, Order, Customer
from django.contrib.auth.models import User
from django.core.mail import send_mail

class ContactForm(forms.ModelForm):

    class Meta:
        model = Contact
        fields = ['name', 'email', 'phonenumber', 'desc']
        

class CheckoutForm(forms.ModelForm):
    PAYMENT_METHOD_CHOICES = [
        ('Paystack', 'Paystack'),
        # Add other payment methods if any
    ]

    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('NGN', 'Naira'),
        ('CAD', 'Canadian Dollar'),
        ('AUD', 'Australian Dollar'),
    ]
    payment_method = forms.ChoiceField(choices=PAYMENT_METHOD_CHOICES)
    currency = forms.ChoiceField(choices=CURRENCY_CHOICES)
    
    class Meta:
        model = Order
        fields = ["ordered_by", "email", "shipping_address", "mobile", 'payment_method', 'currency']



class CustomerRegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.CharField(widget=forms.EmailInput())
    class Meta:
        model = Customer
        fields = ["username", "password", "email", "full_name", "address"]

    def clean_username(self):
        uname = self.cleaned_data.get("username")
        if User.objects.filter(username=uname).exists():
            raise forms.ValidationError("Customer with this username already exists.")
        
        return uname
        


class CustomerLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())


class PasswordForgotForm(forms.Form):
    email = forms.CharField(widget=forms.EmailInput(attrs={
        "class": "form-control",
        "placeholder": "Enter the email used in customer account..."
    }))