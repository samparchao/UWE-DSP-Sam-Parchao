from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from Authentication.forms import LoginForm, RegisterForm
from Recommendations.models import TopicPreference

# Create your views here.
# Login View
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Authenticate the user
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
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
    return render(request, 'login.html', {'form': form})

#Standard django logout
def logout_view(request):
    logout(request)
    return redirect("login")

#Registration Function
def registration_view(request):
	if request.method == "POST":
		form = RegisterForm(request.POST)
		if form.is_valid():
			user = form.save()
			#login(request, user)
			return redirect("login")
		messages.error(request, "Unsuccessful registration. Invalid information.")
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