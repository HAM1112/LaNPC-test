from django.contrib import admin

from .models import Game , Category , CoinsPack , Coupon

# Register your models here.

admin.site.register(Game)
admin.site.register(Category)
admin.site.register(CoinsPack)
admin.site.register(Coupon)