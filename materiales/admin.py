from django.contrib import admin
from .models import Material, Cuadrilla, Solicitud, ItemSolicitud

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'descripcion', 'unidad', 'activo']
    search_fields = ['codigo', 'descripcion']
    list_filter = ['activo']

@admin.register(Cuadrilla)
class CuadrillaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'movil', 'activo']

class ItemInline(admin.TabularInline):
    model = ItemSolicitud
    extra = 0

@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = ['id', 'cuadrilla', 'fecha_solicitud', 'estado']
    list_filter = ['estado']
    inlines = [ItemInline]
