# Arquitectura de Solución - AlertaUTEC (MVP - 24 horas)
## Plataforma Serverless para Gestión de Incidentes en Campus Universitario

> **NOTA IMPORTANTE**: Esta arquitectura está diseñada para AWS Academy/Lab Learner Lab con restricciones de servicios y un desarrollo de 24 horas.

---

## 1. Resumen Ejecutivo

La arquitectura propuesta para **AlertaUTEC MVP** es una solución serverless **simplificada y realista** para 24 horas de desarrollo, usando únicamente servicios disponibles en AWS Lab (EC2, Lambda, API Gateway, DynamoDB, S3). Prioriza funcionalidad core sobre features avanzadas.

### Características Principales del MVP:
- ✅ **Servicios básicos únicamente**: Lambda, API Gateway, DynamoDB, S3, CloudWatch
- ✅ **Sin Cognito**: Autenticación simple con API Keys o JWT manual
- ✅ **Tiempo real simulado**: Polling cada 5 segundos (sin WebSockets complejos)
- ✅ **CRUD completo**: Crear, listar, actualizar y eliminar incidentes
- ✅ **Roles básicos**: Header simple para distinguir usuarios
- ✅ **Desarrollo rápido**: Implementable en 24 horas

---

## 2. Componentes de la Arquitectura MVP

### 2.1 Frontend y Hosting

**Amazon S3 Static Website Hosting**
- **Decisión**: Hosting estático simple vía S3
- **Justificación**: 
  - Disponible en AWS Lab
  - Setup en minutos
  - Sin configuraciones complejas
  - HTML/CSS/JS vanilla o React build estático
- **Uso**: Single Page Application (SPA) con HTML/JS puro o React
- **Configuración**: Bucket público con Static Website Hosting habilitado

### 2.2 Autenticación Simplificada (Sin Cognito)

**Autenticación Manual con JWT o API Key**
- **Decisión**: Sistema simple sin Cognito (no disponible en Lab)
- **Implementación Opción 1 - API Key simple**:
  - Cada rol tiene un API Key hardcodeado
  - `estudiante-key`, `personal-key`, `autoridad-key`
  - Se envía en header `x-api-key`
  - Lambda valida el key y asigna permisos
- **Implementación Opción 2 - JWT manual**:
  - Login simple devuelve JWT firmado con secret
  - Lambda genera y valida JWT
  - Payload incluye: `{userId, role, exp}`
- **Roles básicos**:
  - `estudiante`: Crear incidentes, ver propios
  - `autoridad`: Ver todos, actualizar estado
- **⚠️ Limitación**: Seguridad básica, solo para demo

### 2.3 API y Backend (CORE MVP)

**Amazon API Gateway REST API**
- **Decisión**: API REST simple (sin WebSocket)
- **Justificación**:
  - Disponible en AWS Lab
  - Setup rápido
  - Integración directa con Lambda
- **Endpoints implementados** (5 esenciales):
  ```
  POST   /incidents          - Crear incidente
  GET    /incidents          - Listar todos
  GET    /incidents/{id}     - Ver detalle
  PUT    /incidents/{id}     - Actualizar estado
  DELETE /incidents/{id}     - Eliminar (opcional)
  ```

**AWS Lambda (3 funciones mínimas)**
- **Decisión**: Solo funciones esenciales para MVP
- **Justificación**:
  - Menos código = menos bugs
  - Desarrollo en 24h
  - Disponible en Lab
- **Funciones MVP**:
  1. **`incident-handler`**: Función única que maneja todos los endpoints
     - Analiza event.httpMethod (GET/POST/PUT/DELETE)
     - Valida API key o JWT simple
     - CRUD completo en DynamoDB
     - Sube fotos a S3 con presigned URLs
  2. **`auth-handler`** (opcional): Login simple que genera token
  3. **`list-handler`**: Optimizado para listar con filtros

### 2.4 Base de Datos (SIMPLIFICADA)

**Amazon DynamoDB - 1 Tabla Única**
- **Decisión**: Single-table design para MVP
- **Justificación**:
  - Disponible en AWS Lab
  - Setup en minutos
  - Sin índices complejos para empezar
