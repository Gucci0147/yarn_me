from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View, TemplateView, CreateView, FormView, DetailView, ListView
from django.core.paginator import Paginator
from .utils import password_reset_token
from django.core.mail import send_mail
from django.db.models import Q
from django.conf import settings
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json, requests
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy, reverse
from .forms import ContactForm, CheckoutForm, CustomerRegistrationForm, CustomerLoginForm, PasswordForgotForm, PasswordResetForm, ProductForm
from .models import *
# from payment.models import Payment



# Create your views here.


class EcomMixin():
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated:
                if hasattr(request.user, 'customer'):
                    cart_obj.customer = request.user.customer
                else:
                    # Create a new customer for the user
                    customer = Customer.objects.create(user=request.user)
                    cart_obj.customer = customer
                cart_obj.save()
        return super().dispatch(request, *args, **kwargs)

        



class IndexView(EcomMixin, TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['myname'] = "Ayankola Timileyin"
        all_products = Product.objects.all().order_by("-id")
        paginator = Paginator(all_products, 4)
        page_number = self.request.GET.get("page")
        print(page_number)
        product_list = paginator.get_page(page_number)
        context['product_list'] = product_list
        return context
    
class ShopsView(EcomMixin, TemplateView):
    template_name = "shops.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcategories'] = Category.objects.all()

        # Retrieve all products and their associated colors and sizes
        context['products'] = Product.objects.select_related('color', 'size').all()
        
        return context
    
class ProductDetailView(EcomMixin, TemplateView):
    template_name = "productdetail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url_slug = self.kwargs['slug']
        product = get_object_or_404(Product, slug=url_slug)
        product.view_count += 1
        product.save()
        context['product'] = product
        return context
    

class AddToCartView(EcomMixin, TemplateView):
    template_name = "addtocart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = self.kwargs.get('pro_id')
        product_obj = get_object_or_404(Product, id=product_id)

        color = self.request.GET.get('color', '').strip()
        size = self.request.GET.get('size', '').strip()

        cart_id = self.request.session.get("cart_id")
        if cart_id:
            cart_obj = get_object_or_404(Cart, id=cart_id)
            this_product_in_cart = cart_obj.cartproducts.filter(product=product_obj, color=color, size=size)
            
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last()
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.selling_price
                cartproduct.save()
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
            else:
                cartproduct = CartProduct.objects.create(
                    cart=cart_obj,
                    product=product_obj,
                    rate=product_obj.selling_price,
                    quantity=1,
                    subtotal=product_obj.selling_price,
                    color=color,
                    size=size
                )
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
        else:
            cart_obj = Cart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            CartProduct.objects.create(
                cart=cart_obj,
                product=product_obj,
                rate=product_obj.selling_price,
                quantity=1,
                subtotal=product_obj.selling_price,
                color=color,
                size=size
            )
            cart_obj.total += product_obj.selling_price
            cart_obj.save()
        
        context['cart'] = cart_obj
        context['product'] = product_obj        
        context['color'] = color
        context['size'] = size

        return context







class ManageCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        # print("This is manage cart section")
        cp_id = self.kwargs["cp_id"]
        action = request.GET.get("action")
        cp_obj = get_object_or_404(CartProduct, id=cp_id)
        cart_obj = cp_obj.cart
        
        if action == "inc":
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()

        elif action == "dcr":
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()

        elif action == "rmv":
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
        else:
            pass
        return redirect("ecommerceapp:mycart")
    
class EmptyCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            cart = get_object_or_404(Cart, id=cart_id)
            cart.cartproducts.all().delete()
            cart.total = 0
            cart.save()
        return redirect("ecommerceapp:mycart")



class MyCartView(EcomMixin, TemplateView):
    template_name = "mycart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            # Retrieve the cart and include its cart products
            cart = get_object_or_404(Cart, id=cart_id)
            # Include cart products with their color and size information
            cart_products = cart.cartproducts.all()
        else:
            cart = None
            cart_products = []

        # Add cart and cart products to the context
        context["cart"] = cart
        context["cart_products"] = cart_products
        return context



    
class CheckoutView(EcomMixin, CreateView):
    template_name = "checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("ecommerceapp:index")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            cart_id = self.request.session.get("cart_id", None)
            if not cart_id or not Cart.objects.filter(id=cart_id).exists():
                return redirect("cart")  # Ensure the user has a cart
        else:
            return redirect("/login/?next=/checkout/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            context['cart'] = cart_obj
        else:
            context['cart'] = None
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            
            existing_order = Order.objects.filter(cart=cart_obj).first()
            if existing_order:
                form.instance = existing_order
            else:
                form.instance.cart = cart_obj
                form.instance.subtotal = cart_obj.total
                form.instance.discount = 0
                form.instance.total = cart_obj.total
                form.instance.order_status = "Order Received"
            
                form.instance.currency = form.cleaned_data.get("currency")

            del self.request.session["cart_id"]
            order = form.save()

            pm = form.cleaned_data.get("payment_method")
            if pm == "Paystack":
                import uuid
                reference = str(order.id) + str(uuid.uuid4())
                order.paystack_reference = reference
                order.save()
                return redirect(reverse("ecommerceapp:paystackrequest", kwargs={'order_id': order.id}))

        else:
            return redirect("ecommerceapp:index")
        return super().form_valid(form)


class PaystackRequestView(View):
    def get(self, request, order_id, *args, **kwargs):
        try:
            order = Order.objects.get(id=order_id)
            context = {
                'cart': order.cart,
                'email': order.cart.customer.user.email,
                'amount': order.total,
                'currency': order.currency,
                'first_name': order.cart.customer.user.first_name,
                'last_name': order.cart.customer.user.last_name,
                'reference': order.paystack_reference,
            }
        except Order.DoesNotExist:
            return HttpResponse("Order not found", status=404)

        return render(request, "paystackrequest.html", context)

def verify_paystack_transaction(reference):
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    return response.json()
    
@method_decorator(csrf_exempt, name='dispatch')
class PaystackWebhookView(View):
    def post(self, request, *args, **kwargs):
        payload = json.loads(request.body)
        event = payload.get('event')

        if event == 'charge.success':
            reference = payload['data']['reference']
            verification_result = verify_paystack_transaction(reference)
            
            if verification_result['status'] and verification_result['data']['status'] == 'success':
                try:
                    order = Order.objects.get(paystack_reference=reference)
                    order.order_status = 'Payment Completed'
                    order.payment_completed = True
                    order.save()
                except Order.DoesNotExist:
                    pass
        
        return JsonResponse({'status': 'success'}, status=200)
           

class PaystackVerifyView(View):
    def post(self, request, *args, **kwargs):
        payload = json.loads(request.body)
        reference = payload.get('reference')
        
        verification_result = verify_paystack_transaction(reference)
        
        if verification_result['status'] and verification_result['data']['status'] == 'success':
            try:
                order = Order.objects.get(paystack_reference=reference)
                order.order_status = 'Payment Completed'
                order.payment_completed = True
                order.save()
                return JsonResponse({'status': 'success'}, status=200)
            except Order.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=404)
        return JsonResponse({'status': 'error', 'message': 'Verification failed'}, status=400)



class CustomerRegistrationView(CreateView):
    template_name = "customerregistration.html"
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy("ecommerceapp:index")
 
    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")
        full_name = form.cleaned_data.get("full_name")
        user = User.objects.create_user(username, email, password)
        Customer.objects.create(user=user, full_name=full_name)
        form.instance.user = user
        login(self.request, user)
        return redirect(self.success_url)        
    
    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url
    
class CustomerLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("ecommerceapp:index")
    

class CustomerLoginView(FormView):
    template_name = "customerlogin.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("ecommerceapp:index")

    # form_valid method id a type of post method and is available in createview formview and updateview 
    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data.get("password")
        usr = authenticate(username=uname, password=pword)
        if usr is not None and Customer.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})
        
        return super().form_valid(form)
    
    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url



