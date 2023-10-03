# Standard library
from datetime import date , datetime ,timedelta
import uuid , hashlib , random

# Django
from django.utils import timezone
from django.db.models import Count , Sum
from django.db.models.functions import ExtractMonth, ExtractYear
from django.shortcuts import render
from django.core import serializers
from django.shortcuts import render , redirect
from django.http import HttpResponse , JsonResponse
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate
from django.contrib import auth

# local Django
from account.models import User , Transaction
from user.models import Wishlist , PurchasedGame , Review
from .models import Game , Category , CoinsPack , Coupon 
from .utils import get_monthly_income_for_current_year , get_income_by_month_last_year , get_income_this_week, get_income_last_week , random_hex
from .forms import GameForm , CouponForm

# Create your views here.
def is_superuser(user):
    return user.is_superuser

@never_cache
def signIn(request):    
    # check if user is already logged-in  
    if request.user.is_authenticated and request.session.get('admin'):
        return redirect('admin-home')
    
    # validate details 
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        admin = authenticate(request , username = username, password = password)
        # check if user is admin
        if admin is not None and admin.is_superuser:
            request.session['admin'] = username
            auth.login(request , admin)
            return redirect('admin-home')
        else:
            return render(request , 'adminpanel/login.html', {'error' : 'Invalid username or password'})   
    return render(request , 'adminpanel/login.html' )

@never_cache
@user_passes_test(is_superuser)
def adminHome(request):
    # validating admin
    if request.session.get('admin') is None:
        return redirect('admin-signin')
    
    # retreive all games and users ............so on
    users = User.objects.all()
    games = Game.objects.all()
    purchase_history = PurchasedGame.objects.order_by('-time_added').all()
    transactions = Transaction.objects.all()
    
    total_income = 0
    # calculate total income 
    for transaction in transactions:
        if transaction.status:
            total_income += transaction.coins_pack.price_after_offer
   
    # calculate current montly income
    monthly_income = get_monthly_income_for_current_year()
    # calculate last montly income
    last_year_income = get_income_by_month_last_year()
    # calculate this week income
    this_week = get_income_this_week()
    # calculate last week income
    last_week = get_income_last_week()
    
    latest_reviews = Review.objects.all()[:5]
    context = {
        'usersCount' : users.count(),
        'gamesCount' : games.count(),
        'income' : total_income,
        'purchaseCount' : purchase_history.count(),
        'purchase_history' : purchase_history,
        "monthly_income" : monthly_income,     
        'last_year_income' : last_year_income,
        'this_week' : this_week,
        'last_week' : last_week,
        'latest_reviews' : latest_reviews,
        
    }
    
    return render(request , 'adminpanel/adminhome.html' , context )

@never_cache
def adminLogout(request):
    # request.session.flush()
    request.session.pop('admin', None)
    auth.logout(request)
    return redirect('admin-signin')

#-----------------------------------------------#
# ------------- USER RELATED ------------------ #
#-----------------------------------------------#

# Display all users in a table
@user_passes_test(is_superuser)
def usersList(request):
    # users = User.objects.filter(is_superuser=False)
    users = User.objects.all()   
    context = {
        'users' : users,
    }
    return render(request , 'adminpanel/usersdetails.html' , context)

# diplay details of single users
@user_passes_test(is_superuser)
def singleUser(request , userId):
    # retreive all neccassary details
    user = User.objects.get(id=userId)
    reviews = Review.objects.filter(user = request.user)
    purchases = PurchasedGame.objects.filter(user=request.user)
    
    context = {
        'user' : user,
        'reviews' : reviews,
        'purchases' : purchases,
        'no_purchases' : purchases.count(),
        'no_reviews' : reviews.count(),
        
    }
    return render(request , 'adminpanel/singleuser.html' , context)
@user_passes_test(is_superuser)
def editUser(request , userId):
    user = User.objects.get(id=userId)
    context = {
        'user' : user,
    }
    return render(request , 'adminpanel/edituser.html' , context)
    
    

#-----------------------------------------------#
# ------------- GAMES RELATED ------------------ #
#-----------------------------------------------#


