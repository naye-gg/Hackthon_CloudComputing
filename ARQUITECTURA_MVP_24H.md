# Arquitectura AlertaUTEC - MVP en 24 Horas
## Plataforma Serverless para Gestión de Incidentes (AWS Academy Lab)

> **CONTEXTO**: Hackathon de 24 horas con AWS Academy Lab (servicios limitados)

---

## 1. Resumen Ejecutivo

Arquitectura **serverless simplificada y realista** para desarrollar en 24 horas usando únicamente servicios disponibles en AWS Lab. Prioriza funcionalidad core sobre features avanzadas.

### ✅ Lo que SÍ tiene el MVP:
- **CRUD completo de incidentes** (crear, listar, actualizar, eliminar)
- **Upload de fotos** con presigned URLs de S3
- **"Tiempo real"** con polling cada 5 segundos
- **Roles básicos** (estudiante/autoridad) sin Cognito
- **Panel administrativo** para gestionar incidentes
- **100% Serverless**: Lambda + API Gateway + DynamoDB + S3
- **Costo: $0** (dentro de Free Tier)

### 🛣️ Lo que va en Roadmap (Fase 2):
- Amazon Cognito para autenticación robusta
- WebSockets para tiempo real sub-segundo
- Apache Airflow para orquestación
- SageMaker para análisis predictivo
- SNS/SES para notificaciones

---

## 2. Arquitectura del MVP

### Stack Tecnológico

```
┌─────────────┐
│  Usuarios   │ (Estudiantes, Personal, Autoridades)
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────────────────┐
│  Amazon S3 (Frontend)   │ Static Website Hosting
│  HTML/CSS/JS o React    │
└──────────┬──────────────┘
           │ fetch API
           ▼
┌──────────────────────────┐
│  API Gateway REST API    │
│  /incidents (CRUD)       │
└──────────┬───────────────┘
           │ invoke
           ▼
┌──────────────────────────┐
│  AWS Lambda Functions    │
│  - incident-handler      │
└──────┬───────────────────┘
       │
       ├──► DynamoDB (alertautec-incidents)
       │    └─ Tabla única con todos los incidentes
       │
       └──► S3 (alertautec-photos)
            └─ Fotos de incidentes
```

### 2.1 Frontend - S3 Static Website

**Servicio**: Amazon S3 Static Website Hosting

**Tecnología**: 
- Opción 1 (rápido): HTML/CSS/JavaScript vanilla + Bootstrap
- Opción 2 (si el equipo domina): React (Create React App)

**Estructura**:
```
frontend/
├── index.html          # Página principal (lista incidentes)
├── crear.html          # Formulario crear incidente
├── detalle.html        # Ver detalle
├── styles.css          # Estilos
└── app.js              # Lógica (fetch, polling)
```

**Features**:
- ✅ Formulario crear incidente
- ✅ Lista de incidentes con filtros
- ✅ Botones para cambiar estado (autoridad)
- ✅ Upload de fotos
- ✅ Polling automático cada 5 segundos
- ✅ Responsive (Bootstrap/Tailwind)

**Configuración S3**:
```bash
# Bucket público con Static Website Hosting
# Index document: index.html
# CORS habilitado para API Gateway
```

### 2.2 Autenticación Simplificada (Sin Cognito)

**⚠️ Problema**: Cognito no disponible en AWS Lab

**✅ Solución MVP**: Autenticación simple por rol

**Implementación**:

**Opción 1 - Selector de rol (más simple)**:
```html
<!-- Login básico en frontend -->
<select id="rol">
  <option value="estudiante">Estudiante</option>
  <option value="autoridad">Autoridad</option>
</select>
<input id="nombre" placeholder="Tu nombre">
<button onclick="login()">Entrar</button>
```

```javascript
// Guardar en localStorage
function login() {
  localStorage.setItem('rol', document.getElementById('rol').value);
  localStorage.setItem('nombre', document.getElementById('nombre').value);
  location.href = 'index.html';
}

// Enviar en headers de cada request
fetch('/incidents', {
  headers: {
    'x-user-role': localStorage.getItem('rol'),
    'x-user-name': localStorage.getItem('nombre')
  }
})
```

