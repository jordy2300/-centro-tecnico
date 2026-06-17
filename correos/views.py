from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from datetime import date

from .models import Correo, HistorialCorreo


def _registrar_historial(correo, usuario, campo, anterior, nuevo):
    if str(anterior) != str(nuevo):
        HistorialCorreo.objects.create(
            correo=correo, usuario=usuario,
            campo=campo, valor_anterior=str(anterior), valor_nuevo=str(nuevo)
        )


@login_required
def lista_correos(request):
    qs = Correo.objects.select_related('responsable')
    
    # Filtros
    q = request.GET.get('q', '')
    estado = request.GET.get('estado', '')
    responsable_id = request.GET.get('responsable', '')
    desde = request.GET.get('desde', '')
    hasta = request.GET.get('hasta', '')
    vista = request.GET.get('vista', 'todos')

    if q:
        qs = qs.filter(Q(cliente__icontains=q) | Q(asunto__icontains=q))
    if estado:
        qs = qs.filter(estado=estado)
    if responsable_id:
        qs = qs.filter(responsable_id=responsable_id)
    if desde:
        qs = qs.filter(fecha_recibido__gte=desde)
    if hasta:
        qs = qs.filter(fecha_recibido__lte=hasta)
    if vista == 'pendientes':
        qs = qs.exclude(estado__in=['respondido', 'gestionado'])
    elif vista == 'criticos':
        hoy = date.today()
        qs = qs.filter(fecha_limite__lte=hoy).exclude(estado__in=['respondido', 'gestionado'])

    # Estadísticas
    todos = Correo.objects.all()
    stats = {
        'total': todos.count(),
        'pendientes': todos.filter(estado='pendiente').count(),
        'ejecutados': todos.filter(ejecutado=True).count(),
        'respondidos': todos.filter(respondido=True).count(),
    }

    usuarios = User.objects.filter(is_active=True)
    correos = list(qs)
    
    # Anotar alerta para ordenar: critico primero
    correos_raw = list(qs)
    
    correos = []
    for c in correos_raw:
        alerta = c.alerta()
        dias = c.dias_restantes()
        correos.append({
            'obj': c,
            'alerta': alerta,
            'dias': dias,
            'orden': 0 if alerta == 'critico' else 1 if alerta == 'proximo' else 2,
        })

    correos.sort(key=lambda x: (x['orden'], x['obj'].fecha_limite or date.max))

    return render(request, 'correos/lista.html', {
        'correos': correos,
        'stats': stats,
        'usuarios': usuarios,
        'estados': Correo.ESTADO_CHOICES,
        'filtros': {
            'q': q, 'estado': estado, 'responsable': responsable_id,
            'desde': desde, 'hasta': hasta, 'vista': vista,
        },
    })


@login_required
def nuevo_correo(request):
    if request.method == 'POST':
        correo = Correo.objects.create(
            cliente=request.POST.get('cliente', '').strip(),
            asunto=request.POST.get('asunto', '').strip(),
            fecha_recibido=request.POST.get('fecha_recibido'),
            responsable_id=request.POST.get('responsable') or None,
            estado=request.POST.get('estado', 'pendiente'),
            observaciones=request.POST.get('observaciones', ''),
            creado_por=request.user,
        )
        messages.success(request, f'Correo de {correo.cliente} registrado correctamente.')
        return redirect('lista_correos')
    usuarios = User.objects.filter(is_active=True)
    return render(request, 'correos/form.html', {
        'usuarios': usuarios,
        'estados': Correo.ESTADO_CHOICES,
        'accion': 'Nuevo',
    })


@login_required
def editar_correo(request, pk):
    if not request.user.is_superuser:
        messages.error(request, 'Solo el administrador puede editar correos.')
        return redirect('lista_correos')
    correo = get_object_or_404(Correo, pk=pk)
    if request.method == 'POST':
        # Registrar historial de cambios
        campos = {
            'cliente': request.POST.get('cliente', '').strip(),
            'asunto': request.POST.get('asunto', '').strip(),
            'estado': request.POST.get('estado', correo.estado),
            'responsable_id': request.POST.get('responsable') or None,
            'observaciones': request.POST.get('observaciones', ''),
        }
        _registrar_historial(correo, request.user, 'estado', correo.estado, campos['estado'])
        _registrar_historial(correo, request.user, 'responsable', correo.responsable_id, campos['responsable_id'])

        correo.cliente = campos['cliente']
        correo.asunto = campos['asunto']
        correo.estado = campos['estado']
        correo.responsable_id = campos['responsable_id']
        correo.observaciones = campos['observaciones']
        correo.fecha_recibido = request.POST.get('fecha_recibido', correo.fecha_recibido)
        # Recalcular fecha límite si cambió la fecha recibido
        correo.fecha_limite = None
        correo.save()
        messages.success(request, 'Correo actualizado.')
        return redirect('lista_correos')
    usuarios = User.objects.filter(is_active=True)
    return render(request, 'correos/form.html', {
        'correo': correo,
        'usuarios': usuarios,
        'estados': Correo.ESTADO_CHOICES,
        'accion': 'Editar',
    })


@login_required
@require_POST
def eliminar_correo(request, pk):
    if not request.user.is_superuser:
        messages.error(request, 'Solo el administrador puede eliminar correos.')
        return redirect('lista_correos')
    correo = get_object_or_404(Correo, pk=pk)
    correo.delete()
    messages.success(request, 'Correo eliminado.')
    return redirect('lista_correos')


@login_required
@require_POST
def cambiar_estado_rapido(request, pk):
    """Cambia ejecutado/respondido desde la tabla principal."""
    correo = get_object_or_404(Correo, pk=pk)
    campo = request.POST.get('campo')
    valor = request.POST.get('valor') == 'true'

    if campo == 'ejecutado':
        correo.ejecutado = valor
        if valor:
            correo.estado = 'gestionado'
    elif campo == 'respondido':
        correo.respondido = valor
        if valor:
            correo.estado = 'respondido'

    correo.save()
    _registrar_historial(correo, request.user, campo, not valor, valor)
    return JsonResponse({'ok': True, 'estado': correo.estado})


@login_required
@require_POST  
def cambiar_revision(request, pk):
    if not request.user.is_superuser:
        return JsonResponse({'ok': False, 'error': 'Sin permiso'})
    correo = get_object_or_404(Correo, pk=pk)
    revision = request.POST.get('revision', 'pendiente')
    _registrar_historial(correo, request.user, 'revision', correo.revision, revision)
    correo.revision = revision
    correo.save()
    return JsonResponse({'ok': True})


@login_required
def detalle_correo(request, pk):
    correo = get_object_or_404(Correo, pk=pk)
    historial = correo.historial.select_related('usuario').all()
    return render(request, 'correos/detalle.html', {
        'correo': correo, 'historial': historial,
    })
