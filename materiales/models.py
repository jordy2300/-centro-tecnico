from django.db import models
from django.contrib.auth.models import User
import uuid


class Material(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=300)
    unidad = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Material'
        verbose_name_plural = 'Materiales'
        ordering = ['descripcion']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"


class Cuadrilla(models.Model):
    codigo = models.CharField(max_length=10, unique=True)  # 0001, 0002...
    nombre = models.CharField(max_length=100)
    movil = models.CharField(max_length=20)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Cuadrilla'
        verbose_name_plural = 'Cuadrillas'
        ordering = ['movil']

    def __str__(self):
        return f"{self.movil} - {self.nombre}"


class Solicitud(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de Revisión'),
        ('aprobada', 'Aprobada'),
        ('en_entrega', 'Pendiente de Entrega'),
        ('entregada', 'Entregada Totalmente'),
        ('parcial', 'Entregada Parcialmente'),
        ('cerrada', 'Cerrada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cuadrilla = models.ForeignKey(Cuadrilla, on_delete=models.PROTECT)
    fecha_solicitud = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    observaciones = models.TextField(blank=True)
    aprobado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitudes_aprobadas')
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Solicitud'
        verbose_name_plural = 'Solicitudes'
        ordering = ['-creado']

    def __str__(self):
        return f"{self.cuadrilla.movil} - {self.fecha_solicitud} - {self.get_estado_display()}"

    def id_corto(self):
        return str(self.id)[:8]

    def total_items(self):
        return self.items.count()

    def puede_editar(self):
        return self.estado == 'pendiente'


class ItemSolicitud(models.Model):
    ACOBRO_CHOICES = [
        ('cobro', 'A Cobro'),
        ('sin_cobro', 'Sin Cobro'),
    ]
    ENTREGA_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('entregado', 'Entregado'),
        ('parcial', 'Entregado Parcialmente'),
        ('no_disponible', 'No Disponible'),
    ]

    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='items')
    material = models.ForeignKey(Material, on_delete=models.PROTECT)
    cantidad_solicitada = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_entregada = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    acobro = models.CharField(max_length=10, choices=ACOBRO_CHOICES, default='sin_cobro')
    estado_entrega = models.CharField(max_length=20, choices=ENTREGA_CHOICES, default='pendiente')
    serie = models.CharField(max_length=100, blank=True)
    observacion = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'Item de Solicitud'
        verbose_name_plural = 'Items de Solicitud'

    def __str__(self):
        return f"{self.material.descripcion} x{self.cantidad_solicitada}"

    def cantidad_pendiente(self):
        return self.cantidad_solicitada - self.cantidad_entregada