- **Tabla única: `alertautec-incidents`**
  - **PK**: `incidentId` (String, UUID generado en Lambda)
  - **Atributos**:
    ```json
    {
      "incidentId": "uuid-v4",
      "tipo": "infraestructura|servicio|emergencia|otro",
      "ubicacion": "Edificio A, Piso 3",
      "descripcion": "Texto libre",
      "urgencia": "baja|media|alta|crítica",
      "estado": "pendiente|en_atencion|resuelto",
      "reportadoPor": "nombre o email",
      "rolReportador": "estudiante|personal|autoridad",
      "fotoUrl": "s3://bucket/foto.jpg" (opcional),
      "createdAt": "2025-11-15T10:30:00Z",
      "updatedAt": "2025-11-15T11:00:00Z",
      "responsable": "Nombre autoridad" (opcional)
    }
    ```
  - **Sin GSI inicialmente** (agregar después si hay tiempo)
  - **Scan simple** para listar (suficiente para MVP con <1000 items)

### 2.5 Almacenamiento (SIMPLIFICADO)

**Amazon S3 - 2 Buckets**
- **Decisión**: Almacenamiento mínimo necesario
- **Justificación**:
  - Disponible en Lab
  - Setup rápido
- **Buckets MVP**:
  1. **`alertautec-frontend`**: Frontend estático (HTML/CSS/JS)
     - Static Website Hosting habilitado
     - Público para acceso web
  2. **`alertautec-incident-photos`**: Fotos de incidentes
     - Presigned URLs para upload desde frontend
     - Privado, acceso solo vía URL firmada

### 2.6 "Tiempo Real" Simplificado (Sin WebSockets)

**Polling desde Frontend**
- **Decisión**: Polling simple cada 5-10 segundos
- **Justificación**:
  - WebSockets requiere setup complejo (más tiempo)
  - Polling funciona perfectamente para MVP
  - Menos código = menos bugs
- **Implementación**:
  ```javascript
  // Frontend: refrescar cada 5 segundos
  setInterval(() => {
    fetch('/incidents').then(updateUI);
  }, 5000);
  ```
- **Experiencia**: Actualizaciones casi en tiempo real (5s delay aceptable)
- **Mejora futura**: WebSockets si hay tiempo sobrante

### 2.7 Notificaciones (OPCIONAL - Si hay tiempo)

**Sin notificaciones por ahora**
- **Decisión**: Notificaciones fuera del MVP inicial
- **Justificación**:
  - SNS/SES no crítico para demo funcional
  - Requiere configuración adicional
  - Panel administrativo muestra todo
- **Alternativa simple si hay tiempo**:
  - Console.log en Lambda (visible en CloudWatch)
  - Alert/Toast en frontend cuando hay cambios
  - Simular email guardando en DynamoDB tabla `notifications`

### 2.8 Orquestación (FUERA DEL MVP)

**Sin Airflow para el MVP**
- **Decisión**: Airflow fuera del scope de 24h
- **Justificación**:
  - MWAA no disponible en AWS Lab básico
  - Configuración compleja (varias horas)
  - No crítico para demo funcional
- **Alternativa para mencionar en presentación**:
  - "Implementaríamos Airflow para clasificación automática"
  - "EventBridge + Lambda Cron para tareas periódicas" (más simple)
  - Mostrar diagrama con Airflow como "futura implementación"
- **Si hay tiempo extra**:
  - CloudWatch Events + Lambda para tarea programada simple
  - Ejemplo: Lambda que cada hora clasifica incidentes pendientes

### 2.9 Análisis y Visualización (SIMPLIFICADO)

**Sin SageMaker/QuickSight en MVP**
- **Decisión**: ML y BI fuera del MVP de 24h
- **Justificación**:
  - SageMaker requiere horas de setup y entrenamiento
  - QuickSight no esencial para demo
  - Enfoque en funcionalidad CRUD primero
- **Alternativa simple en Frontend**:
  - **Gráficos básicos con Chart.js**:
    - Incidentes por estado (pie chart)
    - Incidentes por ubicación (bar chart)
    - Línea de tiempo (line chart)
  - **Estadísticas simples**:
    - Total de incidentes
    - Pendientes vs resueltos
    - Promedio de tiempo de resolución
  - Cálculos en frontend con JavaScript (datos de API)
