from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone 

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Администратор'),
        ('supplier', 'Поставщик'),
        ('customer', 'Покупатель'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone']

    email = models.EmailField(
    'email address', 
    unique=True,
    error_messages={'unique': "A user with that email already exists."},
    )
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_supplier(self):
        return self.role == 'supplier'
    
    def is_customer(self):
        return self.role == 'customer'

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

class Supplier(models.Model):
    company_name = models.CharField(max_length=100, unique=True)
    inn = models.CharField(max_length=12)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return self.company_name
        
    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'

class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def get_average_rating(self):
        reviews = self.review_set.all()
        if reviews:
            return sum([r.rating for r in reviews]) / len(reviews)
        return None
    
    def __str__(self):
        return self.name

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_total_price(self):
        return sum([item.product.price * item.quantity for item in self.items.all()])
    
    def __str__(self):
        return f"Корзина {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def update_status(self, new_status):
        self.status = new_status
        self.save()

    def __str__(self):
        return self.name

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    method = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20)
    transaction_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Delivery(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    tracking_number = models.CharField(max_length=50)
    delivery_date = models.DateField(null=True, blank=True)
    shipped_date = models.DateField(null=True, blank=True)
    delivery_address = models.CharField(max_length=255)
    delivery_status = models.CharField(max_length=20)

    def __str__(self):
        return self.name