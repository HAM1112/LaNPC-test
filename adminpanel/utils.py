from django.db.models import Sum
from django.utils import timezone
from account.models import Transaction
from django.db.models.functions import ExtractMonth, ExtractYear
import datetime , hashlib


# to get income of every month of this year
def get_monthly_income_for_current_year():
    # Get the current year
    current_year = timezone.now().year
    
    # Initialize a dictionary to store the income for each month
    monthly_income = {}
    
    # Loop through each month of the year
    for month in range(1, 13):
        # Calculate the start and end date for the month
        start_date = timezone.datetime(current_year, month, 1)
        end_date = timezone.datetime(current_year, month + 1, 1) if month < 12 else timezone.datetime(current_year + 1, 1, 1)
        
        # Query the transactions for the current month where status is True
        monthly_transactions = Transaction.objects.filter(
            status=True,
            timestamp__gte=start_date,
            timestamp__lt=end_date
        )
        
        # Calculate the total income for the month
        total_income = monthly_transactions.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Store the income in the dictionary
        monthly_income[month] = total_income
    
    return monthly_income


def get_income_by_month_last_year():
    # Get the current year
    current_year = timezone.now().year
    last_year = current_year - 1
    
    # Initialize a dictionary to store the income for each month
    monthly_income = {}
    
    # Loop through each month of the year
    for month in range(1, 13):
        # Calculate the start and end date for the month
        start_date = timezone.datetime(last_year, month, 1)
        end_date = timezone.datetime(last_year, month + 1, 1) if month < 12 else timezone.datetime(last_year + 1, 1, 1)
        
        # Query the transactions for the current month where status is True
        monthly_transactions = Transaction.objects.filter(
            status=True,
            timestamp__gte=start_date,
            timestamp__lt=end_date
        )
        
        # Calculate the total income for the month
        total_income = monthly_transactions.aggregate(Sum('amount'))['amount__sum'] or 0
        # Store the income in the dictionary
        monthly_income[month] = total_income
    
    return monthly_income


def get_income_this_week():
    today = timezone.now().date()
    start_of_week = today - timezone.timedelta(days=today.weekday())
    end_of_week = start_of_week + timezone.timedelta(days=6)

    income_per_day = Transaction.objects.filter(
        timestamp__date__range=[start_of_week, end_of_week],
        status=True
    ).values('timestamp__date').annotate(total_income=Sum('amount')).order_by('timestamp__date')

    # Create a dictionary to store income for each day of the week
    income_by_day = {start_of_week + timezone.timedelta(days=i): 0 for i in range(7)}

    for entry in income_per_day:
        date = entry['timestamp__date']
        total_income = entry['total_income']
        income_by_day[date] = total_income

    return income_by_day

def get_income_last_week():
    today = timezone.now().date()
    start_of_week = today - timezone.timedelta(days=today.weekday())
    end_of_week = start_of_week + timezone.timedelta(days=6)

    # Calculate the start and end dates of the previous week
    start_of_last_week = start_of_week - timezone.timedelta(days=7)
    end_of_last_week = end_of_week - timezone.timedelta(days=7)

    income_per_day = Transaction.objects.filter(
        timestamp__date__range=[start_of_last_week, end_of_last_week],
        status=True
    ).values('timestamp__date').annotate(total_income=Sum('amount')).order_by('timestamp__date')

    # Create a dictionary to store income for each day of the last week
    income_by_day = {start_of_last_week + timezone.timedelta(days=i): 0 for i in range(7)}

    for entry in income_per_day:
        date = entry['timestamp__date']
        total_income = entry['total_income']
        income_by_day[date] = total_income
    # Print or return the income for each day
    for date, total_income in income_by_day.items():
        print(f"Income on {date.strftime('%A')}: ${total_income:.2f}")
    return income_by_day

def random_hex(id):
    number_to_hash = id  # same id to be hashed

    #convert the id to str
    number_str = str(number_to_hash)

    # hash the converted string  using haslib.sha256()
    hash_obj = hashlib.sha256()
    hash_obj.update(number_str.encode())
    hashed_number = hash_obj.hexdigest()
    number = 100

    for digit_str in number_str:
        digit = int(digit_str)  
        number *= digit
    # generating the hex color code
    start_position = number % (len(hashed_number) - 6) 
    random_subset = hashed_number[start_position:start_position + 6]
    hex_code = f"#{random_subset}" 
    return hex_code