# Displaying all game inn a table
@user_passes_test(is_superuser)
def gamesList(request):     
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        coins = request.POST.get('coins')
        category = request.POST.get('category')
        # featured = request.POST.get('featured')
        banner_image = request.FILES.get('bannerImage')  # Retrieve uploaded file
        cover_image = request.FILES.get('coverImage')    
        featured = True if request.POST.get('featured') else False

        # create game instance
        game = Game(
            name=name,
            description = description,
            coins = coins,
            banner_image = banner_image,
            cover_image = cover_image,
            featured = featured,
            category_id = category
        )
        game.save()
        
    games = Game.objects.all()
    categories = Category.objects.all()
    context = {
        'games': games,
        'categories': categories,
    }
    print()
    return render(request, 'adminpanel/gamesdetails.html', context)

# display single game in detail
@user_passes_test(is_superuser)
def singleGame(request , gameId):
    # get the game details purchase details
    game = Game.objects.get(pk=gameId)
    purchases = PurchasedGame.objects.filter(game_id=gameId)
    for purchase in purchases:
        purchase.id = hashlib.sha256(str(purchase.id).encode()).hexdigest()
        purchase.download_left = 3 - purchase.download_count
    context = {
        'game' : game,
        'purchases' : purchases
    }
    return render(request , 'adminpanel/singlegame.html' , context)

@user_passes_test(is_superuser)
def editGame(request , gameId):
    # get details from post
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        coins = request.POST.get('coins')
        category = request.POST.get('category')
        featured = True if request.POST.get('featured') else False
        
        # get the game and update the values
        game = Game.objects.get(id=gameId)
        # updating values
        game.name = name
        game.description = description
        game.coins = coins 
        game.category_id = category
        game.featured = featured 
        game.save()
        return redirect('game-details', gameId = gameId)
    
    game = Game.objects.get(id=gameId)
    categories = Category.objects.exclude(id=game.category_id).all()
    context = {
        'game' : game,
        'categories' : categories,
    }
    return render(request , 'adminpanel/editgame.html' , context)

@user_passes_test(is_superuser)
def deleteGame(request , gameId):
    # get game and delete it
    game = Game.objects.get(pk=gameId)
    game.delete()
    return redirect('gameslist')

#-----------------------------------------------#
# ------------- CATEGORY RELATED -------------- #
#-----------------------------------------------#


# Listing all categories
@user_passes_test(is_superuser)
def categoriesList(request):
    # add new category
    if request.method == 'POST' and request.POST['category'] != '':
        category = request.POST['category']
        Category.objects.create(name=category)
        return redirect('categorieslist')
    # get all categories all number of games in them
    categories = Category.objects.annotate(game_count=Count('game')).order_by('name')
    # generate random hex . for graph
    for category in categories:
        category.bg_color = random_hex(category.id)
   
    context = {
        'categories' : categories,         
    }  
    return render(request , 'adminpanel/categorydetails.html' , context )

@user_passes_test(is_superuser)
def deleteCategory(request , categoryId):
    # get category and delete it
    category = Category.objects.get(pk = categoryId)
    category.delete()
    return redirect('categorieslist')

