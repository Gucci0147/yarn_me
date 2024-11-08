from django.urls import path
from .views import *
from . import views


app_name = "ecommerceapp"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("about/", AboutView.as_view(), name="about"),
    path("contact/", ContactView.as_view(), name="contact"),
    path("shops/", ShopsView.as_view(), name="shops"),
    path("product/<slug:slug>", ProductDetailView.as_view(), name="productdetail"),

    path("addtocart/<int:pro_id>/", AddToCartView.as_view(), name="addtocart"),
    path("my-cart/", MyCartView.as_view(), name="mycart"),
    path("manage-cart/<int:cp_id>/", ManageCartView.as_view(), name="managecart"),
    path("empty-cart/", EmptyCartView.as_view(), name="emptycart"),

    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("paystack-request/<int:order_id>/", PaystackRequestView.as_view(), name="paystackrequest"),
    path("paystack-webhook/", PaystackWebhookView.as_view(), name="paystack-webhook"),
    path("paystack-verify/", PaystackVerifyView.as_view(), name="paystack-verify"),

    path("register/", CustomerRegistrationView.as_view(), name="customerregistration"),
    
    path("logout/", CustomerLogoutView.as_view(), name="customerlogout"),
    path("login/", CustomerLoginView.as_view(), name="customerlogin"),


    path("profile/", CustomerProfileView.as_view(), name="customerprofile"),
    path("profile/order-<int:pk>/", CustomerOrderDetailView.as_view(), name="customerorderdetail"),
    
    path("profile/edit/", CustomerProfileEditView.as_view(), name="customerprofile_edit"),

    path('change_password/', views.change_password, name='change_password'),


    path("search/", SearchView.as_view(), name="search"),

    path("forgot-password/", PasswordForgotView.as_view(), name="passwordforgot"),
    path("password-reset/<email>/<token>/", PasswordResetView.as_view(), name="passwordreset"),

    # Admin Side pages

    path("admin-login/", AdminLoginView.as_view(), name="adminlogin"),
    path("admin-home/", AdminHomeView.as_view(), name="adminhome"),
    path("admin-order/<int:pk>/", AdminOrderDetailView.as_view(), name="adminorderdetail"),
    path("admin-all-orders/", AdminOrderListView.as_view(), name="adminorderlist"),

    path("admin-order/<int:pk>-change/", AdminOrderStatusChangeView.as_view(), name="adminorderstatuschange"),

    path("admin-product/list/", AdminProductListView.as_view(), name="adminproductlist"),
    path("admin-product/add/", AdminProductCreateView.as_view(), name="adminproductcreate"),
]