**Lambda valida rol**:
```python
def lambda_handler(event, context):
    role = event['headers'].get('x-user-role', 'estudiante')
    
    # Solo autoridades pueden actualizar
    if event['httpMethod'] == 'PUT' and role != 'autoridad':
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'No autorizado'})
        }
    # ...resto de lógica
```

**Opción 2 - API Keys (más seguro)**:
```javascript
// Headers con API key
const API_KEYS = {
  'estudiante': 'student-key-12345',
  'autoridad': 'admin-key-67890'
};

fetch('/incidents', {
  headers: {
    'x-api-key': API_KEYS[rol]
  }
})
```

**📌 Nota para presentación**: "En producción usaríamos Amazon Cognito para autenticación robusta con MFA"

### 2.3 API REST - API Gateway

**Servicio**: Amazon API Gateway (REST API)

**Endpoints**:
```
POST   /incidents          - Crear incidente
GET    /incidents          - Listar todos
GET    /incidents/{id}     - Ver detalle
PUT    /incidents/{id}     - Actualizar estado
DELETE /incidents/{id}     - Eliminar (opcional)
POST   /presigned-url      - Generar URL para upload
```

**Configuración importante**:
- ✅ **CORS habilitado** (crucial para frontend)
- ✅ Integración Lambda Proxy
- ✅ Deploy en stage `prod`
- ✅ Sin API Key requirement (para simplificar)

**Ejemplo de configuración CORS**:
```yaml
Access-Control-Allow-Origin: '*'
Access-Control-Allow-Methods: 'GET,POST,PUT,DELETE,OPTIONS'
Access-Control-Allow-Headers: 'Content-Type,x-user-role,x-user-name'
```

### 2.4 Backend - AWS Lambda

**Función principal**: `incident-handler`

**Runtime**: Python 3.11 o Node.js 18
- **Python**: Mejor para lógica compleja, boto3 robusto
- **Node.js**: Más rápido para APIs simples

**Código Python (ejemplo simplificado)**:
```python
import json
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('alertautec-incidents')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    method = event['httpMethod']
    path = event['path']
    
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
    }
    
    try:
        if method == 'POST' and path == '/incidents':
            return create_incident(event, headers)
        elif method == 'GET' and path == '/incidents':
            return list_incidents(headers)
        elif method == 'GET' and path.startswith('/incidents/'):
            incident_id = path.split('/')[-1]
            return get_incident(incident_id, headers)
        elif method == 'PUT' and path.startswith('/incidents/'):
            incident_id = path.split('/')[-1]
            return update_incident(incident_id, event, headers)
        elif method == 'POST' and path == '/presigned-url':
            return generate_presigned_url(event, headers)
        else:
            return {'statusCode': 404, 'headers': headers, 'body': json.dumps({'error': 'Not found'})}
    except Exception as e:
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'error': str(e)})}

def create_incident(event, headers):
    body = json.loads(event['body'])
    
    incident_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    item = {
        'incidentId': incident_id,
        'tipo': body.get('tipo', 'otro'),
        'ubicacion': body.get('ubicacion', ''),
        'descripcion': body.get('descripcion', ''),
        'urgencia': body.get('urgencia', 'baja'),
        'estado': 'pendiente',
        'reportadoPor': body.get('reportadoPor', 'Anónimo'),
        'rolReportador': event['headers'].get('x-user-role', 'estudiante'),
        'fotoUrl': body.get('fotoUrl', ''),
        'createdAt': timestamp,
        'updatedAt': timestamp,
        'responsable': ''
    }
    
    table.put_item(Item=item)
    
    return {
        'statusCode': 201,
        'headers': headers,
        'body': json.dumps(item)
    }

def list_incidents(headers):
    response = table.scan()
    items = response.get('Items', [])
    
    # Ordenar por fecha (más reciente primero)
    items.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(items, default=str)
    }

def get_incident(incident_id, headers):
    response = table.get_item(Key={'incidentId': incident_id})
    item = response.get('Item')
    
    if not item:
        return {'statusCode': 404, 'headers': headers, 'body': json.dumps({'error': 'Not found'})}
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(item, default=str)
    }

def update_incident(incident_id, event, headers):
    body = json.loads(event['body'])
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Validar rol
    role = event['headers'].get('x-user-role', 'estudiante')
    if role != 'autoridad':
        return {'statusCode': 403, 'headers': headers, 'body': json.dumps({'error': 'No autorizado'})}
    
    update_expr = 'SET updatedAt = :ts'
    expr_values = {':ts': timestamp}
    
    if 'estado' in body:
        update_expr += ', estado = :estado'
        expr_values[':estado'] = body['estado']
    
    if 'responsable' in body:
        update_expr += ', responsable = :resp'
        expr_values[':resp'] = body['responsable']
    
    response = table.update_item(
        Key={'incidentId': incident_id},
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_values,
        ReturnValues='ALL_NEW'
    )
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(response['Attributes'], default=str)
    }

def generate_presigned_url(event, headers):
    body = json.loads(event['body'])
    filename = body.get('filename', 'foto.jpg')
    
    # Generar nombre único
    unique_filename = f"{uuid.uuid4()}-{filename}"
    
    # Presigned URL válida por 10 minutos
    url = s3.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': 'alertautec-photos',
            'Key': unique_filename,
            'ContentType': 'image/jpeg'
        },
        ExpiresIn=600
    )
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'uploadUrl': url,
            'photoUrl': f"https://alertautec-photos.s3.amazonaws.com/{unique_filename}"
        })
    }
```