#-----------------------------------------------#
# ------------- Coins RELATED ----------------- #
#-----------------------------------------------#
@user_passes_test(is_superuser)
def coinsList(request):
    # add new coin package
    if request.method == "POST" and request.POST.get('add_coin') == "add_coin":
        coins = request.POST.get('coins')
        offer = request.POST.get('offer')
        coinPack = CoinsPack.objects.create(coins = coins , offer = offer)
        coinPack.save()
        return redirect('coinslist')
    
    # for sorting and retriving specific transaction history . used in ajax
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        selected_option = request.POST.get('option')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Convert start_date and end_date to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        # Query the Transaction model to get transactions within the date range
        transaction_history = Transaction.objects.filter(timestamp__range=(start_date, end_date))
        
        if selected_option != "all":
            transaction_history = transaction_history.filter(user_id=selected_option)

        # convert queries into list of dictonaties for giving response to front . Ajax
        transaction_list = [
            {
                'id': transaction.id,
                'user' : transaction.user.username,
                'user_id' : transaction.user.id,
                'no_coins' : transaction.coins_pack.coins,
                'price' : transaction.amount,
                'transaction_id' : transaction.transaction_id,
                'date': transaction.timestamp.date(),
                'time': transaction.timestamp.time(),
                'status' : transaction.status,
            }
            for transaction in transaction_history
        ]
        users_with_transactions = User.objects.filter(transaction__isnull=False).distinct()
        # Convert the serialized data into a Python list of dictionaries
        users_data = [
            {
                'username' : user.username ,
                'user_id' : user.id,

            } for user in users_with_transactions]
        
        #semd the data as Json response  
        data = {
            'transaction_count' : transaction_history.count(),
            'transactions' : transaction_list,
            'users' : users_data,
        }
        return JsonResponse(data)
    # get coin pack and transaction details
    coinsPack = CoinsPack.objects.all()
    transaction_history = Transaction.objects.order_by('-id')
    # convert queries into list of dictonaties for giving response to front . Ajax
    transaction_list = [
        {
            'id': transaction.id,
            'user' : transaction.user.username,
            'user_id' : transaction.user.id,
            'no_coins' : transaction.coins_pack.coins,
            'price' : transaction.amount,
            'transaction_id' : transaction.transaction_id,
            'date': transaction.timestamp.date(),
            'time': transaction.timestamp.time(),
            'status' : transaction.status,
        }
        for transaction in transaction_history
    ]
    
    users_with_transactions = User.objects.filter(transaction__isnull=False).distinct()
    # convert queries into list of dictonaties for giving response to front . Ajax
    users_data = [
        {
            'username' : user.username ,
            'user_id' : user.id,

        } for user in users_with_transactions]

    context = {
        'coins' : coinsPack,
        'transactions' : transaction_list,
        'users' : users_data,
    }
    return render(request , 'adminpanel/coinsdetails.html' , context)

@user_passes_test(is_superuser)
def deleteCoins(request , coinsId):
    coinPack = CoinsPack.objects.get(id = coinsId)
    coinPack.delete()
    return redirect('coinslist')


#-----------------------------------------------#
# ------------- Coupon RELATED ----------------- #
#-----------------------------------------------#

@user_passes_test(is_superuser)
def couponList(request):
    error = None
    # generate new coupon
    if request.method == "POST":
        discount = request.POST.get('discount')
        checked = request.POST.get('active')
        exp_date_str = request.POST.get('date')
        exp_date = datetime.strptime(exp_date_str, '%Y-%m-%d').date()
        today_date = date.today()
        
        if exp_date <= today_date:
            error = "Select tomorrow or above"
        else :
            active = True if checked == 'on' else False
            unique_id = str(uuid.uuid4().int)
            coupon_code = unique_id[:12]
            
            coupon = Coupon.objects.create(
                code = coupon_code,
                discount = discount,
                expiration_date = exp_date,
                active = active
            )
            coupon.save()
    # retrieve all coupon instances
    coupons = Coupon.objects.all().order_by('expiration_date' , 'created_at')
    context = {
        'coupons' : coupons,
    }
    if error :
        context['error'] = error
    return render(request , 'adminpanel/coupon-list.html' , context )

@user_passes_test(is_superuser)
def deleteCoupon(request , couponId):
    # if coupon exists delete it 
    try:
        coupon = Coupon.objects.get(id=couponId)
        coupon.delete()
    except Coupon.DoesNotExist:
        print("some error inc encountered")
    return redirect('couponslist')
@user_passes_test(is_superuser)
def toggoleCouponActive(request, couponId):
    # if coupon exists toggle its status 
    try:
        coupon = Coupon.objects.get(id=couponId)
        coupon.active = not coupon.active
        print(coupon)
        print("reached herex")
        coupon.save()
        return JsonResponse({'success': True, 'active': coupon.active})
    except Coupon.DoesNotExist:
        return JsonResponse({'success': False})