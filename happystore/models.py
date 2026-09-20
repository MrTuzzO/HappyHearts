from django.db import models
from decimal import Decimal
from users.models import User
# Create your models here.



class Products(models.Model):
    STATUS_CHOICES = (
        ("active", "Active"),
        ("draft", "Draft")
    )

    item_name=models.CharField(max_length=250)
    description=models.TextField(blank=True)
    
    sock_quantity=models.IntegerField()
    lower_alart = models.IntegerField()

    regular_price=models.DecimalField(max_digits=10, decimal_places=2)
    selling_price=models.DecimalField(max_digits=10, decimal_places=2,default=0.00)

    status = models.CharField(max_length=250, choices=STATUS_CHOICES, default='pending')

    sell_count = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ProductImage(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    product_image = models.ImageField(upload_to='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OrderdProudcts(models.Model):
    item=models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity=models.IntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_total(self):
        price = (
            self.item.selling_price
            if self.item.selling_price > Decimal("0.00")
            else self.item.regular_price
        )
        return price * self.quantity


class Order(models.Model):
    STATUS_CHOICES = (
        ('cancel', 'Cancel'),
        ('received', 'Received'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('packed', 'Packed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered')
    )

    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(OrderdProudcts, related_name="orders")
    delivary_location = models.TextField()
    total = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    
    is_paid = models.BooleanField(default=False)

    order_status=models.CharField(max_length=250, choices=STATUS_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_total(self):
        return sum(
            product.total
            for product in self.products.all()
        )