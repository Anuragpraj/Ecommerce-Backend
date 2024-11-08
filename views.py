from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from .models import Product, Cart, CartItem, Order, OrderItem
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json

def home(request):
    return HttpResponse("Welcome to the E-commerce platform backend!")

# Authentication
# 1. Sign Up
@csrf_exempt
def signup(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email is already registered'}, status=400)

         # Create the new user
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password) # Hash the password
        )

        return JsonResponse({'message': 'User registered successfully', 'user_id': user.id})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

from django.contrib.auth import authenticate, login

# 2. Sign In
@csrf_exempt
def signin(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        # Check if user with this email exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)

        # Check if the provided password matches the stored hashed password
        if check_password(password, user.password):
            login(request, user)  # Log the user in
            return JsonResponse({'message': 'Login successful'})
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

# Product Management
# 1. Add Product
@csrf_exempt
def add_product(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        description = data.get('description')
        price = data.get('price')
        category = data.get('category')

        # Validate input data
        if not all([name, description, price, category]):
            return JsonResponse({'error': 'All fields are required'}, status=400)

        try:
            price = float(price)
            if price <= 0:
                return JsonResponse({'error': 'Price must be a positive number'}, status=400)
        except ValueError:
            return JsonResponse({'error': 'Invalid price format'}, status=400)

        product = Product.objects.create(
            name=name,
            description=description,
            price=price,
            category=category
        )

        return JsonResponse({'message': 'Product added successfully', 'product_id': product.id})
    return JsonResponse({'error': 'Invalid request method'}, status=405)

# 2. Update Product
@csrf_exempt
def update_product(request, product_id):
    if request.method == 'PUT':
        data = json.loads(request.body)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)

        name = data.get('name', product.name)
        description = data.get('description', product.description)
        price = data.get('price', product.price)
        category = data.get('category', product.category)

        if price is not None:
            try:
                price = float(price)
                if price <= 0:
                    return JsonResponse({'error': 'Price must be a positive number'}, status=400)
            except ValueError:
                return JsonResponse({'error': 'Invalid price format'}, status=400)

        product.name = name
        product.description = description
        product.price = price
        product.category = category
        product.save()

        return JsonResponse({'message': 'Product updated successfully'})
    return JsonResponse({'error': 'Invalid request method'}, status=405)

# 3. Delete Product
@csrf_exempt
def delete_product(request, product_id):
    if request.method == 'DELETE':
        try:
            product = Product.objects.get(id=product_id)
            product.delete()
            return JsonResponse({'message': 'Product deleted successfully'})
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

# 4. Get All Products
@csrf_exempt
def get_all_products(request):
    if request.method == 'GET':
        products = Product.objects.all()
        product_list = [
            {
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': float(product.price),
                'category': product.category
            } for product in products
        ]

        if not product_list:
            return JsonResponse({'message': 'No products found'}, status=404)

        return JsonResponse({'products': product_list})
    return JsonResponse({'error': 'Invalid request method'}, status=405)

# Cart Management
# 1. Add Product to Cart
@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)

        # Validate quantity
        if quantity <= 0:
            return JsonResponse({'error': 'Quantity must be greater than 0'}, status=400)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)

        # Get or create the cart for the customer
        user = request.user
        cart, created = Cart.objects.get_or_create(customer=user)

        # Check if product is already in the cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            # If product exists, update quantity
            cart_item.quantity += quantity
            cart_item.save()

        return JsonResponse({'message': 'Product added to cart', 'cart_item_id': cart_item.id, 'quantity': cart_item.quantity})

    return JsonResponse({'error': 'Invalid request method'}, status=405)

# 2. Update Cart Item Quantity
@csrf_exempt
def update_cart(request):
    if request.method == 'PUT':
        data = json.loads(request.body)
        cart_item_id = data.get('cart_item_id')
        quantity = data.get('quantity')

        if quantity is None or quantity <= 0:
            return JsonResponse({'error': 'Quantity must be greater than 0'}, status=400)

        try:
            cart_item = CartItem.objects.get(id=cart_item_id)
        except CartItem.DoesNotExist:
            return JsonResponse({'error': 'Cart item not found'}, status=404)

        cart_item.quantity = quantity
        cart_item.save()

        return JsonResponse({'message': 'Cart item updated successfully', 'cart_item_id': cart_item.id, 'quantity': cart_item.quantity})

    return JsonResponse({'error': 'Invalid request method'}, status=405)

