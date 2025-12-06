from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_http_methods
from django import forms
from django.contrib.auth.decorators import login_required

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('profile_image', 'name', 'location', 'about', 'email')
        widgets = {
            'profile_image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'accept': 'image/*'
            }),
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Your full name'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'City, Country'
            }),
            'about': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Tell us about yourself...',
                'rows': 4
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'your@email.com'
            })
        }


@require_http_methods(["GET", "POST"])
def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/signup.html', {'form': form})


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def edit_profile(request):
    """Edit user profile: image, name, location, about."""
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})


@require_http_methods(["POST", "GET"])
def logout_view(request):
    """Log out the user and redirect to home. Accepts POST (preferred) and GET for safety.
    We call Django's logout to ensure the session is cleared.
    """
    if request.user.is_authenticated:
        # perform logout
        logout(request)
    return redirect('home')
