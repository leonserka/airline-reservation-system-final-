from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from ..forms import RegisterForm

def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.is_staff = False
        user.save()
        login(request, user)
        return redirect("home")
    return render(request, "flights/register.html", {"form": form})

def custom_logout(request):
    logout(request)
    return redirect("home")
