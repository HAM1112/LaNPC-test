# standard library
import os
import io
import zipfile
from datetime import datetime


# Django
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt

# local Django
from .models import Wishlist , PurchasedGame , Review , Message
from account.models import Transaction , User
from adminpanel.models import Game , Category , CoinsPack


# --------------------------------------------------#
# ------------------Home Page-----------------------#
# --------------------------------------------------#

# @login_required()
def home(request):
    # get user details from request.user
    user = request.user
    
    try:
        # get all games of the user . empty if there is no game
        mygames = PurchasedGame.objects.filter(user=request.user) if request.user.id else []
    except Exception as e:
        # Handle the exception here (e.g., log it or provide an appropriate response)
        print(e)
        mygames = []  # Assign an empty list in case of an exception

        
    # retrieve all game order by the date (newest games first)  
    latest_games = Game.objects.order_by('-time_of_creation')[:8]
    
    # adding context 
    context = {
        'latests' : latest_games,
        'mygames' : mygames,
    }
    
    return render(request , 'user/home.html' , context)

# --------------------------------------------------#
# ------------------Game details--------------------#
# --------------------------------------------------#
def gameDetails(request , gameId):
    # retrieve game using gameid in the url 
    game = Game.objects.get(id=gameId)
    
    if request.method == "POST":
        # retrieve data from post
        rating  = request.POST.get('rate')
        description = request.POST.get('description')
        
        # save review to the database
        review = Review.objects.create(
            user = request.user,
            game = game,
            rating = rating,
            description = description
        )
        review.save()
        
        return redirect('game' , gameId = gameId ) # redirect to same page  (redirection is for avoiding resubmisson)
    
    count = 0 # total number of reviews
    total = 0 
    reviews = Review.objects.filter(game=game)
    
    for review in reviews:
        count += 1
        total += review.rating
    
    if count > 0:
        rating = total / count
    else:
        rating = 4.5
        
    reviews_with_description = Review.objects.filter(game=game).exclude(description__isnull=True).exclude(description__exact='')
    
    related_games = Game.objects.filter(category=game.category).exclude(id=game.id)
    wishlist = Wishlist.objects.filter(user = request.user , game = game).exists()
    
    no_of_downloads_left = 3
    
    # check wheather the game is purchased or not
    try:
        purchased_game = PurchasedGame.objects.get(game=game, user=request.user)
        purchased = True
        
        no_of_downloads_left = 3 - purchased_game.download_count
    except PurchasedGame.DoesNotExist:
        purchased = False

    print(no_of_downloads_left)
    context = {
        'game' : game,
        'related' : related_games,
        'wishlist' : wishlist,
        'purchased' : purchased,
        'reviews' : reviews,
        'reviews_discription' : reviews_with_description,
        'rating' : rating,
        'no_of_downloads_left':no_of_downloads_left
    }
    return render(request , 'user/gamedetails.html' , context )

def allGames(request):
    # filter and sort game based on the requirement 
    if request.method == "POST":
        selected = request.POST['selected']
        search = request.POST['search']
        category = request.POST['category']
        
        # if category is all give all category 
        if category == "All":
            # serach empty then get all games
            if search == '':
                games = Game.objects.all()
            
            else : #search with keyword
                games = Game.objects.filter(name__istartswith=search)
        else:
            if search == '':
                games = Game.objects.filter(category=category)
            else :
                games = Game.objects.filter(name__istartswith=search , category=category)
        
        # sorting based on the given option
        if selected == 'latest':
            games = games.order_by('-time_of_creation')
        elif selected == 'oldest':
            games = games.order_by('time_of_creation')
        elif selected == 'highcoin':
            games = games.order_by('-coins')
        elif selected == 'lowcoin' :
            games = games.order_by('coins')
            
        #  passing all categories for the select/option
        categories = Category.objects.order_by('name')
        
        context = {
            'games' : games,
            'selected' : selected,
            'search' : search,
            'categories' : categories,
            'c_selected' : category,
            'search' : search,
        }
        return render(request , 'user/exploregames.html' , context )
    
    games = Game.objects.all()
    categories = Category.objects.all()
    context = {
        'games' : games,
        'categories' : categories,
    }
    return render(request, 'user/exploregames.html' , context)

def categoryGame(request , categoryId):
    games = Game.objects.filter(category = categoryId)
    categories = Category.objects.all()
    context = {
        'games' : games,
        'categories' : categories,
    }
    return render(request, 'user/exploregames.html' , context)

def browse(request):
    # retrieve all games and all categories
    games = Game.objects.all()
    categories = Category.objects.all()
    
    top_coins = Game.objects.order_by('-coins')[:3]
    other_games = Game.objects.all()[:6]
  
    
    try:
        # get games purchased by the user
        user_games = PurchasedGame.objects.filter(user=request.user)
        for purchased_game in user_games:
            date_added = purchased_game.time_added.date()
            print(date_added)
        print(user_games)
    except Exception as e:
        print("user is not signed in !!!!!!Please in sign in")
        user_games = None  # Assign a default value or handle the error as needed

    context = {
        'games' : games,
        'categories' : categories,
        'top_coins' : top_coins,
        'other_games' : other_games,   
        'user_games' : user_games,
    }   
    return render(request , 'user/browse.html' , context )

