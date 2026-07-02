from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def inicio(request):
    if request.user.username == 'almacen':
        return redirect('almacen_panel')
    return render(request, 'core/inicio.html')