# 3. Delete Product from Cart
@csrf_exempt
def delete_from_cart(request):
    if request.method == 'DELETE':
        data = json.loads(request.body)
        cart_item_id = data.get('cart_item_id')

        try:
            cart_item = CartItem.objects.get(id=cart_item_id)
            cart_item.delete()
            return JsonResponse({'message': 'Product removed from cart'})
        except CartItem.DoesNotExist:
            return JsonResponse({'error': 'Cart item not found'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

# 4. Get Cart
@csrf_exempt
def get_cart(request):
    if request.method == 'GET':
        user = request.user
        try:
            cart = Cart.objects.get(customer=user)
        except Cart.DoesNotExist:
            return JsonResponse({'message': 'Cart is empty'}, status=404)

        cart_items = cart.items.all()
        cart_details = [
            {
                'product_id': item.product.id,
                'name': item.product.name,
                'description': item.product.description,
                'quantity': item.quantity,
                'price': float(item.product.price),
                'total_price': float(item.product.price) * item.quantity
            }
            for item in cart_items
        ]

        total_amount = sum(item['total_price'] for item in cart_details)

        return JsonResponse({'cart': cart_details, 'total_amount': total_amount})

    return JsonResponse({'error': 'Invalid request method'}, status=405)

# Order Management
# 1 Place Order
@csrf_exempt
def place_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        shipping_address = data.get('shipping_address')

        if not shipping_address:
            return JsonResponse({'error': 'Shipping address is required'}, status=400)

        user = request.user
        try:
            cart = Cart.objects.get(customer=user)
        except Cart.DoesNotExist:
            return JsonResponse({'error': 'Cart is empty'}, status=404)

        cart_items = cart.items.all()
        if not cart_items:
            return JsonResponse({'error': 'Cart is empty, cannot place order'}, status=400)

        # Create the order
        order = Order.objects.create(
            customer=user,
            shipping_address=shipping_address,
            status='Processing'
        )

        total_amount = 0
        for item in cart_items:
            # Create order items for each product in the cart
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            total_amount += item.product.price * item.quantity

        # Clear the cart after the order is placed
        cart.items.all().delete()

        return JsonResponse({'message': 'Order placed successfully', 'order_id': order.id, 'total_amount': total_amount})

    return JsonResponse({'error': 'Invalid request method'}, status=405)

# 2. Get All Orders (Admin View)
@csrf_exempt
def get_all_orders(request):
    if request.method == 'GET':
        orders = Order.objects.all()
        order_list = [
            {
                'order_id': order.id,
                'customer': order.customer.username,
                'shipping_address': order.shipping_address,
                'status': order.status,
                'order_date': order.order_date,
                'items': [
                    {
                        'product_name': item.product.name,
                        'quantity': item.quantity,
                        'price': float(item.price),
                        'total_price': float(item.price) * item.quantity
                    }
                    for item in order.items.all()
                ]
            } for order in orders
        ]
        return JsonResponse({'orders': order_list})
    return JsonResponse({'error': 'Invalid request method'}, status=405)

# 3. Get Orders by Customer ID
@csrf_exempt
def get_orders_by_customer(request, customer_id):
    if request.method == 'GET':
        try:
            customer = User.objects.get(id=customer_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Customer not found'}, status=404)

        orders = Order.objects.filter(customer=customer)
        if not orders.exists():
            return JsonResponse({'error': 'No orders found for this customer'}, status=404)
        
        order_list = [
            {
                'order_id': order.id,
                'shipping_address': order.shipping_address,
                'status': order.status,
                'order_date': order.order_date,
                'items': [
                    {
                        'product_name': item.product.name,
                        'quantity': item.quantity,
                        'price': float(item.price),
                        'total_price': float(item.price) * item.quantity
                    }
                    for item in order.items.all()
                ]
            } for order in orders
        ]
        return JsonResponse({'orders': order_list})

    return JsonResponse({'error': 'Invalid request method'}, status=405)