**Configuración Lambda**:
- Timeout: 30 segundos
- Memory: 512 MB (suficiente)
- Environment variables: `DYNAMODB_TABLE=alertautec-incidents`, `S3_BUCKET=alertautec-photos`

**IAM Role (permisos necesarios)**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
        "dynamodb:Scan",
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/alertautec-incidents"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::alertautec-photos/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

### 2.5 Base de Datos - DynamoDB

**Tabla única**: `alertautec-incidents`

**Diseño**:
```
Partition Key: incidentId (String)
```

**Atributos**:
```json
{
  "incidentId": "uuid-v4",
  "tipo": "infraestructura|servicio|emergencia|otro",
  "ubicacion": "Edificio A, Piso 3",
  "descripcion": "Texto libre del problema",
  "urgencia": "baja|media|alta|crítica",
  "estado": "pendiente|en_atencion|resuelto",
  "reportadoPor": "Juan Pérez",
  "rolReportador": "estudiante|personal|autoridad",
  "fotoUrl": "https://s3.../foto.jpg" (opcional),
  "createdAt": "2025-11-15T10:30:00Z",
  "updatedAt": "2025-11-15T11:00:00Z",
  "responsable": "Dra. María López" (opcional)
}
```

**Configuración**:
- Capacity mode: **On-demand** (sin planificación de capacidad)
- Sin GSI inicialmente (agregar después si hay tiempo)
- Scan para listar todos (suficiente para <1000 items en demo)

**Mejora futura (si hay tiempo)**:
- GSI por estado: `statusIndex` (PK: estado, SK: createdAt)
- GSI por urgencia: `urgencyIndex` (PK: urgencia, SK: createdAt)

### 2.6 Almacenamiento - Amazon S3

**Bucket 1**: `alertautec-frontend`
- **Propósito**: Hospedar frontend estático
- **Configuración**:
  - Static Website Hosting: Enabled
  - Index document: `index.html`
  - Permissions: Public read
  - Bucket policy:
    ```json
    {
      "Version": "2012-10-17",
      "Statement": [{
        "Sid": "PublicReadGetObject",
        "Effect": "Allow",
        "Principal": "*",
        "Action": "s3:GetObject",
        "Resource": "arn:aws:s3:::alertautec-frontend/*"
      }]
    }
    ```

