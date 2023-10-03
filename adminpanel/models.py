from django.db import models

# Create your models here.
from django.db import models

# Create your models here.

class Category(models.Model):
    
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Game(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    coins = models.PositiveIntegerField()
    time_of_creation = models.DateTimeField(auto_now_add=True)
    banner_image = models.ImageField(upload_to='game_banners/' , null=True)
    cover_image = models.ImageField(upload_to='game_covers/', null=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    featured = models.BooleanField(default=False )
    purchases = models.PositiveIntegerField(default=0) 

    def __str__(self):
        return self.name
    

class CoinsPack(models.Model):
    coins = models.PositiveIntegerField()
    offer = models.PositiveIntegerField()

    @property
    def total_price(self):
        return self.coins * 15  # Assuming 1 coin = 15 dollars

    @property
    def price_after_offer(self):
        return self.total_price - ((self.offer / 100) * self.total_price)

    def __str__(self):
        return f"{self.coins} Coins Pack with {self.offer}% Offer"
    

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    expiration_date = models.DateField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code