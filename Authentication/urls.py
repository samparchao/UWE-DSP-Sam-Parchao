from django.urls import path
from Authentication import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = "authentication"

urlpatterns = [
    path("", views.login_view, name="login"),
    path("signup/", views.registration_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("myAccount/", views.myAccount, name="myAccount"),
    path('delete-preferences/', views.delete_preferences, name='delete_preferences'),
    path('delete-account/', views.delete_account, name='delete_account'),
]

urlpatterns += staticfiles_urlpatterns()