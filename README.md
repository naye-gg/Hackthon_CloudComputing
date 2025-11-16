# # 🚨 AlertaUTEC - Sistema de Gestión de Incidentes

> Plataforma serverless para reportar, monitorear y gestionar incidentes dentro del campus UTEC en tiempo real

[![AWS](https://img.shields.io/badge/AWS-Serverless-orange)](https://aws.amazon.com)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

## 📋 Descripción

**AlertaUTEC** es una solución serverless desarrollada en 24 horas para la Hackathon Cloud Computing. Permite a estudiantes, personal y autoridades reportar y gestionar incidentes del campus de manera ágil y centralizada.

### ✨ Características Principales

- ✅ **CRUD Completo**: Crear, listar, actualizar y eliminar incidentes
- ✅ **Upload de Fotos**: Adjuntar evidencia visual a los reportes
- ✅ **Actualizaciones Automáticas**: Polling cada 5 segundos para refrescar datos
- ✅ **Panel Administrativo**: Vista especial para autoridades
- ✅ **100% Serverless**: Sin servidores que gestionar
- ✅ **Costo Cero**: Dentro de AWS Free Tier

## 🏗️ Arquitectura

### MVP Implementado (24 horas)

```
┌─────────────┐
│  Usuarios   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ S3 Frontend     │  (HTML/CSS/JS + Bootstrap)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ API Gateway     │  (REST API)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Lambda Handler  │  (Python 3.11)
└────┬────────────┘
     │
     ├──► DynamoDB (Incidentes)
     └──► S3 (Fotos)
```

### Servicios AWS Utilizados

| Servicio | Propósito | Costo |
|----------|-----------|-------|
| **S3** | Hosting frontend + almacenamiento fotos | $0 (Free Tier) |
| **API Gateway** | REST API endpoints | $0 (Free Tier) |
| **Lambda** | Lógica de negocio serverless | $0 (Free Tier) |
| **DynamoDB** | Base de datos NoSQL | $0 (Free Tier) |
| **CloudWatch** | Logs y monitoreo | $0 (Free Tier) |

**Total**: **$0/mes** dentro de Free Tier

## 🚀 Demo

**URL Frontend**: `http://alertautec-frontend.s3-website-us-east-1.amazonaws.com`
**API Endpoint**: `https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/prod`

### Screenshots

*(Agregar screenshots aquí)*

## 📁 Estructura del Proyecto

```
Hackthon_CloudComputing/
├── frontend/
│   ├── index.html          # Lista de incidentes
│   ├── crear.html          # Formulario crear incidente
│   ├── detalle.html        # Ver detalle
│   ├── login.html          # Selector de rol
│   ├── app.js              # Lógica JavaScript
│   └── styles.css          # Estilos
├── backend/
│   ├── lambda_function.py  # Lambda handler principal
│   ├── requirements.txt    # Dependencias Python
│   └── README.md           # Instrucciones deploy
├── docs/
│   ├── ARQUITECTURA_MVP_24H.md      # Documentación completa
│   ├── DIAGRAMA_ERASER_IO.md        # Código diagramas
│   └── arquitectura.png             # Diagrama visual
├── challenge.md            # Descripción del reto
├── bases.md                # Bases de la hackathon
└── README.md               # Este archivo
```

## 🛠️ Instalación y Deploy

### Prerrequisitos

- Cuenta AWS (Academy Lab o Free Tier)
- AWS CLI configurado
- Python 3.11+ o Node.js 18+

### 1. Backend (Lambda + API Gateway + DynamoDB)

```bash
# Crear tabla DynamoDB
aws dynamodb create-table \
  --table-name alertautec-incidents \
  --attribute-definitions AttributeName=incidentId,AttributeType=S \
  --key-schema AttributeName=incidentId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# Crear bucket para fotos
aws s3 mb s3://alertautec-photos
aws s3api put-bucket-cors --bucket alertautec-photos --cors-configuration file://cors.json

# Crear función Lambda
cd backend
zip function.zip lambda_function.py
aws lambda create-function \
  --function-name incident-handler \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR-ACCOUNT:role/lambda-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip \
  --timeout 30 \
  --memory-size 512

# Crear API Gateway (manual via Console o SAM)
```

### 2. Frontend (S3 Static Website)

```bash
# Crear bucket
aws s3 mb s3://alertautec-frontend

# Configurar Static Website Hosting
aws s3 website s3://alertautec-frontend --index-document index.html

# Hacer público
aws s3api put-bucket-policy --bucket alertautec-frontend --policy file://bucket-policy.json

# Subir archivos
cd frontend
aws s3 sync . s3://alertautec-frontend --acl public-read

# URL: http://alertautec-frontend.s3-website-us-east-1.amazonaws.com
```

### 3. Configurar Frontend con API URL

```javascript
// En frontend/app.js, actualizar:
const API_URL = 'https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/prod';
```

## 📖 Uso

### Como Estudiante

1. Abre el frontend
2. Selecciona rol "Estudiante"
3. Ingresa tu nombre
4. Clic en "+ Nuevo Incidente"
5. Llena el formulario:
   - Tipo: infraestructura, servicio, emergencia, otro
   - Ubicación: edificio y piso
   - Descripción: detalle del problema
   - Urgencia: baja, media, alta, crítica
   - (Opcional) Adjuntar foto
6. Enviar

### Como Autoridad

1. Selecciona rol "Autoridad"
2. Ve todos los incidentes
3. Usa filtros por estado/urgencia
4. Clic en botones:
   - **Atender**: Cambia a "en_atencion"
   - **Resolver**: Cambia a "resuelto"
5. Lista se actualiza automáticamente cada 5s

## 🧪 Testing

### Test Manual

```bash
# Crear incidente
curl -X POST https://API-URL/prod/incidents \
  -H "Content-Type: application/json" \
  -H "x-user-role: estudiante" \
  -H "x-user-name: Juan Perez" \
  -d '{
    "tipo": "infraestructura",
    "ubicacion": "Edificio A, Piso 3",
    "descripcion": "Aire acondicionado no funciona",
    "urgencia": "media",
    "reportadoPor": "Juan Perez",
    "rolReportador": "estudiante"
  }'

# Listar incidentes
curl https://API-URL/prod/incidents \
  -H "x-user-role: estudiante"

# Actualizar estado (como autoridad)
curl -X PUT https://API-URL/prod/incidents/INCIDENT-ID \
  -H "Content-Type: application/json" \
  -H "x-user-role: autoridad" \
  -H "x-user-name: Dra Lopez" \
  -d '{
    "estado": "resuelto",
    "responsable": "Dra Lopez"
  }'
```

### Ver Logs

```bash
# Logs de Lambda
aws logs tail /aws/lambda/incident-handler --follow

# Logs de API Gateway
aws logs tail /aws/apigateway/api-id --follow
```

## 🛣️ Roadmap (Fase 2)

### Features Planificadas

- [ ] **Amazon Cognito**: Autenticación robusta con MFA
- [ ] **WebSocket API**: Tiempo real <100ms (sin polling)
- [ ] **Apache Airflow**: Orquestación de workflows
  - Clasificación automática
  - Envío de notificaciones
  - Reportes periódicos
- [ ] **Amazon SageMaker**: Machine Learning
  - Clasificación automática de tipo
  - Predicción de urgencia
  - Detección de zonas de riesgo
- [ ] **SNS/SES**: Notificaciones email/SMS
- [ ] **QuickSight**: Dashboards y analytics
- [ ] **App móvil**: React Native

## 👥 Equipo

- **Backend Lead**: [Nombre] - Lambda, DynamoDB, API Gateway
- **Frontend Lead**: [Nombre] - HTML/CSS/JS, UX/UI
- **Full-Stack**: [Nombre] - Integración, testing
- **DevOps/Docs**: [Nombre] - AWS setup, documentación

## 📊 Métricas del Proyecto

- **Tiempo de desarrollo**: 24 horas
- **Líneas de código**:
  - Backend: ~300 líneas Python
  - Frontend: ~500 líneas JS/HTML/CSS
- **Servicios AWS**: 5 (S3, API Gateway, Lambda, DynamoDB, CloudWatch)
- **Costo**: $0 (Free Tier)
- **Latencia promedio**: <500ms
- **Disponibilidad**: 99.9% (SLA AWS)

## 📄 Documentación Adicional

- [Arquitectura Completa (MVP 24h)](./ARQUITECTURA_MVP_24H.md)
- [Diagramas Eraser.io](./DIAGRAMA_ERASER_IO.md)
- [Challenge Original](./challenge.md)
- [Bases Hackathon](./bases.md)

## 🤝 Contribuciones

Este proyecto fue desarrollado para la Hackathon Cloud Computing. Las contribuciones son bienvenidas:

1. Fork el proyecto
2. Crea un branch (`git checkout -b feature/nueva-feature`)
3. Commit cambios (`git commit -m 'Agregar nueva feature'`)
4. Push al branch (`git push origin feature/nueva-feature`)
5. Abre un Pull Request

## 📜 Licencia

MIT License - ver [LICENSE](LICENSE) para detalles

## 🏆 Agradecimientos

- **UTEC** por organizar la hackathon
- **AWS** por los servicios cloud
- Todos los mentores y participantes

---

**Desarrollado con ❤️ en 24 horas para Hackathon Cloud Computing**

*Noviembre 2025*