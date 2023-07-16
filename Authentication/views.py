import datetime
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from Authentication.forms import LoginForm, RegisterForm
from Recommendations.models import DailyTaskFlag, TopicPreference
from Recommendations.views import fetch_articles_from_categories
from django.contrib.auth.decorators import login_required

# Create your views here.
# Login View
def login_view(request):
    print_output = None  # Define print_output variable outside the if block

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Authenticate the user
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Check if the news has been fetched for the day
                today = datetime.date.today()
                news_fetched_today = DailyTaskFlag.objects.filter(date=today).exists()

                if not news_fetched_today:
                    # Fetch the news and capture the printed output
                    import io
                    from contextlib import redirect_stdout

                    f = io.StringIO()
                    with redirect_stdout(f):
                        fetch_articles_from_categories(capture_output=True)

                    print_output = f.getvalue()

                    # Create the flag to mark the news as fetched for the day
                    DailyTaskFlag.objects.create(date=today)

                # Login the user
                login(request, user)
                print("SUCCESSFUL LOGIN----------------------------------------------------------------")

                # Check if the user has selected topics
                topic_preference = TopicPreference.objects.filter(user=user).first()
                if topic_preference is None:
                    # User hasn't selected topics, redirect to select topics page
                    return redirect('recommendations:select_topics')
                else:
                    # User has selected topics, redirect to desired page
                    return redirect('index:home')
            else:
                # Authentication failed
                messages.error(request, "Invalid username or password.")
                print("FAILED LOGIN----------------------------------------------------------------")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form, 'print_output': print_output})




#Standard django logout
def logout_view(request):
    logout(request)
    return redirect("authentication:login")

#Registration Function
def registration_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect("authentication:login")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = RegisterForm()
    return render(request, 'signup.html', {'form': form})

def myAccount(request):
    user = request.user
    if request.method == 'POST':
        form = RegisterForm(request.POST, instance=request.user)
        # update the user's details
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('firstname')
        user.last_name = request.POST.get('surname')
        user.save()
    else:
        form = RegisterForm(instance=request.user)

    return render(request, 'myAccount.html', {'form': form})

def delete_preferences(request):
    user = request.user
    TopicPreference.objects.filter(user=user).delete()
    messages.success(request, 'Topic preferences deleted.')
    return redirect('recommendations:select_topics')  

@login_required
def delete_account(request):
    if request.method == 'POST':
        # Delete the account logic
        user = request.user
        user.delete()
        messages.success(request, 'Your account has been deleted.')
        return redirect('authentication:login')  