- **Mención en presentación**:
  - "Fase 2 incluiría SageMaker para clasificación automática"
  - Mostrar diagrama con ML como roadmap futuro

### 2.10 Monitoreo Básico

**Amazon CloudWatch (automático)**
- **Decisión**: Logging básico incluido por defecto
- **Justificación**:
  - Sin configuración adicional
  - Lambda y API Gateway logean automáticamente
- **Uso mínimo**:
  - Ver logs de Lambda en CloudWatch Logs
  - Debugging de errores
  - `console.log()` en Lambda aparece en CloudWatch
- **Sin alarmas ni métricas custom** (no necesario para MVP)

### 2.11 Seguridad Básica

**AWS IAM (mínimo necesario)**
- **Decisión**: Rol único de Lambda con permisos básicos
- **Roles MVP**:
  - **`LambdaExecutionRole`**: Permisos para:
    - DynamoDB: GetItem, PutItem, UpdateItem, Scan
    - S3: GetObject, PutObject (bucket de fotos)
    - CloudWatch: Logs
- **Sin WAF** (no crítico para MVP)
- **Sin Secrets Manager** (secrets en variables de entorno de Lambda)

---

## 3. Flujos Principales del MVP

### 3.1 Flujo de Creación de Incidente (CORE)

1. **Usuario abre el frontend** (S3 Static Website)
2. **Ingresa con rol** (selecciona: estudiante/autoridad - sin login real)
3. **Llena formulario**: tipo, ubicación, descripción, urgencia
4. **(Opcional) Sube foto**: 
   - Frontend solicita presigned URL a Lambda
   - Lambda genera URL firmada de S3
   - Frontend hace PUT directo a S3
5. **Frontend envía POST /incidents**:
   ```json
   {
     "tipo": "infraestructura",
     "ubicacion": "Edificio A, Piso 3",
     "descripcion": "Aire acondicionado no funciona",
     "urgencia": "media",
     "reportadoPor": "Juan Pérez",
     "rolReportador": "estudiante",
     "fotoUrl": "s3://..." (si hay)
   }
   ```
6. **API Gateway** recibe request
7. **Lambda `incident-handler`**:
   - Genera UUID para incidentId
   - Agrega timestamps (createdAt, updatedAt)
   - Asigna estado inicial: "pendiente"
   - Guarda en DynamoDB
8. **Retorna 201 Created** con el incidente creado
9. **Frontend muestra confirmación** y redirige a lista

**Tiempo estimado de desarrollo**: 3-4 horas

### 3.2 Flujo de Listado de Incidentes

1. **Frontend carga** (`GET /incidents`)
2. **Lambda escanea DynamoDB** (Scan operation)
3. **Retorna array de incidentes**:
   ```json
   [
     {
       "incidentId": "abc-123",
       "tipo": "infraestructura",
       "estado": "pendiente",
       "urgencia": "media",
       "descripcion": "...",
       "createdAt": "2025-11-15T10:30:00Z"
     }
   ]
   ```
4. **Frontend renderiza tabla/cards**
5. **Polling cada 5 segundos** para refrescar automáticamente

**Tiempo estimado**: 2 horas

### 3.3 Flujo de Actualización de Estado (Autoridad)

1. **Autoridad ve lista de incidentes**
2. **Hace clic en "Atender" o "Resolver"**
3. **Frontend envía PUT /incidents/{id}**:
   ```json
   {
     "estado": "en_atencion",
     "responsable": "Dra. María López"
   }
   ```
4. **Lambda actualiza DynamoDB**:
   - UpdateItem con nuevo estado
   - Actualiza `updatedAt`
5. **Retorna 200 OK** con incidente actualizado
6. **Polling detecta cambio** y actualiza UI en otros navegadores

**Tiempo estimado**: 2 horas

### 3.4 Flujo de "Tiempo Real" con Polling

**Frontend (JavaScript)**:
```javascript
let lastFetch = null;

function pollIncidents() {
  fetch('/incidents')
    .then(res => res.json())
    .then(incidents => {
      updateUI(incidents);
      // Resaltar cambios si hay diferencias
      if (lastFetch) {
        highlightChanges(lastFetch, incidents);
      }
      lastFetch = incidents;
    });
}

// Poll cada 5 segundos
setInterval(pollIncidents, 5000);
```

