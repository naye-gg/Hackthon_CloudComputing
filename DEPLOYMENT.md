# Guía de Despliegue - Alerta UTEC Backend

## 📋 Requisitos Previos

1. **Node.js 18+** instalado
2. **AWS CLI** configurado con credenciales
3. **Serverless Framework** instalado globalmente

## 🔧 Configuración Inicial

### 1. Instalar Node.js y npm
```bash
# Verificar instalación
node --version
npm --version
```

### 2. Instalar AWS CLI
```bash
# Verificar instalación
aws --version

# Configurar credenciales
aws configure
```

### 3. Instalar Serverless Framework
```bash
npm install -g serverless

# Verificar instalación
serverless --version
```

## 🚀 Pasos de Despliegue

### 1. Instalar Dependencias
```bash
cd BackendHack
npm install
```

### 2. Desplegar a AWS
```bash
npm run deploy
# o
serverless deploy
```

Este comando:
- Empaqueta todo el código
- Crea las tablas DynamoDB
- Despliega las funciones Lambda
- Configura API Gateway (REST y WebSocket)
- Configura permisos IAM

### 3. Obtener URLs

Después del despliegue, verás las URLs:

```
endpoints:
  POST - https://xxxxx.execute-api.us-east-1.amazonaws.com/dev/auth/register
  POST - https://xxxxx.execute-api.us-east-1.amazonaws.com/dev/auth/login
  POST - https://xxxxx.execute-api.us-east-1.amazonaws.com/dev/incidentes
  GET - https://xxxxx.execute-api.us-east-1.amazonaws.com/dev/incidentes
  GET - https://xxxxx.execute-api.us-east-1.amazonaws.com/dev/incidentes/{id}
  PATCH - https://xxxxx.execute-api.us-east-1.amazonaws.com/dev/incidentes/{id}/estado

websocket:
  wss://yyyyy.execute-api.us-east-1.amazonaws.com/dev
```

**⚠️ IMPORTANTE:** Guarda estas URLs para configurar tu frontend.

## 🧪 Probar el Backend

### Opción 1: Usando curl (PowerShell)

```powershell
# Registrar usuario
Invoke-RestMethod -Uri "https://tu-api-url/dev/auth/register" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"test@utec.edu.pe","password":"123456","rol":"estudiante"}'

# Login
Invoke-RestMethod -Uri "https://tu-api-url/dev/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"test@utec.edu.pe","password":"123456"}'
```

### Opción 2: Usando Postman

1. Importa la colección de endpoints (ver EJEMPLOS.md)
2. Configura las variables de entorno con tu URL
3. Prueba cada endpoint

## 📊 Verificar Recursos en AWS

### Ver Tablas DynamoDB
```bash
aws dynamodb list-tables
```

### Ver Funciones Lambda
```bash
aws lambda list-functions --query "Functions[?starts_with(FunctionName, 'alerta-utec-backend')]"
```

### Ver APIs
```bash
aws apigateway get-rest-apis
aws apigatewayv2 get-apis
```

## 🔍 Ver Logs

### Ver logs de una función específica
```bash
serverless logs -f crearIncidente -t
# o
npm run logs crearIncidente
```

### Ver logs en AWS CloudWatch
```bash
aws logs tail /aws/lambda/alerta-utec-backend-dev-crearIncidente --follow
```

## 🔄 Actualizar el Backend

Si haces cambios en el código:

```bash
# Redesplegar todo
serverless deploy

# O desplegar solo una función (más rápido)
serverless deploy function -f crearIncidente
```

## 🗑️ Eliminar el Backend

Para eliminar todos los recursos de AWS:

```bash
npm run remove
# o
serverless remove
```

**⚠️ ADVERTENCIA:** Esto eliminará todas las tablas y datos.

## 🐛 Solución de Problemas

### Error: "AWS credentials not configured"
```bash
aws configure
# Ingresa tus credenciales
```

### Error: "Cannot find module"
```bash
npm install
```

### Error: "Rate exceeded"
```bash
# Espera unos minutos y vuelve a intentar
serverless deploy
```

### Ver errores detallados
```bash
serverless deploy --verbose
```

## 📝 Variables de Entorno

Para configurar variables de entorno, edita `serverless.yml`:

```yaml
provider:
  environment:
    JWT_SECRET: "tu-secreto-aqui"
    STAGE: ${self:provider.stage}
```

## 🔐 Seguridad

### Mejores prácticas:

1. **Cambiar JWT_SECRET** en producción
2. **Usar AWS Secrets Manager** para credenciales
3. **Habilitar CORS** solo para dominios específicos
4. **Agregar rate limiting** en API Gateway
5. **Usar autenticación** en todos los endpoints sensibles

## 📚 Comandos Útiles

```bash
# Ver información del stack
serverless info

# Ver métricas
serverless metrics

# Invocar función localmente
serverless invoke local -f crearIncidente -p test-event.json

# Ver configuración
serverless print
```

## 🎯 Próximos Pasos

1. ✅ Backend desplegado
2. Configurar frontend con las URLs obtenidas
3. Probar integración completa
4. Configurar CI/CD (opcional)
5. Monitoreo con CloudWatch