**Bucket 2**: `alertautec-photos`
- **Propósito**: Almacenar fotos de incidentes
- **Configuración**:
  - Static Website Hosting: Disabled
  - Permissions: Private (acceso vía presigned URLs)
  - CORS configurado:
    ```json
    [
      {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["PUT", "GET"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": []
      }
    ]
    ```

### 2.7 "Tiempo Real" con Polling

**Sin WebSockets** (requiere setup complejo)

**Solución simple**:
```javascript
// Frontend: app.js
let previousIncidents = [];

function pollIncidents() {
  fetch('https://api-url.com/incidents', {
    headers: {
      'x-user-role': localStorage.getItem('rol'),
      'x-user-name': localStorage.getItem('nombre')
    }
  })
  .then(res => res.json())
  .then(incidents => {
    updateUI(incidents);
    highlightChanges(previousIncidents, incidents);
    previousIncidents = incidents;
  })
  .catch(err => console.error('Error:', err));
}

// Polling cada 5 segundos
setInterval(pollIncidents, 5000);

// Cargar inmediatamente al inicio
pollIncidents();

function highlightChanges(old, current) {
  // Detectar nuevos incidentes
  const oldIds = new Set(old.map(i => i.incidentId));
  current.forEach(incident => {
    if (!oldIds.has(incident.incidentId)) {
      // Nuevo incidente - mostrar notificación
      showToast(`Nuevo incidente: ${incident.tipo} en ${incident.ubicacion}`);
      // Agregar clase CSS de highlight
      document.getElementById(incident.incidentId)?.classList.add('new-item');
    }
  });
}
```

**Experiencia de usuario**: 
- ✅ Actualizaciones automáticas cada 5 segundos
- ✅ Notificaciones toast cuando hay cambios
- ✅ Highlight visual de items nuevos/actualizados
- ⚠️ 5 segundos de delay (aceptable para MVP)

---

## 3. Plan de Implementación (24 horas)

### Distribución Recomendada

#### **Horas 0-2: Setup Infraestructura** 🛠️

**Persona 1+2 (juntos)**:
- [ ] Crear bucket `alertautec-frontend` con Static Website
- [ ] Crear tabla DynamoDB `alertautec-incidents`
- [ ] Crear bucket `alertautec-photos` con CORS
- [ ] Crear función Lambda `incident-handler`
- [ ] Crear API Gateway REST API
- [ ] Configurar IAM role de Lambda
- [ ] Testing básico: curl/Postman

**Output**: Infraestructura lista

#### **Horas 2-6: Backend CRUD** ⚙️

**Persona 1 (Backend Lead)**:
- [ ] Implementar POST /incidents
- [ ] Implementar GET /incidents (scan)
- [ ] Implementar GET /incidents/{id}
- [ ] Implementar PUT /incidents/{id}
- [ ] Testing con Postman

**Output**: API funcionando

#### **Horas 6-8: Upload Fotos** 🖼️

**Persona 1**:
- [ ] Endpoint POST /presigned-url
- [ ] Generar presigned URL
- [ ] Testing upload con Postman/curl
- [ ] Guardar URL en DynamoDB

**Output**: Upload funcionando

#### **Horas 8-10: Break ☕**
- Descanso
- Testing manual
- Fix bugs

#### **Horas 10-16: Frontend** 🎨

**Persona 2 (Frontend Lead)**:
- [ ] HTML base (index.html, crear.html)
- [ ] CSS con Bootstrap/Tailwind
- [ ] Formulario crear incidente
- [ ] Conectar con API (POST /incidents)
- [ ] Lista de incidentes (GET /incidents)
- [ ] Vista detalle
- [ ] Botones actualizar estado (solo autoridad)
- [ ] Implementar polling
- [ ] Upload foto desde frontend
- [ ] Responsive design

**Persona 3**:
- [ ] Selector de rol (login.html)
- [ ] Filtros de lista (por estado, urgencia)
- [ ] Estadísticas simples (contadores)
- [ ] Notificaciones toast
- [ ] Manejo de errores

**Output**: Frontend completo

#### **Horas 16-18: Integración** 🧪

**Todos**:
- [ ] Testing end-to-end
- [ ] Fix bugs
- [ ] CORS issues
- [ ] Validaciones
- [ ] Loading states