**Experiencia de usuario**: Actualizaciones "casi" en tiempo real (5s de delay)

---

## 4. Decisiones Técnicas Clave

### 4.1 ¿Por qué Serverless?

**Ventajas para AlertaUTEC**:
- **Escalabilidad automática**: Durante picos (ej: emergencia real), la plataforma escala automáticamente sin intervención
- **Costo optimizado**: Solo se paga por uso real. En horarios de baja actividad (madrugada), costo es mínimo
- **Mantenimiento mínimo**: Sin servidores que parchear, actualizar o monitorear
- **Alta disponibilidad**: AWS garantiza SLA del 99.9% en la mayoría de servicios
- **Desarrollo rápido**: Enfocarse en lógica de negocio, no en infraestructura

### 4.2 ¿Por qué DynamoDB sobre RDS?

**Justificación**:
- **Serverless nativo**: No hay instancias que gestionar
- **Escalado automático**: Maneja de 0 a millones de requests sin configuración
- **Latencia predecible**: Milisegundos constantes independiente de la carga
- **DynamoDB Streams**: Eventos en tiempo real sin código adicional
- **Costo**: Más económico en cargas variables (campus universitario)

**Trade-off**: 
- Menor flexibilidad en queries complejas
- Solucionado con GSIs (índices secundarios) para filtros comunes

### 4.3 ¿Por qué Apache Airflow (MWAA)?

**Justificación**:
- **Orquestación compleja**: Los DAGs manejan workflows con múltiples pasos y dependencias
- **Reintentos y error handling**: Airflow maneja fallos automáticamente
- **Scheduling avanzado**: Cron expressions para tareas periódicas
- **Interfaz visual**: Monitoreo y debugging fácil
- **Comunidad**: Gran ecosistema de operadores (S3, Lambda, SageMaker, etc.)

**Alternativas consideradas**:
- **Step Functions**: Más serverless pero menos flexible para workflows complejos
- **EventBridge + Lambda**: No maneja dependencias complejas ni reintentos sofisticados
- **Decisión**: Airflow por requerimiento explícito en el challenge

### 4.4 ¿Por qué WebSockets sobre Polling?

**Ventajas**:
- **Eficiencia**: Conexión persistente, sin requests redundantes
- **Latencia real**: Actualizaciones en <100ms
- **Menor costo**: Menos invocaciones de Lambda
- **Mejor UX**: Actualizaciones fluidas sin recargar

**Implementación**:
- API Gateway WebSocket API (serverless)
- Lambda para manejar conexiones y mensajes
- DynamoDB para almacenar connectionIds

### 4.5 ¿Por qué SageMaker sobre Lambda ML?

**Justificación**:
- **Entrenamiento escalable**: Instancias GPU/CPU bajo demanda
- **Gestión de modelos**: Versionado, despliegue, A/B testing
- **Endpoints optimizados**: Inferencia rápida con autoscaling
- **Notebooks**: Experimentación y análisis
- **Pipelines**: Automatización de training/deployment

**Modelos elegidos**:
- **XGBoost**: Rápido, preciso para clasificación
- **BERT**: Para NLP en español (descripción de incidentes)
- **K-means**: Clustering de zonas de riesgo
- **Prophet**: Series temporales para predicción

---

## 5. Seguridad y Compliance

### 5.1 Autenticación y Autorización

- **Cognito**: Autenticación robusta con MFA opcional
- **JWT tokens**: Stateless, validación en API Gateway
- **Grupos de usuarios**: Roles granulares (estudiante, personal, autoridad)
- **Políticas IAM**: Permisos mínimos por servicio

### 5.2 Protección de Datos

- **Encriptación en reposo**: 
  - DynamoDB con KMS
  - S3 con SSE-S3 o SSE-KMS
- **Encriptación en tránsito**: 
  - HTTPS/WSS obligatorio
  - TLS 1.2+
- **Presigned URLs**: Acceso temporal y seguro a archivos S3

### 5.3 Protección de APIs

- **WAF**: Protección contra OWASP Top 10
- **Rate limiting**: Prevención de abuso
- **CORS**: Configuración estricta
- **API Keys**: Para integraciones externas (opcional)

### 5.4 Auditoría

