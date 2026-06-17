from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, date


def calcular_dias_habiles(fecha_inicio, dias=8):
    fecha = fecha_inicio
    habiles = 0
    while habiles < dias:
        fecha += timedelta(days=1)
        if fecha.weekday() < 5:
            habiles += 1
    return fecha


def dias_habiles_restantes(fecha_limite):
    hoy = date.today()
    if hoy >= fecha_limite:
        return 0
    dias = 0
    fecha = hoy
    while fecha < fecha_limite:
        fecha += timedelta(days=1)
        if fecha.weekday() < 5:
            dias += 1
    return dias


class Correo(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_revision', 'En Revisión'),
        ('gestionado', 'Gestionado'),
        ('respondido', 'Respondido'),
        ('vencido', 'Vencido'),
    ]
    REVISION_CHOICES = [
        ('pendiente', 'Pend. Revisión'),
        ('omitido', 'Omitido'),
        ('revisado', 'Revisado'),
    ]

    cliente = models.CharField(max_length=200)
    asunto = models.CharField(max_length=500)
    fecha_recibido = models.DateField()
    fecha_limite = models.DateField(blank=True, null=True)
    responsable = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='correos_asignados'
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    revision = models.CharField(max_length=20, choices=REVISION_CHOICES, default='pendiente')
    ejecutado = models.BooleanField(default=False)
    respondido = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True)
    creado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='correos_creados'
    )
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Correo'
        verbose_name_plural = 'Correos'
        ordering = ['fecha_limite', 'fecha_recibido']

    def __str__(self):
        return f"{self.cliente} - {self.asunto[:50]}"

    def save(self, *args, **kwargs):
        if not self.fecha_limite and self.fecha_recibido:
            self.fecha_limite = calcular_dias_habiles(self.fecha_recibido, 8)
        super().save(*args, **kwargs)

    def dias_restantes(self):
        if not self.fecha_limite:
            return None
        return dias_habiles_restantes(self.fecha_limite)

    def esta_vencido(self):
        if not self.fecha_limite:
            return False
        return date.today() > self.fecha_limite and self.estado not in ['respondido', 'gestionado']

    def alerta(self):
        if self.estado in ['respondido', 'gestionado']:
            return 'normal'
        dias = self.dias_restantes()
        if dias is None:
            return 'normal'
        if self.esta_vencido() or dias == 0:
            return 'critico'
        if dias <= 2:
            return 'proximo'
        return 'normal'


class HistorialCorreo(models.Model):
    correo = models.ForeignKey(Correo, on_delete=models.CASCADE, related_name='historial')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    campo = models.CharField(max_length=50)
    valor_anterior = models.CharField(max_length=200, blank=True)
    valor_nuevo = models.CharField(max_length=200, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
