from django.contrib import admin
from .models import Correo, HistorialCorreo

@admin.register(Correo)
class CorreoAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'asunto', 'fecha_recibido', 'fecha_limite', 'responsable', 'estado']
    list_filter = ['estado', 'revision']
    search_fields = ['cliente', 'asunto']

@admin.register(HistorialCorreo)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ['correo', 'usuario', 'campo', 'valor_anterior', 'valor_nuevo', 'fecha']
