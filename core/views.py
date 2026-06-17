from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def inicio(request):
    return render(request, 'core/inicio.html')