class AboutView(EcomMixin, TemplateView):
    template_name = "about.html"

class ContactView(EcomMixin, FormView):
    template_name = 'contact.html'
    form_class = ContactForm
    success_url = '/contact/'

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Your message has been sent successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error in your form. Please try again.')
        return super().form_invalid(form)


class CustomerProfileView(TemplateView):
    template_name = "customerprofile.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context["customer"] = customer
        orders = Order.objects.filter(cart__customer=customer).order_by("-id")
        context["orders"] = orders
        return context
    
class CustomerOrderDetailView(DetailView):
    template_name = "customerorderdetail.html"
    model = Order
    context_object_name = "ord_obj"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            order_id = self.kwargs["pk"]
            order = Order.objects.get(id=order_id)
            if request.user.customer != order.cart.customer:
                return redirect("ecommerceapp:customerprofile")
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)
    
class SearchView(TemplateView):
    template_name = "search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kw = self.request.GET.get("keyword")
        results = Product.objects.filter(
            Q(title__icontains=kw) | Q(description__icontains=kw))
        print(results)
        context["results"] = results
        return context
    


class PasswordForgotView(FormView):
    template_name = "forgotpassword.html"
    form_class = PasswordForgotForm
    success_url = '/forgot-password/?m=s'

    def form_valid(self, form):
        # get email from user
        email = form.cleaned_data.get("email")
        # get current host ip/dpmain
        url = self.request.META['HTTP_HOST']
        # get customer and then user
        customer = Customer.objects.get(user__email=email)
        user = customer.user
        # send mail to the user with email
        text_content = 'Please Click the link below to reset your password. '
        html_content = url + "/password-reset/" + email + \
        "/" + password_reset_token.make_token(user) + "/"
        send_mail(
            'Password Reset Link | Yarn_me',
            text_content + html_content,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        return super().form_valid(form)

class PasswordResetView(FormView):
    template_name = "passwordreset.html"
    form_class = PasswordResetForm
    success_url = "/login/"

    def dispatch(self, request, *args, **kwargs):
        email = self.kwargs.get("email")
        user = User.objects.get(email=email)
        token = self.kwargs.get("token")
        if user is not None and password_reset_token.check_token(user, token):
            pass
        else:
            return redirect(reverse("ecommerceapp:passwordforgot") + "?m=e")

        return super().dispatch(request, *args, **kwargs)
    

    def form_valid(self, form):
        password = form.cleaned_data['new_password']
        email = self.kwargs.get("email")
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        return super().form_valid(form)
    

    # admin pages

class AdminLoginView(FormView):
    template_name = "adminpages/adminlogin.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("ecommerceapp:adminhome")

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=pword)
        if usr is not None and Admin.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})
        return super().form_valid(form)
    