**Output**: App funcionando completa

#### **Horas 18-20: Polish** ✨

**Persona 2+3**:
- [ ] Estilos mejorados
- [ ] Animaciones CSS
- [ ] Gráficos Chart.js (opcional)
- [ ] UX improvements

**Output**: UI pulida

#### **Horas 20-22: Documentación** 📝

**Persona 4 (DevOps/Docs)**:
- [ ] README.md completo
- [ ] Diagrama en Eraser.io
- [ ] Screenshots
- [ ] Video demo (2-3 min)

**Output**: Docs listos

#### **Horas 22-24: Deploy Final** 🚀

**Todos**:
- [ ] Testing multi-browser
- [ ] Fix bugs finales
- [ ] Subir frontend a S3
- [ ] Push a GitHub
- [ ] Ensayar presentación

**Output**: ✅ **MVP COMPLETO**

### Roles del Equipo (4 personas)

| Rol | Responsabilidad | Horas Clave |
|-----|-----------------|-------------|
| **Backend Lead** | Lambda, API Gateway, DynamoDB | 2-8 |
| **Frontend Lead** | HTML/CSS/JS, UI/UX | 10-18 |
| **Full-Stack** | Ayuda backend y frontend, testing | 2-18 |
| **DevOps/Docs** | Setup AWS, monitoreo, docs, diagrama | 0-2, 20-24 |

---

## 4. Código Frontend Ejemplo

### index.html (Lista de incidentes)
```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AlertaUTEC - Incidentes</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <nav class="navbar navbar-dark bg-primary">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1">🚨 AlertaUTEC</span>
            <div>
                <span id="user-info" class="text-white me-3"></span>
                <a href="crear.html" class="btn btn-light">+ Nuevo Incidente</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-md-3">
                <h5>Filtros</h5>
                <select id="filter-estado" class="form-select mb-2">
                    <option value="">Todos los estados</option>
                    <option value="pendiente">Pendiente</option>
                    <option value="en_atencion">En atención</option>
                    <option value="resuelto">Resuelto</option>
                </select>
                <select id="filter-urgencia" class="form-select mb-2">
                    <option value="">Todas las urgencias</option>
                    <option value="baja">Baja</option>
                    <option value="media">Media</option>
                    <option value="alta">Alta</option>
                    <option value="crítica">Crítica</option>
                </select>
                <button onclick="applyFilters()" class="btn btn-primary w-100">Aplicar</button>
            </div>
            <div class="col-md-9">
                <div class="d-flex justify-content-between mb-3">
                    <h3>Incidentes</h3>
                    <div>
                        <span class="badge bg-warning">Pendientes: <span id="count-pendiente">0</span></span>
                        <span class="badge bg-info">En atención: <span id="count-atencion">0</span></span>
                        <span class="badge bg-success">Resueltos: <span id="count-resuelto">0</span></span>
                    </div>
                </div>
                <div id="incidents-list" class="row">
                    <!-- Incidentes se cargan dinámicamente -->
                </div>
            </div>
        </div>
    </div>

    <!-- Toast para notificaciones -->
    <div class="toast-container position-fixed bottom-0 end-0 p-3">
        <div id="toast" class="toast" role="alert">
            <div class="toast-header">
                <strong class="me-auto">AlertaUTEC</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body"></div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="app.js"></script>
    <script>
        // Verificar login
        if (!localStorage.getItem('rol')) {
            window.location.href = 'login.html';
        }

        // Mostrar info usuario
        document.getElementById('user-info').textContent = 
            `${localStorage.getItem('nombre')} (${localStorage.getItem('rol')})`;

        // Iniciar polling
        loadIncidents();
        setInterval(loadIncidents, 5000);
    </script>
</body>
</html>
```

