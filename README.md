# Alerta UTEC - Backend

Sistema de alertas en tiempo real para UTEC usando AWS Lambda, API Gateway, DynamoDB y WebSockets.

## 📋 Requisitos

- Node.js 18+
- AWS CLI configurado
- Serverless Framework

## 🚀 Instalación

```bash
npm install
```

## 📦 Despliegue

```bash
npm run deploy
```

## 🧪 Endpoints

### Autenticación
- `POST /auth/register` - Registrar usuario
- `POST /auth/login` - Iniciar sesión

### Incidentes
- `POST /incidentes` - Crear incidente
- `GET /incidentes` - Listar incidentes
- `GET /incidentes/{id}` - Obtener incidente
- `PATCH /incidentes/{id}/estado` - Actualizar estado

### WebSocket
- `$connect` - Conectar cliente
- `$disconnect` - Desconectar cliente
- `notify` - Enviar notificaciones

## 🗄️ Estructura

```
backend/
├── serverless.yml
├── package.json
├── src/
│   ├── auth/
│   ├── incidentes/
│   └── websocket/
└── db/
```
