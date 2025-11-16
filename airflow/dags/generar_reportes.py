"""
DAG de Reportes Estadísticos
Genera reportes periódicos con análisis de incidentes y tendencias
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import json
import boto3
from collections import Counter

# Configuración
API_BASE_URL = "https://if1stu7r2g.execute-api.us-east-1.amazonaws.com/dev"

default_args = {
    'owner': 'alerta-utec',
    'depends_on_past': False,
    'start_date': datetime(2025, 11, 15),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'generar_reportes',
    default_args=default_args,
    description='Generación de reportes estadísticos periódicos',
    schedule_interval=timedelta(hours=6),  # Cada 6 horas
    catchup=False,
    tags=['reportes', 'analytics', 'estadisticas']
)

def recolectar_datos_incidentes(**context):
    """Recolecta todos los incidentes del período"""
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Incidentes')

    # Obtener todos los incidentes
    response = table.scan()
    incidentes = response.get('Items', [])

    # Periodo de análisis (últimas 24 horas)
    hace_24h = datetime.now() - timedelta(hours=24)

    incidentes_recientes = []
    for inc in incidentes:
        fecha_creacion = datetime.fromisoformat(inc['fechaCreacion'].replace('Z', '+00:00'))
        if fecha_creacion >= hace_24h:
            incidentes_recientes.append(inc)

    print(f"📊 Recolectados {len(incidentes_recientes)} incidentes de las últimas 24h")
    print(f"📊 Total histórico: {len(incidentes)} incidentes")

    context['ti'].xcom_push(key='incidentes_recientes', value=incidentes_recientes)
    context['ti'].xcom_push(key='incidentes_historico', value=incidentes)

    return {
        'recientes': len(incidentes_recientes),
        'historico': len(incidentes)
    }

def analizar_por_tipo(**context):
    """Analiza distribución de incidentes por tipo"""
    incidentes = context['ti'].xcom_pull(key='incidentes_recientes')

    tipos = [inc.get('tipo', 'Sin clasificar') for inc in incidentes]
    contador_tipos = Counter(tipos)

    analisis = {
        'total': len(incidentes),
        'por_tipo': dict(contador_tipos),
        'tipo_mas_comun': contador_tipos.most_common(1)[0] if contador_tipos else ('N/A', 0)
    }

    print("📊 ANÁLISIS POR TIPO:")
    for tipo, cantidad in contador_tipos.most_common():
        porcentaje = (cantidad / len(incidentes)) * 100 if incidentes else 0
        print(f"  {tipo}: {cantidad} ({porcentaje:.1f}%)")

    context['ti'].xcom_push(key='analisis_tipo', value=analisis)
    return analisis

def analizar_por_ubicacion(**context):
    """Analiza incidentes por ubicación (zonas críticas)"""
    incidentes = context['ti'].xcom_pull(key='incidentes_recientes')

    ubicaciones = [inc.get('ubicacion', 'Sin ubicación') for inc in incidentes]
    contador_ubicaciones = Counter(ubicaciones)

    # Top 5 zonas con más incidentes
    zonas_criticas = contador_ubicaciones.most_common(5)

    analisis = {
        'total_ubicaciones': len(set(ubicaciones)),
        'zonas_criticas': [
            {'ubicacion': ub, 'incidentes': cant}
            for ub, cant in zonas_criticas
        ]
    }

    print("📍 ZONAS CRÍTICAS (Top 5):")
    for ubicacion, cantidad in zonas_criticas:
        print(f"  {ubicacion}: {cantidad} incidentes")

    context['ti'].xcom_push(key='analisis_ubicacion', value=analisis)
    return analisis

def analizar_tiempos_resolucion(**context):
    """Analiza tiempos promedio de resolución"""
    incidentes = context['ti'].xcom_pull(key='incidentes_historico')

    tiempos_resolucion = []

    for inc in incidentes:
        if inc.get('estado') == 'resuelto':
            fecha_creacion = datetime.fromisoformat(inc['fechaCreacion'].replace('Z', '+00:00'))

            # Buscar en historial la fecha de resolución
            historial = inc.get('historial', [])
            for evento in historial:
                if 'resuelto' in evento.get('accion', '').lower():
                    fecha_resolucion = datetime.fromisoformat(evento['fecha'].replace('Z', '+00:00'))
                    tiempo_resolucion = (fecha_resolucion - fecha_creacion).total_seconds() / 60  # minutos
                    tiempos_resolucion.append({
                        'incidenteId': inc['incidenteId'],
                        'tipo': inc.get('tipo', 'N/A'),
                        'urgencia': inc.get('urgencia', 'N/A'),
                        'tiempo_minutos': tiempo_resolucion
                    })
                    break

    if tiempos_resolucion:
        tiempo_promedio = sum(t['tiempo_minutos'] for t in tiempos_resolucion) / len(tiempos_resolucion)
        tiempo_min = min(t['tiempo_minutos'] for t in tiempos_resolucion)
        tiempo_max = max(t['tiempo_minutos'] for t in tiempos_resolucion)
    else:
        tiempo_promedio = tiempo_min = tiempo_max = 0

    analisis = {
        'total_resueltos': len(tiempos_resolucion),
        'tiempo_promedio_min': round(tiempo_promedio, 2),
        'tiempo_minimo_min': round(tiempo_min, 2),
        'tiempo_maximo_min': round(tiempo_max, 2),
        'detalles': tiempos_resolucion[:10]  # Top 10
    }

    print(f"⏱️ TIEMPOS DE RESOLUCIÓN:")
    print(f"  Promedio: {tiempo_promedio:.1f} minutos")
    print(f"  Más rápido: {tiempo_min:.1f} minutos")
    print(f"  Más lento: {tiempo_max:.1f} minutos")

    context['ti'].xcom_push(key='analisis_tiempos', value=analisis)
    return analisis

def analizar_estados(**context):
    """Analiza distribución de estados actuales"""
    incidentes = context['ti'].xcom_pull(key='incidentes_recientes')

    estados = [inc.get('estado', 'sin_estado') for inc in incidentes]
    contador_estados = Counter(estados)

    analisis = {
        'por_estado': dict(contador_estados),
        'pendientes': contador_estados.get('pendiente', 0),
        'en_atencion': contador_estados.get('en_atencion', 0),
        'resueltos': contador_estados.get('resuelto', 0),
        'cancelados': contador_estados.get('cancelado', 0)
    }

    print("📈 DISTRIBUCIÓN DE ESTADOS:")
    for estado, cantidad in contador_estados.items():
        porcentaje = (cantidad / len(incidentes)) * 100 if incidentes else 0
        print(f"  {estado}: {cantidad} ({porcentaje:.1f}%)")

    # Calcular tasa de resolución
    total = len(incidentes)
    resueltos = analisis['resueltos']
    tasa_resolucion = (resueltos / total * 100) if total > 0 else 0
    analisis['tasa_resolucion'] = round(tasa_resolucion, 2)

    print(f"✅ Tasa de resolución: {tasa_resolucion:.1f}%")

    context['ti'].xcom_push(key='analisis_estados', value=analisis)
    return analisis

def detectar_tendencias(**context):
    """Detecta patrones y tendencias"""
    incidentes_historico = context['ti'].xcom_pull(key='incidentes_historico')

    # Agrupar por día de la semana y hora
    por_dia_semana = Counter()
    por_hora = Counter()

    for inc in incidentes_historico:
        fecha = datetime.fromisoformat(inc['fechaCreacion'].replace('Z', '+00:00'))
        dia_semana = fecha.strftime('%A')
        hora = fecha.hour

        por_dia_semana[dia_semana] += 1
        por_hora[hora] += 1

    dia_mas_incidentes = por_dia_semana.most_common(1)[0] if por_dia_semana else ('N/A', 0)
    hora_pico = por_hora.most_common(1)[0] if por_hora else (0, 0)

    tendencias = {
        'dia_mas_incidentes': {'dia': dia_mas_incidentes[0], 'cantidad': dia_mas_incidentes[1]},
        'hora_pico': {'hora': hora_pico[0], 'cantidad': hora_pico[1]},
        'distribucion_hora': dict(por_hora.most_common(5))
    }

    print(f"📊 TENDENCIAS:")
    print(f"  Día con más incidentes: {dia_mas_incidentes[0]} ({dia_mas_incidentes[1]})")
    print(f"  Hora pico: {hora_pico[0]}:00 ({hora_pico[1]} incidentes)")

    context['ti'].xcom_push(key='tendencias', value=tendencias)
    return tendencias

def generar_reporte_completo(**context):
    """Genera reporte completo consolidado"""
    # Recolectar todos los análisis
    analisis_tipo = context['ti'].xcom_pull(key='analisis_tipo')
    analisis_ubicacion = context['ti'].xcom_pull(key='analisis_ubicacion')
    analisis_tiempos = context['ti'].xcom_pull(key='analisis_tiempos')
    analisis_estados = context['ti'].xcom_pull(key='analisis_estados')
    tendencias = context['ti'].xcom_pull(key='tendencias')

    reporte = {
        'fecha_generacion': datetime.now().isoformat(),
        'periodo': 'últimas 24 horas',
        'resumen_ejecutivo': {
            'total_incidentes': analisis_tipo['total'],
            'tipo_mas_comun': analisis_tipo['tipo_mas_comun'][0],
            'zona_mas_critica': analisis_ubicacion['zonas_criticas'][0] if analisis_ubicacion['zonas_criticas'] else 'N/A',
            'tiempo_resolucion_promedio': analisis_tiempos['tiempo_promedio_min'],
            'tasa_resolucion': analisis_estados['tasa_resolucion']
        },
        'analisis_detallado': {
            'por_tipo': analisis_tipo,
            'por_ubicacion': analisis_ubicacion,
            'tiempos': analisis_tiempos,
            'estados': analisis_estados,
            'tendencias': tendencias
        }
    }

    print("\n" + "="*60)
    print("📊 REPORTE ESTADÍSTICO - ALERTA UTEC")
    print("="*60)
    print(json.dumps(reporte['resumen_ejecutivo'], indent=2))
    print("="*60 + "\n")

    # Guardar reporte en S3 (opcional)
    context['ti'].xcom_push(key='reporte_final', value=reporte)

    return reporte

def guardar_reporte_s3(**context):
    """Guarda el reporte en S3 para histórico"""
    reporte = context['ti'].xcom_pull(key='reporte_final')

    # Descomentar para guardar en S3
    # s3 = boto3.client('s3')
    # bucket = 'alerta-utec-reportes'
    # key = f"reportes/{datetime.now().strftime('%Y-%m-%d-%H%M')}.json"

    # s3.put_object(
    #     Bucket=bucket,
    #     Key=key,
    #     Body=json.dumps(reporte, indent=2),
    #     ContentType='application/json'
    # )

    print(f"📁 Reporte guardado en S3 (simulado)")
    return True

# Definir tareas
task_recolectar = PythonOperator(
    task_id='recolectar_datos',
    python_callable=recolectar_datos_incidentes,
    dag=dag
)

task_analizar_tipo = PythonOperator(
    task_id='analizar_tipo',
    python_callable=analizar_por_tipo,
    dag=dag
)

task_analizar_ubicacion = PythonOperator(
    task_id='analizar_ubicacion',
    python_callable=analizar_por_ubicacion,
    dag=dag
)

task_analizar_tiempos = PythonOperator(
    task_id='analizar_tiempos',
    python_callable=analizar_tiempos_resolucion,
    dag=dag
)

task_analizar_estados = PythonOperator(
    task_id='analizar_estados',
    python_callable=analizar_estados,
    dag=dag
)

task_tendencias = PythonOperator(
    task_id='detectar_tendencias',
    python_callable=detectar_tendencias,
    dag=dag
)

task_generar = PythonOperator(
    task_id='generar_reporte',
    python_callable=generar_reporte_completo,
    dag=dag
)

task_guardar = PythonOperator(
    task_id='guardar_s3',
    python_callable=guardar_reporte_s3,
    dag=dag
)

# Definir flujo
task_recolectar >> [task_analizar_tipo, task_analizar_ubicacion, task_analizar_tiempos, task_analizar_estados, task_tendencias] >> task_generar >> task_guardar
