from django import forms
from .models import Game , Coupon

class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['name', 'description', 'coins', 'banner_image', 'cover_image', 'category', 'featured']
        # fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'mt-1 p-2 w-full border rounded-md text-black' , 'value' : ''}),
            'description': forms.Textarea(attrs={'class': 'mt-1 p-2 w-full border rounded-md text-black'}),
            'coins': forms.NumberInput(attrs={'class': 'mt-1 p-2 w-full border rounded-md text-black'}),
            'banner_image': forms.FileInput(attrs={'class': 'mt-1 text-black'}),
            'cover_image': forms.FileInput(attrs={'class': 'mt-1 text-black'}),
            'category': forms.Select(attrs={'class': 'mt-1 p-2 w-full border rounded-md text-black text-black'}),
            'featured': forms.CheckboxInput(attrs={'class': 'mt-1 text-black' }),
        }

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount', 'expiration_date', 'active']