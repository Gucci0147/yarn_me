from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register([Contact, Admin, Customer, Category, Product, Cart, CartProduct, Order, ProductImage])