class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Admin.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/admin-login/")
        return super().dispatch(request, *args, **kwargs)


class AdminHomeView(AdminRequiredMixin, TemplateView):
    template_name = "adminpages/adminhome.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pendingorders"] = Order.objects.filter(
            order_status="Order Received").order_by("-id")
        return context
    

class AdminOrderDetailView(AdminRequiredMixin, DetailView):
    template_name = "adminpages/adminorderdetail.html"
    model = Order
    context_object_name = "ord_obj"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["allstatus"] = ORDER_STATUS
        return context
    


class AdminOrderListView(AdminRequiredMixin, ListView):
    template_name = "adminpages/adminorderlist.html"
    queryset = Order.objects.all().order_by("-id")
    context_object_name = "allorders"


class AdminOrderStatusChangeView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        order_id = self.kwargs["pk"]
        order_obj = Order.objects.get(id=order_id)
        new_status = request.POST.get("status")
        order_obj.order_status = new_status
        order_obj.save()

        return redirect(reverse_lazy("ecommerceapp:adminorderdetail", kwargs={"pk": order_id}))

class AdminProductListView(AdminRequiredMixin, ListView):
    template_name = "adminpages/adminproductlist.html"
    queryset = Product.objects.all().order_by("-id")
    context_object_name = "allproducts"

class AdminProductCreateView(AdminRequiredMixin, CreateView):
    template_name = "adminpages/adminproductcreate.html"
    form_class = ProductForm
    success_url = reverse_lazy("ecommerceapp:adminproductlist")

    def form_valid(self, form):
        p = form.save()
        images = self.request.FILES.getlist("more_images")
        for i in images:
            ProductImage.objects.create(product=p, images=i)
        return super().form_valid(form)
    
        
    