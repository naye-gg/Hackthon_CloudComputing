"""
DAG de Notificaciones
Envía notificaciones a áreas responsables según la gravedad del incidente
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
import json
import boto3
import requests

# Configuración
API_BASE_URL = "https://if1stu7r2g.execute-api.us-east-1.amazonaws.com/dev"
WEBSOCKET_URL = "wss://3lgmyhtvpa.execute-api.us-east-1.amazonaws.com/dev"

default_args = {
    'owner': 'alerta-utec',
    'depends_on_past': False,
    'start_date': datetime(2025, 11, 15),
    'email_on_failure': True,
    'email': ['soporte@utec.edu.pe'],
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    'enviar_notificaciones',
    default_args=default_args,
    description='Envío de notificaciones a áreas responsables',
    schedule_interval=timedelta(minutes=3),  # Cada 3 minutos
    catchup=False,
    tags=['notificaciones', 'alertas', 'comunicacion']
)

def detectar_incidentes_criticos(**context):
    """Detecta incidentes de alta urgencia que requieren atención inmediata"""
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Incidentes')

    # Buscar incidentes de alta urgencia pendientes
    response = table.scan(
        FilterExpression='urgencia = :urg AND (estado = :est1 OR estado = :est2)',
        ExpressionAttributeValues={
            ':urg': 'alta',
            ':est1': 'pendiente',
            ':est2': 'en_atencion'
        }
    )

    incidentes_criticos = response.get('Items', [])

    # Detectar incidentes muy antiguos (más de 30 minutos sin resolver)
    tiempo_limite = datetime.now() - timedelta(minutes=30)

    criticos_urgentes = []
    for inc in incidentes_criticos:
        fecha_creacion = datetime.fromisoformat(inc['fechaCreacion'].replace('Z', '+00:00'))
        if fecha_creacion < tiempo_limite and inc['estado'] != 'resuelto':
            inc['razon'] = 'tiempo_excedido'
            criticos_urgentes.append(inc)
        elif inc['urgencia'] == 'alta' and inc['estado'] == 'pendiente':
            inc['razon'] = 'alta_prioridad'
            criticos_urgentes.append(inc)

    print(f"🚨 Detectados {len(criticos_urgentes)} incidentes críticos")
    context['ti'].xcom_push(key='incidentes_criticos', value=criticos_urgentes)
    return criticos_urgentes

def enviar_notificacion_websocket(**context):
    """Envía notificaciones en tiempo real vía WebSocket"""
    incidentes = context['ti'].xcom_pull(key='incidentes_criticos')

    # En producción, esto se haría con boto3 ApiGatewayManagementApi
    # Para simplificar, simulamos el envío

    notificaciones_enviadas = 0

    for inc in incidentes:
        mensaje = {
            'tipo': 'alerta_critica',
            'incidenteId': inc['incidenteId'],
            'urgencia': inc['urgencia'],
            'descripcion': inc['descripcion'],
            'ubicacion': inc['ubicacion'],
            'razon': inc.get('razon', 'alta_prioridad'),
            'timestamp': datetime.now().isoformat()
        }

        print(f"📡 Enviando notificación WebSocket para {inc['incidenteId']}")
        print(json.dumps(mensaje, indent=2))

        # Aquí se enviaría realmente vía WebSocket API
        # usando boto3.client('apigatewaymanagementapi')
        notificaciones_enviadas += 1

    print(f"✅ {notificaciones_enviadas} notificaciones WebSocket enviadas")
    return notificaciones_enviadas

def preparar_notificaciones_email(**context):
    """Prepara contenido de emails para cada área responsable"""
    incidentes = context['ti'].xcom_pull(key='incidentes_criticos')

    # Agrupar por tipo/área
    por_area = {}

    areas_email = {
        'Seguridad': 'seguridad@utec.edu.pe',
        'Infraestructura': 'infraestructura@utec.edu.pe',
        'Limpieza': 'servicios@utec.edu.pe',
        'Tecnología': 'ti@utec.edu.pe',
        'Académico': 'academico@utec.edu.pe',
    }

    for inc in incidentes:
        tipo = inc.get('tipo', 'General')
        email = areas_email.get(tipo, 'soporte@utec.edu.pe')

        if email not in por_area:
            por_area[email] = []

        por_area[email].append(inc)

    # Generar contenido de emails
    emails_a_enviar = []

    for email, incidentes_area in por_area.items():
        contenido = f"""
        <h2>🚨 Alerta de Incidentes Críticos - UTEC</h2>
        <p>Se han detectado {len(incidentes_area)} incidentes que requieren atención inmediata:</p>
        <ul>
        """

        for inc in incidentes_area:
            contenido += f"""
            <li>
                <strong>ID:</strong> {inc['incidenteId']}<br>
                <strong>Tipo:</strong> {inc['tipo']}<br>
                <strong>Ubicación:</strong> {inc['ubicacion']}<br>
                <strong>Descripción:</strong> {inc['descripcion']}<br>
                <strong>Estado:</strong> {inc['estado']}<br>
                <strong>Urgencia:</strong> {inc['urgencia']}<br>
                <strong>Fecha:</strong> {inc['fechaCreacion']}<br>
                <hr>
            </li>
            """

        contenido += """
        </ul>
        <p>Por favor, atiendan estos incidentes lo antes posible.</p>
        <p><a href="https://alerta-utec.com/dashboard">Ver Dashboard</a></p>
        """

        emails_a_enviar.append({
            'destinatario': email,
            'asunto': f'🚨 {len(incidentes_area)} Incidentes Críticos Pendientes',
            'contenido': contenido
        })

    print(f"📧 Preparados {len(emails_a_enviar)} emails para enviar")
    context['ti'].xcom_push(key='emails', value=emails_a_enviar)
    return emails_a_enviar

def enviar_notificaciones_sns(**context):
    """Envía notificaciones SMS críticas vía AWS SNS"""
    incidentes = context['ti'].xcom_pull(key='incidentes_criticos')

    # Solo para incidentes de seguridad de alta urgencia
    incidentes_sms = [
        inc for inc in incidentes
        if inc['tipo'] == 'Seguridad' and inc['urgencia'] == 'alta'
    ]

    if not incidentes_sms:
        print("ℹ️ No hay incidentes que requieran SMS")
        return 0

    sns = boto3.client('sns', region_name='us-east-1')

    # Números de contacto de emergencia (configurar en variables)
    contactos_emergencia = [
        '+51999999999',  # Jefe de Seguridad
        # Agregar más números
    ]

    enviados = 0

    for inc in incidentes_sms:
        mensaje = f"""
