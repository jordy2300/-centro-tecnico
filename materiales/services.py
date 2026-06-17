import uuid
import openpyxl
from io import BytesIO
from django.utils import timezone
from .models import Material, Cuadrilla, Solicitud, ItemSolicitud


def importar_materiales(ruta):
    import pandas as pd
    df = pd.read_excel(ruta)
    creados, actualizados = 0, 0
    for _, row in df.iterrows():
        codigo = str(row.get('Codigo', '') or '').strip()
        descripcion = str(row.get('Descripcion', '') or '').strip()
        unidad = str(row.get('Unidad', '') or '').strip()
        if not codigo or not descripcion:
            continue
        obj, created = Material.objects.update_or_create(
            codigo=codigo,
            defaults={'descripcion': descripcion, 'unidad': unidad, 'activo': True}
        )
        if created: creados += 1
        else: actualizados += 1
    return {'creados': creados, 'actualizados': actualizados}


def exportar_solicitudes_excel(solicitudes_qs):
    """Genera el Excel con el mismo formato de Plantilla_Almacen (Datos1 + Datos2)."""
    wb = openpyxl.Workbook()

    # ── Hoja Datos1 ──
    ws1 = wb.active
    ws1.title = 'Datos1'
    ws1.append(['ID_Solicitud', 'Movil', 'Nombre_solicitante', 'Fecha_solicitud'])
    for s in solicitudes_qs:
        ws1.append([
            str(s.id)[:8],
            s.cuadrilla.movil,
            s.cuadrilla.nombre,
            s.fecha_solicitud.strftime('%Y-%m-%d'),
        ])

    # ── Hoja Datos2 ──
    ws2 = wb.create_sheet('Datos2')
    ws2.append(['ID_Detalle', 'ID_Solicitud', 'Descripcion_material',
                'Descripcion_texto', 'Codigo_material', 'Cantidad', 'Unidad', 'Serie', 'AcoBro'])
    for s in solicitudes_qs:
        for item in s.items.select_related('material'):
            ws2.append([
                str(uuid.uuid4())[:8],
                str(s.id)[:8],
                item.material.codigo,
                item.material.descripcion,
                item.material.codigo,
                float(item.cantidad_solicitada),
                item.material.unidad,
                item.serie or '',
                'A cobro' if item.acobro == 'cobro' else 'Sin cobro',
            ])

    out = BytesIO()
    wb.save(out)
    out.seek(0)
    return out
