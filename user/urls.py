from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home , name='home' ),
    path('browse/', views.browse , name='browse' ),
    path('profile/', views.profile , name='profile' ),
    
    path('allgames/' , views.allGames , name='all-games'),
    path('game/<int:gameId>/' , views.gameDetails , name='game'),
    path('buyGame/<int:gameId>', views.buyGame, name='buy-game'),     
    path('download/<int:game_id>/', views.download_game_images, name='download_game'),
    
    path('category/<int:categoryId>/' , views.categoryGame , name='category-game'),
    path('addWishList/<int:gameId>', views.addWishList, name='add-wishlist'),     
    path('delWishList/<int:gameId>', views.delWishList, name='del-wishlist'),     
       
    path('coins/', views.coins , name='coins'),
    path('chat/<int:game_id>/', views.chatRooms, name='chat-rooms'),

    path('logout/', views.userLogout, name='user-logout'),
]