### app.js (Lógica principal)
```javascript
const API_URL = 'https://tu-api-id.execute-api.us-east-1.amazonaws.com/prod';
let allIncidents = [];
let previousIncidents = [];

async function loadIncidents() {
    try {
        const response = await fetch(`${API_URL}/incidents`, {
            headers: {
                'x-user-role': localStorage.getItem('rol') || 'estudiante',
                'x-user-name': localStorage.getItem('nombre') || 'Anónimo'
            }
        });
        
        const incidents = await response.json();
        allIncidents = incidents;
        
        // Detectar cambios
        if (previousIncidents.length > 0) {
            const newIncidents = incidents.filter(i => 
                !previousIncidents.find(p => p.incidentId === i.incidentId)
            );
            newIncidents.forEach(incident => {
                showToast(`Nuevo: ${incident.tipo} en ${incident.ubicacion}`);
            });
        }
        
        previousIncidents = [...incidents];
        renderIncidents(incidents);
        updateStats(incidents);
    } catch (error) {
        console.error('Error loading incidents:', error);
    }
}

function renderIncidents(incidents) {
    const container = document.getElementById('incidents-list');
    
    if (incidents.length === 0) {
        container.innerHTML = '<p class="text-muted">No hay incidentes</p>';
        return;
    }
    
    container.innerHTML = incidents.map(incident => `
        <div class="col-md-6 mb-3" id="${incident.incidentId}">
            <div class="card ${getCardClass(incident.urgencia)}">
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <h5 class="card-title">${incident.tipo}</h5>
                        <span class="badge ${getStatusBadge(incident.estado)}">${incident.estado}</span>
                    </div>
                    <p class="card-text">${incident.descripcion.substring(0, 100)}...</p>
                    <p class="small text-muted">
                        📍 ${incident.ubicacion}<br>
                        🚨 ${incident.urgencia} | 
                        👤 ${incident.reportadoPor} |
                        🕒 ${formatDate(incident.createdAt)}
                    </p>
                    ${incident.fotoUrl ? `<img src="${incident.fotoUrl}" class="img-fluid mb-2" style="max-height:150px">` : ''}
                    <div class="d-flex gap-2">
                        <a href="detalle.html?id=${incident.incidentId}" class="btn btn-sm btn-outline-primary">Ver detalle</a>
                        ${localStorage.getItem('rol') === 'autoridad' ? `
                            <button onclick="updateStatus('${incident.incidentId}', 'en_atencion')" class="btn btn-sm btn-warning">Atender</button>
                            <button onclick="updateStatus('${incident.incidentId}', 'resuelto')" class="btn btn-sm btn-success">Resolver</button>
                        ` : ''}
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function updateStats(incidents) {
    const stats = {
        pendiente: 0,
        en_atencion: 0,
        resuelto: 0
    };
    
    incidents.forEach(i => {
        if (stats.hasOwnProperty(i.estado)) {
            stats[i.estado]++;
        }
    });
    
    document.getElementById('count-pendiente').textContent = stats.pendiente;
    document.getElementById('count-atencion').textContent = stats.en_atencion;
    document.getElementById('count-resuelto').textContent = stats.resuelto;
}

