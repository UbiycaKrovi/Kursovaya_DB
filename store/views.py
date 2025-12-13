from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Category

def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'store/product_list.html', {
        'products': products, 
        'categories': categories
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {
        'product': product
    })