from django import forms
from .models import Contact, Order, Customer, Product
from django.contrib.auth.forms import  UserChangeForm
from django.contrib.auth.models import User
from captcha.fields import CaptchaField


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
    captcha = CaptchaField()  # Add this field

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
    captcha = CaptchaField()  # Add this field



class ProductForm(forms.ModelForm):
    # more_images = forms.FileField(required=False, widget=forms.FileInput(attrs={
    #     "class": "form-control",
    #     "multiple": True
    # }))

    class Meta:
        model = Product
        fields = ["title", "slug", "category", "image", "marked_price", "selling_price", "description", "variant"]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter the product title here..."
            }),
            "slug": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter the unique slug here..."
            }),
            "category": forms.Select(attrs={
                "class": "form-control",
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
            "marked_price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Marked price of the product..."
            }),
            "selling_price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Selling price of the product..."
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",                
                "placeholder": "Description of the product...",
                "rows": 5
            }),
            "variant": forms.Select(attrs={
                "class": "form-control",
            }),
        }

class PasswordForgotForm(forms.Form):
    email = forms.CharField(widget=forms.EmailInput(attrs={
        "class": "form-control",
        "placeholder": "Enter the email used in customer account..."
    }))

    def clean_email(self):
        e = self.cleaned_data.get("email")
        if Customer.objects.filter(user__email=e).exists():
            pass
        else:
            raise forms.ValidationError(
                "Customer with this account does not exists..")
        return e
    

class PasswordResetForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'autocomplete': 'new-password',
        'placeholder': 'Enter New Password',
    }), label="New Password")
    confirm_new_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'autocomplete': 'new-password',
        'placeholder': 'Confirm New Password',
    }), label="Confirm New Password")

    def clean_confirm_new_password(self):
        new_password = self.cleaned_data.get("new_password")
        confirm_new_password = self.cleaned_data.get("confirm_new_password")
        if new_password != confirm_new_password:
            raise forms.ValidationError(
                "New Passwords did not match!")
        return confirm_new_password
    

class ProfileEditForm(forms.ModelForm):
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='', widget=forms.HiddenInput(), required=False
    )

    class Meta:
        model = Customer
        fields = ('full_name', 'address', 'password')

# class PasswordChangeForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['old_password'].widget.attrs.update({'placeholder': 'Old Password'})
#         self.fields['new_password1'].widget.attrs.update({'placeholder': 'New Password'})
#         self.fields['new_password2'].widget.attrs.update({'placeholder': 'Confirm New Password'})