from django.urls import path
from . import views

urlpatterns = [

    # Authentication
    path('', views.home, name='home'),  # Root URL
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),

    # Product Management
    path('addproduct', views.add_product, name='add_product'),
    path('updateproduct/<int:product_id>', views.update_product, name='update_product'),
    path('deleteproduct/<int:product_id>', views.delete_product, name='delete_product'),
    path('products', views.get_all_products, name='get_all_products'),

    # Cart Management
    path('cart/add', views.add_to_cart, name='add_to_cart'),
    path('cart/update', views.update_cart, name='update_cart'),
    path('cart/delete', views.delete_from_cart, name='delete_from_cart'),
    path('cart', views.get_cart, name='get_cart'),

     # Order Management
    path('placeorder', views.place_order, name='place_order'),
    path('getallorders', views.get_all_orders, name='get_all_orders'),
    path('orders/customer/<int:customer_id>', views.get_orders_by_customer, name='get_orders_by_customer'),

]