- **CloudTrail**: Log de todas las acciones en AWS
- **IncidentHistory**: Trazabilidad completa de cambios
- **CloudWatch Logs**: Logs centralizados con retención configurable

---

## 6. Escalabilidad y Rendimiento

### 6.1 Capacidad

**Sin limitaciones prácticas**:
- **DynamoDB**: Millones de requests/seg con auto-scaling
- **Lambda**: Hasta 1000 ejecuciones concurrentes (aumentable)
- **WebSocket**: 100,000+ conexiones concurrentes
- **S3**: Almacenamiento ilimitado

**Para campus UTEC (estimación)**:
- ~5,000 usuarios (estudiantes + personal)
- ~100 incidentes/día promedio
- Picos de ~500 incidentes/hora en emergencias
- **Conclusión**: Arquitectura sobrada para la carga

### 6.2 Latencia

**Objetivos de rendimiento**:
- Creación de incidente: <500ms
- Actualización en tiempo real: <100ms
- Consulta de lista: <300ms
- Predicción ML: <1s

**Optimizaciones**:
- **API Gateway Cache**: Reduce llamadas a Lambda
- **DynamoDB DAX**: Caché en memoria (opcional)
- **CloudFront**: CDN global para frontend
- **Lambda Provisioned Concurrency**: Elimina cold starts (opcional)

### 6.3 Disponibilidad

**SLAs de AWS**:
- Amplify: 99.95%
- API Gateway: 99.95%
- Lambda: 99.95%
- DynamoDB: 99.99%
- S3: 99.99%

**Disponibilidad compuesta**: >99.8% sin configuración adicional

**Mejoras posibles**:
- Multi-región (overkill para un campus)
- DynamoDB Global Tables (replicación)

---

## 5. Costos del MVP (Prácticamente Gratis)

### 5.1 Capa Gratuita de AWS

**Servicios dentro de Free Tier**:
- ✅ **Lambda**: 1M requests/mes + 400,000 GB-segundos GRATIS
- ✅ **API Gateway**: 1M requests/mes GRATIS (primer año)
- ✅ **DynamoDB**: 25GB + 25 WCU + 25 RCU GRATIS siempre
- ✅ **S3**: 5GB + 20,000 GET + 2,000 PUT GRATIS (primer año)
- ✅ **CloudWatch**: 5GB logs GRATIS

**Estimación para hackathon (2-3 días)**:
- Requests totales: ~10,000 (testing + demo)
- Storage: <1GB
- **Costo total: $0.00** 🎉

### 5.2 AWS Academy Lab

**Créditos disponibles**: Generalmente $50-100
**Consumo estimado del MVP**: <$5 en todo el desarrollo
**Margen**: Muy cómodo para experimentar

---

## 6. Plan de Implementación (24 horas)

### Timeline Realista

#### **Horas 0-2: Setup Inicial** 🛠️
- [ ] Crear cuenta/Lab de AWS
- [ ] Crear repositorio GitHub
- [ ] Setup local: VS Code, AWS CLI, Python/Node
- [ ] Crear bucket S3 para frontend
- [ ] Crear tabla DynamoDB
- [ ] Crear bucket S3 para fotos

**Entregables**: Infraestructura base funcionando

#### **Horas 2-6: Backend Core** ⚙️
- [ ] Crear función Lambda `incident-handler`
- [ ] Implementar POST /incidents (crear)
- [ ] Implementar GET /incidents (listar)
- [ ] Implementar PUT /incidents/{id} (actualizar)
- [ ] Crear API Gateway REST
- [ ] Conectar endpoints a Lambda
- [ ] Testing con Postman/curl

**Entregables**: API funcional, CRUD completo

#### **Horas 6-8: Almacenamiento de Fotos** 🖼️
- [ ] Endpoint para generar presigned URLs
- [ ] Subir foto desde Postman (testing)
- [ ] Guardar URL en DynamoDB

**Entregables**: Upload de imágenes funcionando

#### **Horas 8-10: Break ☕** 
- Descanso, comer, revisar progreso
- Testing manual de lo implementado
- Fix de bugs encontrados

