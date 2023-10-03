from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.signIn , name='admin-signin'),
    path('home/' , views.adminHome, name='admin-home'),
    path('logout/', views.adminLogout, name="admin-logout"),
    
    # users related
    path('users/' , views.usersList , name='userslist'),
    path('user/<int:userId>/' , views.singleUser , name='user-details'),
    path('edituser/<int:userId>/', views.editUser , name='edit-user'),
    
    # games related
    path('games/' , views.gamesList , name='gameslist'),
    path('game/<int:gameId>/' , views.singleGame , name='game-details'),
    path('editGame/<int:gameId>/' , views.editGame , name='edit-game'),
    path('delGame/<int:gameId>' , views.deleteGame , name="delete-game"),
    
    # category related
    path('categories/' , views.categoriesList , name='categorieslist'),
    path('delCategory/<int:categoryId>' , views.deleteCategory , name='deleteCategory'),
    
    # Coins related
    path('coins/' , views.coinsList , name="coinslist"),
    path('delCoins/<int:coinsId>' , views.deleteCoins , name="delete-coins"),
    
    # Coupon related
    path('coupons/', views.couponList , name="couponslist" ),
    path('delcoupon/<int:couponId>', views.deleteCoupon , name="delete-coupon" ),
    path('togCouponActive/<int:couponId>', views.toggoleCouponActive , name="toggle-coupon-active" ),
    
]