async function updateStatus(incidentId, newStatus) {
    try {
        const response = await fetch(`${API_URL}/incidents/${incidentId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'x-user-role': localStorage.getItem('rol'),
                'x-user-name': localStorage.getItem('nombre')
            },
            body: JSON.stringify({
                estado: newStatus,
                responsable: localStorage.getItem('nombre')
            })
        });
        
        if (response.ok) {
            showToast(`Incidente actualizado a: ${newStatus}`);
            loadIncidents(); // Recargar
        }
    } catch (error) {
        console.error('Error updating:', error);
    }
}

function applyFilters() {
    const estado = document.getElementById('filter-estado').value;
    const urgencia = document.getElementById('filter-urgencia').value;
    
    let filtered = allIncidents;
    
    if (estado) {
        filtered = filtered.filter(i => i.estado === estado);
    }
    if (urgencia) {
        filtered = filtered.filter(i => i.urgencia === urgencia);
    }
    
    renderIncidents(filtered);
}

function getCardClass(urgencia) {
    const classes = {
        'baja': 'border-secondary',
        'media': 'border-warning',
        'alta': 'border-danger',
        'crítica': 'border-danger border-3'
    };
    return classes[urgencia] || '';
}

function getStatusBadge(estado) {
    const badges = {
        'pendiente': 'bg-warning',
        'en_atencion': 'bg-info',
        'resuelto': 'bg-success'
    };
    return badges[estado] || 'bg-secondary';
}

function formatDate(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString('es-PE');
}

function showToast(message) {
    const toastEl = document.getElementById('toast');
    const toast = new bootstrap.Toast(toastEl);
    document.querySelector('.toast-body').textContent = message;
    toast.show();
}
```

---

## 5. Costos (Gratis)

### Free Tier de AWS

| Servicio | Free Tier | Uso Estimado | Costo |
|----------|-----------|--------------|-------|
| Lambda | 1M requests/mes | 10,000 | $0 |
| API Gateway | 1M requests/mes | 10,000 | $0 |
| DynamoDB | 25GB + 25 RCU/WCU | <1GB | $0 |
| S3 | 5GB + 20k GET + 2k PUT | <1GB | $0 |
| CloudWatch | 5GB logs | <500MB | $0 |
| **TOTAL** | | | **$0** 🎉 |

---

## 6. Entregables

### ✅ Checklist Final

**1. Solución final funcional**:
- [ ] URL pública del frontend en S3
- [ ] CRUD completo funcionando
- [ ] Upload de fotos
- [ ] Polling de actualizaciones

**2. Repositorio GitHub**:
- [ ] Código Lambda (Python)
- [ ] Código Frontend (HTML/CSS/JS)
- [ ] README con instrucciones
- [ ] Screenshots

**3. Diagrama de arquitectura**:
- [ ] Diagrama en Eraser.io
- [ ] Exportado como PNG/PDF
- [ ] Incluye roadmap (Cognito, Airflow, SageMaker)

**4. Extras (bonus)**:
- [ ] Video demo (2-3 min)
- [ ] Presentación (PowerPoint/Google Slides)
- [ ] Documentación técnica

---

## 7. Tips para Presentación

### 🔥 Lo que MOSTRAR (demo en vivo):
1. **Crear incidente** con foto desde frontend
2. **Ver en lista** actualizada automáticamente
3. **Cambiar estado** como autoridad
4. **Polling en acción**: Abrir en 2 navegadores, mostrar sincronización
5. **CloudWatch logs**: Mostrar Lambda ejecutándose
6. **DynamoDB**: Mostrar tabla con datos

### 💬 Lo que EXPLICAR:
- **Serverless**: Sin servidores, 100% managed services
- **Escalable**: Auto-scaling de Lambda y DynamoDB
- **Costo cero**: Free Tier
- **24 horas**: Priorización de features core
- **Roadmap claro**: Cognito, WebSockets, Airflow, ML

### 🎯 Mensaje Clave:
> "Construimos un **MVP completamente funcional** en 24 horas con arquitectura serverless. La app está lista para usar hoy, y tenemos un roadmap claro para escalarla a producción."

---

## 8. Troubleshooting Común

### Problema: CORS Errors
**Solución**:
```python
headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type,x-user-role,x-user-name'
}
```

### Problema: Lambda timeout
**Solución**: Aumentar timeout a 30s en configuración

### Problema: DynamoDB access denied
**Solución**: Verificar IAM role tiene permisos correctos

### Problema: S3 upload falla
**Solución**: Verificar CORS en bucket, presigned URL válida

### Problema: Frontend no carga
**Solución**: Verificar bucket policy es pública, index.html en raíz

---

## 9. Conclusión

Esta arquitectura MVP es **100% factible en 24 horas** y cumple con los requisitos core del challenge. 

**Ventajas**:
- ✅ Serverless real
- ✅ Funcional end-to-end
- ✅ Costo cero
- ✅ Demo impresionante
- ✅ Escalable

**Próximos pasos después del MVP**:
1. Cognito para auth robusta
2. WebSocket para tiempo real <100ms
3. Airflow para workflows
4. SageMaker para ML

**¡Éxito en la hackathon! 🚀**