#### **Horas 10-16: Frontend** 🎨
- [ ] HTML base con Bootstrap/Tailwind
- [ ] Formulario de crear incidente
- [ ] Lista de incidentes (tabla o cards)
- [ ] Vista detalle de incidente
- [ ] Botón de actualizar estado (autoridad)
- [ ] Implementar polling cada 5 seg
- [ ] Upload de foto desde frontend
- [ ] Filtros básicos (por estado, urgencia)
- [ ] Responsive design

**Entregables**: Frontend funcional conectado a API

#### **Horas 16-18: Integración y Testing** 🧪
- [ ] Testing end-to-end
- [ ] Fix bugs de integración
- [ ] Validaciones de frontend
- [ ] Manejo de errores
- [ ] Loading states

**Entregables**: Aplicación completa funcionando

#### **Horas 18-20: Polish y Features Extra** ✨
- [ ] Estilos mejorados
- [ ] Animaciones/transiciones
- [ ] Estadísticas simples (contador de incidentes)
- [ ] Gráficos con Chart.js (opcional)
- [ ] Notificaciones toast/alert en frontend

**Entregables**: UI pulida

#### **Horas 20-22: Documentación y Diagrama** 📝
- [ ] README.md completo
- [ ] Diagrama de arquitectura en Eraser.io
- [ ] Screenshots de la aplicación
- [ ] Video demo (2-3 minutos)
- [ ] Preparar presentación

**Entregables**: Documentación completa

#### **Horas 22-24: Buffer y Deploy Final** 🚀
- [ ] Testing final en diferentes navegadores
- [ ] Fix de bugs de último minuto
- [ ] Subir frontend a S3
- [ ] Verificar URL pública funciona
- [ ] Push final a GitHub
- [ ] Preparar presentación/pitch

**Entregables**: ✅ **MVP COMPLETO Y FUNCIONAL**

### Distribución de Equipo (4 personas)

**Persona 1 - Backend Lead**:
- Lambda functions
- API Gateway
- DynamoDB operations
- S3 presigned URLs

**Persona 2 - Frontend Lead**:
- HTML/CSS/JS structure
- API integration (fetch)
- UI/UX design
- Responsive layout

**Persona 3 - Full-stack**:
- Ayuda backend (horas 2-8)
- Ayuda frontend (horas 10-16)
- Testing e integración
- Bug fixing

**Persona 4 - DevOps/Docs**:
- AWS setup inicial
- Monitoreo CloudWatch
- Documentación
- Diagrama de arquitectura
- Video demo

### Riesgos y Mitigaciones

| Riesgo | Probabilidad | Mitigación |
|--------|--------------|---------------|
| CORS errors | Alta | Configurar CORS en API Gateway desde el inicio |
| Lambda timeout | Media | Aumentar timeout a 30s, optimizar queries DynamoDB |
| Permisos IAM | Alta | Usar managed policies, documentar permisos necesarios |
| Frontend no conecta | Media | Testing incremental, usar Postman primero |
| Presigned URL expira | Baja | Configurar expiración de 1 hora |
| Polling consume muchos requests | Baja | Está dentro de Free Tier, no hay problema |

---

## 7. Features del MVP vs Roadmap Futuro

### ✅ MVP Funcional (24 horas)

**Core Features Implementadas**:
1. ✅ Crear incidentes con foto
2. ✅ Listar todos los incidentes
3. ✅ Ver detalle de incidente
4. ✅ Actualizar estado (pendiente/en atención/resuelto)
5. ✅ Roles básicos (estudiante/autoridad)
6. ✅ "Tiempo real" con polling (5s)
7. ✅ Estadísticas simples
8. ✅ Responsive design

**Arquitectura Serverless**:
- API Gateway REST + Lambda + DynamoDB + S3
- Completamente funcional y escalable
- Sin servidores que mantener

### 🛣️ Roadmap Futuro (Fase 2)

**Mejoras de Autenticación**:
- ⭕ Amazon Cognito para autenticación robusta
- ⭕ MFA para autoridades
- ⭕ Integración con directorio UTEC (SAML/LDAP)

**Tiempo Real Mejorado**:
- ⭕ WebSocket API para actualizaciones instantáneas (<100ms)
- ⭕ DynamoDB Streams + Lambda triggers
- ⭕ Notificaciones push en navegador

