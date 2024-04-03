from django.shortcuts import render
from django.views.generic import TemplateView
from .models import *


# Create your views here.

class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['myname'] = "Ayankola Timileyin"
        context['product_list'] = Product.objects.all()
        return context
    
class ShopsView(TemplateView):
    template_name = "shops.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcategories'] = Category.objects.all()
        return context
    

class AboutView(TemplateView):
    template_name = "about.html"

class ContactView(TemplateView):
    template_name = "contact.html"