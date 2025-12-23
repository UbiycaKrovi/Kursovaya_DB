from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import Product, Category, Supplier, Cart, CartItem, Order, Payment, Delivery, Review
from .forms import UserRegistrationForm, ProductForm, ReviewForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
import csv
import json
from django.http import JsonResponse, HttpResponse

def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    category_id = request.GET.get('category')
    supplier_id = request.GET.get('supplier')

    selected_category_name = None
    selected_supplier = None

    if category_id:
        products = products.filter(category_id=category_id)
        try:
            selected_category_name = Category.objects.get(id=category_id).name
        except Category.DoesNotExist:
            selected_category_name = None

    if supplier_id:
        products = products.filter(supplier_id=supplier_id)
        try:
            selected_supplier = Supplier.objects.get(id=supplier_id)
        except Supplier.DoesNotExist:
            selected_supplier = None

    return render(request, 'store/product_list.html', {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'selected_category_name': selected_category_name,
        'selected_supplier': selected_supplier,
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = Review.objects.filter(product=product).select_related('user').order_by('-created_at')
    avg_rating = product.get_average_rating()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Отзыв добавлен!')
            return redirect('product_detail', pk=product.pk)
    else:
        form = ReviewForm()

    return render(request, 'store/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'form': form,
    })

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'{user.username}, добро пожаловать!')
            return redirect('login')
    else:
        form = UserRegistrationForm()  
    return render(request, 'store/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('product_list')
    else:
        form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('product_list')

class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'store/product_create.html'
    success_url = '/'

    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_supplier

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    total_price = cart.get_total_price()
    return render(request, 'store/cart.html', {
        'cart': cart, 'total_price': total_price
    })

@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f'{product.name} добавлен в корзину!')
    return redirect('cart')

@login_required
def remove_from_cart(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Товар удален из корзины!')
    return redirect('cart')

@login_required
def update_cart_item(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

@login_required
def export_products_json(request):
    products = Product.objects.all()
    category_id = request.GET.get('category')
    if category_id not in (None, '', 'None'):
        products = products.filter(category_id=category_id)

    data = []
    for p in products:
        data.append({
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'category': p.category.name if p.category else None,
            'price': float(p.price),
            'quantity': p.quantity,
            'supplier': p.supplier.company_name if p.supplier else None,
        })

    response = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = 'attachment; filename="products.json"'
    return response

@login_required
def export_products_csv(request):
    products = Product.objects.all()
    category_id = request.GET.get('category')

    if category_id not in (None, '', 'None'):
        products = products.filter(category_id=category_id)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'

    response.write('\ufeff'.encode('utf-8'))

    writer = csv.writer(response)
    writer.writerow(['ID', 'Название', 'Категория', 'Цена', 'Количество', 'Поставщик'])

    for p in products:
        writer.writerow([
            p.id,
            p.name,
            p.category.name if p.category else '',
            p.price,
            p.quantity,
            p.supplier.company_name if p.supplier else '',
        ])

    return response

@login_required
def export_orders_json(request):
    """Экспорт заказов в JSON (можно фильтровать по пользователю)."""
    orders = Order.objects.select_related('user').all()
    user_id = request.GET.get('user')
    if user_id:
        orders = orders.filter(user_id=user_id)

    data = []
    for o in orders:
        data.append({
            'id': o.id,
            'user_email': o.user.email,
            'status': o.status,
            'total_price': float(o.total_price),
            'created_at': o.created_at.isoformat(),
        })

    response = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = 'attachment; filename="orders.json"'
    return response


@login_required
def export_orders_csv(request):
    orders = Order.objects.select_related('user').all()
    user_id = request.GET.get('user')
    if user_id:
        orders = orders.filter(user_id=user_id)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'

    response.write('\ufeff'.encode('utf-8')) 

    writer = csv.writer(response)
    writer.writerow(['ID', 'Email пользователя', 'Статус', 'Сумма', 'Дата создания'])

    for o in orders:
        writer.writerow([
            o.id,
            o.user.email,
            o.status,
            o.total_price,
            o.created_at.strftime('%Y-%m-%d %H:%M'),
        ])
    return response


@login_required
def export_suppliers_json(request):
    """Экспорт поставщиков в JSON."""
    suppliers = Supplier.objects.all()

    data = []
    for s in suppliers:
        data.append({
            'id': s.id,
            'company_name': s.company_name,
            'inn': s.inn,
            'phone': s.phone,
            'email': s.email,
            'address': s.address,
        })

    response = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = 'attachment; filename="suppliers.json"'
    return response


@login_required
def export_suppliers_csv(request):
    suppliers = Supplier.objects.all()

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="suppliers.csv"'

    response.write('\ufeff'.encode('utf-8'))

    writer = csv.writer(response)
    writer.writerow(['ID', 'Название компании', 'ИНН', 'Телефон', 'Email', 'Адрес'])

    for s in suppliers:
        writer.writerow([
            s.id,
            s.company_name,
            s.inn,
            s.phone,
            s.email,
            s.address,
        ])
    return response

@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    if not cart.items.exists():
        messages.error(request, 'Корзина пуста.')
        return redirect('cart')

    if request.method == 'POST':
        total_price = cart.get_total_price()

        order = Order.objects.create(
            user=request.user,
            cart=cart,
            status='оплачен',
            total_price=total_price,
        )

        Payment.objects.create(
            order=order,
            method='Онлайн-оплата (тест)',
            amount=total_price,
            status='успешно',
        )

        Delivery.objects.create(
            order=order,
            tracking_number=f'TEST-{order.id}',
            delivery_address=request.user.address or 'Не указан',
            delivery_status='в обработке',
        )

        messages.success(request, f'Заказ #{order.id} оформлен и оплачен.')
        return redirect('order_detail', pk=order.pk)

    total_price = cart.get_total_price()
    return render(request, 'store/checkout.html', {
        'cart': cart,
        'total_price': total_price,
    })


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).select_related('payment', 'delivery')
    return render(request, 'store/order_list.html', {'orders': orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.select_related('payment', 'delivery', 'cart'),
        pk=pk,
        user=request.user,
    )
    return render(request, 'store/order_detail.html', {'order': order})

@login_required
def supplier_products(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    products = Product.objects.filter(supplier=supplier)
    return render(request, 'store/supplier_products.html', {
        'supplier': supplier,
        'products': products,
    })