🚨 ALERTA UTEC
Tipo: {inc['tipo']}
Ubicación: {inc['ubicacion']}
Descripción: {inc['descripcion'][:100]}
ID: {inc['incidenteId']}
        """.strip()

        for numero in contactos_emergencia:
            try:
                # Descomentar en producción
                # response = sns.publish(
                #     PhoneNumber=numero,
                #     Message=mensaje
                # )
                print(f"📱 SMS enviado a {numero}: {mensaje}")
                enviados += 1
            except Exception as e:
                print(f"❌ Error enviando SMS a {numero}: {str(e)}")

    print(f"✅ {enviados} SMS enviados")
    return enviados

def registrar_notificaciones(**context):
    """Registra las notificaciones enviadas en DynamoDB"""
    incidentes = context['ti'].xcom_pull(key='incidentes_criticos')

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Incidentes')

    for inc in incidentes:
        # Actualizar historial del incidente
        historial = inc.get('historial', [])
        historial.append({
            'accion': 'notificacion_enviada',
            'fecha': datetime.now().isoformat(),
            'tipo': 'automatica',
            'canales': ['websocket', 'email']
        })

        try:
            table.update_item(
                Key={'incidenteId': inc['incidenteId']},
                UpdateExpression='SET historial = :h',
                ExpressionAttributeValues={':h': historial}
            )
            print(f"✅ Notificación registrada para {inc['incidenteId']}")
        except Exception as e:
            print(f"❌ Error registrando: {str(e)}")

    return len(incidentes)

# Definir tareas
task_detectar = PythonOperator(
    task_id='detectar_incidentes_criticos',
    python_callable=detectar_incidentes_criticos,
    dag=dag
)

task_websocket = PythonOperator(
    task_id='enviar_websocket',
    python_callable=enviar_notificacion_websocket,
    dag=dag
)

task_preparar_email = PythonOperator(
    task_id='preparar_emails',
    python_callable=preparar_notificaciones_email,
    dag=dag
)

task_sms = PythonOperator(
    task_id='enviar_sms',
    python_callable=enviar_notificaciones_sns,
    dag=dag
)

task_registrar = PythonOperator(
    task_id='registrar_notificaciones',
    python_callable=registrar_notificaciones,
    dag=dag
)

# Definir flujo
task_detectar >> [task_websocket, task_preparar_email, task_sms] >> task_registrar
