"""
DAG de Clasificación Automática de Incidentes
Clasifica incidentes por tipo, urgencia y asigna áreas responsables
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.http.sensors.http import HttpSensor
import json
import boto3

# Configuración
API_BASE_URL = "https://if1stu7r2g.execute-api.us-east-1.amazonaws.com/dev"

default_args = {
    'owner': 'alerta-utec',
    'depends_on_past': False,
    'start_date': datetime(2025, 11, 15),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}

dag = DAG(
    'clasificar_incidentes',
    default_args=default_args,
    description='Clasificación automática de incidentes pendientes',
    schedule_interval=timedelta(minutes=5),  # Cada 5 minutos
    catchup=False,
    tags=['incidentes', 'clasificacion', 'automatizacion']
)

def obtener_incidentes_pendientes(**context):
    """Obtiene incidentes con estado pendiente desde DynamoDB"""
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Incidentes')

    response = table.scan(
        FilterExpression='estado = :estado',
        ExpressionAttributeValues={':estado': 'pendiente'}
    )

    incidentes = response.get('Items', [])
    print(f"📋 Encontrados {len(incidentes)} incidentes pendientes")

    # Guardar en XCom para siguiente tarea
    context['ti'].xcom_push(key='incidentes_pendientes', value=incidentes)
    return len(incidentes)

def clasificar_por_urgencia(**context):
    """Clasifica incidentes por nivel de urgencia"""
    incidentes = context['ti'].xcom_pull(key='incidentes_pendientes')

    clasificacion = {
        'alta': [],
        'media': [],
        'baja': []
    }

    for inc in incidentes:
        urgencia = inc.get('urgencia', 'media')
        clasificacion[urgencia].append(inc)

    print(f"🔴 Alta urgencia: {len(clasificacion['alta'])}")
    print(f"🟡 Media urgencia: {len(clasificacion['media'])}")
    print(f"🟢 Baja urgencia: {len(clasificacion['baja'])}")

    context['ti'].xcom_push(key='clasificacion', value=clasificacion)
    return clasificacion

def asignar_area_responsable(**context):
    """Asigna área responsable según tipo de incidente"""
    clasificacion = context['ti'].xcom_pull(key='clasificacion')

    # Mapeo de tipos a áreas responsables
    areas_responsables = {
        'Seguridad': 'seguridad@utec.edu.pe',
        'Infraestructura': 'infraestructura@utec.edu.pe',
        'Limpieza': 'servicios@utec.edu.pe',
        'Tecnología': 'ti@utec.edu.pe',
        'Académico': 'academico@utec.edu.pe',
        'default': 'soporte@utec.edu.pe'
    }

    asignaciones = []

    # Procesar primero los de alta urgencia
    for inc in clasificacion.get('alta', []):
        tipo = inc.get('tipo', 'default')
        area = areas_responsables.get(tipo, areas_responsables['default'])

        asignaciones.append({
            'incidenteId': inc['incidenteId'],
            'tipo': tipo,
            'urgencia': 'alta',
            'area_responsable': area,
            'prioridad': 1
        })

    # Luego media y baja urgencia
    for urgencia in ['media', 'baja']:
        for inc in clasificacion.get(urgencia, []):
            tipo = inc.get('tipo', 'default')
            area = areas_responsables.get(tipo, areas_responsables['default'])

            asignaciones.append({
                'incidenteId': inc['incidenteId'],
                'tipo': tipo,
                'urgencia': urgencia,
                'area_responsable': area,
                'prioridad': 2 if urgencia == 'media' else 3
            })

    print(f"✅ Asignadas {len(asignaciones)} incidentes a áreas responsables")
    context['ti'].xcom_push(key='asignaciones', value=asignaciones)
    return asignaciones

def actualizar_estado_en_atencion(**context):
    """Actualiza el estado de incidentes clasificados a 'en_atencion'"""
    import requests

    asignaciones = context['ti'].xcom_pull(key='asignaciones')
    actualizados = 0

    for asignacion in asignaciones:
        try:
            # Actualizar estado del incidente
            response = requests.patch(
                f"{API_BASE_URL}/incidentes/{asignacion['incidenteId']}/estado",
                json={'nuevoEstado': 'en_atencion'},
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                actualizados += 1
                print(f"✅ Incidente {asignacion['incidenteId']} → en_atencion")
            else:
                print(f"❌ Error actualizando {asignacion['incidenteId']}: {response.text}")

        except Exception as e:
            print(f"❌ Error: {str(e)}")

    print(f"📊 Total actualizados: {actualizados}/{len(asignaciones)}")
    return actualizados

def generar_reporte_clasificacion(**context):
    """Genera un reporte resumen de la clasificación"""
    clasificacion = context['ti'].xcom_pull(key='clasificacion')
    asignaciones = context['ti'].xcom_pull(key='asignaciones')

    reporte = {
        'fecha': datetime.now().isoformat(),
        'total_procesados': len(asignaciones),
        'por_urgencia': {
            'alta': len(clasificacion.get('alta', [])),
            'media': len(clasificacion.get('media', [])),
            'baja': len(clasificacion.get('baja', []))
        },
        'por_area': {}
    }

    # Contar por área
    for asig in asignaciones:
        area = asig['area_responsable']
        reporte['por_area'][area] = reporte['por_area'].get(area, 0) + 1

    print("📊 REPORTE DE CLASIFICACIÓN")
    print(json.dumps(reporte, indent=2))

    # Guardar en S3 o DynamoDB si es necesario
    return reporte

# Definir tareas
task_obtener = PythonOperator(
    task_id='obtener_incidentes_pendientes',
    python_callable=obtener_incidentes_pendientes,
    dag=dag
)

task_clasificar = PythonOperator(
    task_id='clasificar_por_urgencia',
    python_callable=clasificar_por_urgencia,
    dag=dag
)

task_asignar = PythonOperator(
    task_id='asignar_area_responsable',
    python_callable=asignar_area_responsable,
    dag=dag
)

task_actualizar = PythonOperator(
    task_id='actualizar_estado',
    python_callable=actualizar_estado_en_atencion,
    dag=dag
)

task_reporte = PythonOperator(
    task_id='generar_reporte',
    python_callable=generar_reporte_clasificacion,
    dag=dag
)

# Definir flujo
task_obtener >> task_clasificar >> task_asignar >> task_actualizar >> task_reporte