@login_required # login is must for buying game 
def buyGame(request , gameId):
    
    game = Game.objects.get(id=gameId)
    user = request.user
    if not user.is_authenticated: # check weather user is authenticated
        return redirect('acc-signin')
     
    #  if already purchased redirect to the game page
    if PurchasedGame.objects.filter(user=user, game=game).exists():
        return redirect('game' , gameId)
    
    # check the nessasary conditions of the webpage
    if user.coins >= game.coins:
        purchase = PurchasedGame.objects.create(user=user , game=game)
        purchase.save()
        user.coins -= game.coins
        user.save()   
        game.purchases += 1
        game.save()
        
        try:
            # Try to get the Wishlist object if it exists
            wishlist_entry = Wishlist.objects.get(user=user, game=game)
            
            # If it exists, delete it
            wishlist_entry.delete()
        except ObjectDoesNotExist:
            # Handle the case where the Wishlist entry doesn't exist
            pass
        
        return redirect('profile')
    else: # return to coins page if no enought coins
        return redirect('coins')

# Adding game to wishlist
def addWishList(request , gameId):
    print(request.user)
    user = request.user
    wishlist = Wishlist.objects.create(user = user , game_id = gameId)
    wishlist.save()
    return redirect('game' , gameId=gameId)
# deleting game from wishlist
def delWishList(request, gameId):
    
    try:
        user = request.user
        wishlist = Wishlist.objects.get(user=user, game_id=gameId)
        wishlist.delete()
        return redirect('profile')
    except ObjectDoesNotExist:
        print(ObjectDoesNotExist)
        return redirect('profile')

# display coins packages
def coins(request):
    # clearing session if this page is redirected from payment canceled or payement succesful page 
    if 'pack_id' in request.session:
        del request.session['pack_id']
    if 'in_id' in request.session:
        del request.session['in_id']
    if 'details' in request.session:
        del request.session['details']
    if 'amount' in request.session:
        del request.session['amount']
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
        
    coinsPack = CoinsPack.objects.order_by('coins')
    context = {
        'coins' : coinsPack,
    }
    return render(request, 'user/coins.html' , context)

# display profile page
def profile(request):
    # update profile details
    if request.method == "POST":
        username = request.POST.get('username')
        first_name = request.POST.get('firstname')
        second_name = request.POST.get('secondname')
        dob_str = request.POST.get('dob')
        dob_date = datetime.strptime(dob_str, '%Y-%m-%d').date()
   
        user = request.user
        user.username = username
        user.first_name = first_name
        user.last_name = second_name
        user.date_of_birth = dob_date
        user.save()
        
        return redirect('profile')
    
    user = request.user
    if not user.is_authenticated: # user validation
        return redirect('acc-signin')
    

    wishlists = Wishlist.objects.filter(user = user)
    purchased_games = PurchasedGame.objects.filter(user = user)
    
    transactions = Transaction.objects.filter(user=request.user)
    if purchased_games :
        gamechat = purchased_games[0].game
    else:
        gamechat = None
    context = {
        'wishlists' : wishlists,
        'purchased_games' : purchased_games,
        'wishlist_count' : wishlists.count(),
        'purchase_count' : purchased_games.count(),
        'transactions' : transactions,
        "gamechat" : gamechat,
    } 
    return render(request , 'user/profile.html' , context)

# download a zip file containing game images
@csrf_exempt  
def download_game_images(request, game_id):
    # retrieve the game 
    game = Game.objects.get(pk=game_id)
    purchase = PurchasedGame.objects.get(game_id = game_id , user = request.user)
    
    # only three downloads are available
    if purchase.download_count < 3 :
        # creating a temperary directory
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        os.makedirs(temp_dir, exist_ok=True)

        # Create an in-memory ZIP buffer
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zipf:

            # Loop through the banner_image and cover_image associated with the game
            for image in [game.banner_image, game.cover_image]:
                if image:
                    
                    # Get the absolute file path of the image
                    image_path = default_storage.path(image.name)
                    
                    # Add the image to the ZIP file with its original name
                    zipf.write(image_path, os.path.basename(image_path))
        # deleteing ther temperary directory
        os.rmdir(temp_dir)

       # Create an HTTP response with the ZIP archive content
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        
        # Set the Content-Disposition header to suggest a filename for the downloaded ZIP file
        response['Content-Disposition'] = f'attachment; filename="{game.name}_images.zip"'
        
        # Add a JavaScript snippet to reload the current page after the download is initiated
        response.write('<script>window.onload = function() { location.reload(); }</script>')
        
        # Update the download count for the game's purchase record
        purchase.download_count += 1
        purchase.save()
        if purchase.download_count == 3:
            purchase.delete()
        return response
    else:
        purchase.delete()  
        return redirect('game' , game_id)
        
    

def chatRooms(request , game_id):
    # retrieve all purchased games for displaying in the side panel
    purchased_games = PurchasedGame.objects.filter(user = request.user)
    
    # retrieve the game of chat room
    game = Game.objects.get(id=game_id)
    messages = Message.objects.filter(game = game)
    context = {
        'games' : purchased_games,
        'game' : game,
        'messages' : messages,
    }
    return render(request , 'user/chatrooms.html', context)

# user logout 
def userLogout(request):
    logout(request)
    return redirect('home')
