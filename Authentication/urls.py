from django.urls import path
from Authentication import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("", views.login_view, name="login"),
    path("signup/", views.registration_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
]

urlpatterns += staticfiles_urlpatterns()