**Orquestación y Automatización**:
- ⭕ Apache Airflow (MWAA) para workflows complejos
- ⭕ Clasificación automática de incidentes
- ⭕ Envío de alertas a áreas responsables
- ⭕ Reportes periódicos automatizados

**Machine Learning**:
- ⭕ SageMaker para análisis predictivo
- ⭕ Clasificación automática de tipo de incidente
- ⭕ Predicción de urgencia
- ⭕ Detección de zonas de riesgo
- ⭕ Tendencias y patrones

**Analytics y BI**:
- ⭕ Amazon QuickSight dashboards
- ⭕ Heatmaps del campus
- ⭕ Análisis temporal avanzado
- ⭕ Predicciones de incidentes

**Notificaciones Avanzadas**:
- ⭕ Email vía SES
- ⭕ SMS vía SNS
- ⭕ Integración con Slack/Teams
- ⭕ Notificaciones push móviles

---

## 8. Conclusión
### MVP AlertaUTEC - Arquitectura Serverless Realista

La arquitectura propuesta es **pragmática y ejecutable en 24 horas** dentro de las restricciones de AWS Academy Lab. Prioriza:

✅ **Funcionalidad core completa**: CRUD de incidentes end-to-end
✅ **Serverless real**: Lambda, API Gateway, DynamoDB, S3
✅ **Experiencia fluida**: UI responsive con actualizaciones periódicas
✅ **Escalabilidad**: Arquitectura lista para producción
✅ **Costo cero**: Dentro de Free Tier de AWS
✅ **Demo impresionante**: Aplicación web funcional y profesional

### Cumplimiento de Requisitos

| Requisito del Challenge | Estado MVP | Implementación |
|-------------------------|------------|------------------|
| 1. Registro y autenticación | ✅ Parcial | Selección de rol simple (Cognito en roadmap) |
| 2. Reporte de incidentes | ✅ Completo | POST /incidents con foto |
| 3. Actualización tiempo real | ✅ Completo | Polling cada 5s (WebSocket en roadmap) |
| 4. Panel administrativo | ✅ Completo | Vista de autoridad con filtros |
| 5. Orquestación Airflow | ⭕ Roadmap | Mencionado en presentación |
| 6. Notificaciones | ⭕ Roadmap | Alert/toast en frontend |
| 7. Historial y trazabilidad | ✅ Completo | timestamps en DynamoDB |
| 8. Escalabilidad | ✅ Completo | Serverless auto-scaling |
| 9. Análisis predictivo (Opcional) | ⭕ Roadmap | Mencionado como Fase 2 |

**Cumplimiento**: 6/9 requisitos completos, 3/9 en roadmap (claramente documentados)

### Estrategia de Presentación
**Lo que MOSTRAR en demo**:
1. 🔥 Aplicación funcionando en vivo
2. 🔥 Crear incidente con foto en tiempo real
3. 🔥 Ver actualización en otro navegador (polling)
4. 🔥 Cambiar estado como autoridad
5. 🔥 Mostrar código de Lambda (destacar simplicidad)
6. 🔥 Mostrar CloudWatch logs (serverless en acción)

**Lo que EXPLICAR verbalmente**:
- ✨ Arquitectura serverless completa
- ✨ Escalabilidad automática
- ✨ Costo cero (Free Tier)
- ✨ Roadmap con Airflow, SageMaker, Cognito
- ✨ Por qué priorizamos funcionalidad sobre features avanzadas

**Mensaje clave**: 
> "Construimos un MVP **completamente funcional** en 24 horas usando arquitectura serverless. La aplicación está lista para usar hoy, y tenemos un roadmap claro para escalarla a producción con Airflow, ML y tiempo real avanzado."

### 🏆 Fortalezas para Evaluación
1. **Entregables completos**: ✅ Frontend funcional + ✅ Repo GitHub + ✅ Diagrama
2. **Solución técnica**: Arquitectura serverless real, bien diseñada
3. **Avance presentado**: MVP funcional end-to-end, no un prototipo a medias
4. **Bonus**: Documentación excelente, roadmap claro, justificaciones técnicas

### 🚀 ¡A Implementar!

Esta arquitectura es **100% factible en 24 horas** con un equipo de 3-4 personas. Sigue el plan de implementación, divide tareas, y tendrás una demo impresionante.

**¡Éxito en la hackathon! 🔥**
