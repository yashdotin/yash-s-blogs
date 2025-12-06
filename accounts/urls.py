from django.urls import path
from django.contrib.auth import views as auth_views
from . import views as account_views


urlpatterns = [
    path('signup/', account_views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html',
        redirect_authenticated_user=True,
    ), name='login'),
    path('logout/', account_views.logout_view, name='logout'),
    path('profile/', account_views.edit_profile, name='edit_profile'),
]