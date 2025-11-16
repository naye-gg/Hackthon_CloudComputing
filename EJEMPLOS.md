# Ejemplos de uso de la API

## 1. Registrar Usuario

```bash
curl -X POST https://tu-api-gateway-url/dev/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "estudiante@utec.edu.pe",
    "password": "123456",
    "rol": "estudiante"
  }'
```

**Respuesta:**
```json
{
  "ok": true,
  "userId": "USR_84a9d",
  "message": "Usuario registrado correctamente"
}
```

## 2. Login

```bash
curl -X POST https://tu-api-gateway-url/dev/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "estudiante@utec.edu.pe",
    "password": "123456"
  }'
```

**Respuesta:**
```json
{
  "ok": true,
  "token": "JWT_GENERADO",
  "user": {
    "userId": "USR_84a9d",
    "rol": "estudiante"
  }
}
```

## 3. Crear Incidente

```bash
curl -X POST https://tu-api-gateway-url/dev/incidentes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer JWT_TOKEN" \
  -d '{
    "tipo": "Seguridad",
    "descripcion": "Persona sospechosa en entrada principal",
    "ubicacion": "Entrada A",
    "urgencia": "alta"
  }'
```

**Respuesta:**
```json
{
  "ok": true,
  "incidenteId": "INC_12ba1",
  "estado": "pendiente"
}
```

## 4. Listar Incidentes

```bash
curl -X GET https://tu-api-gateway-url/dev/incidentes \
  -H "Authorization: Bearer JWT_TOKEN"
```

**Respuesta:**
```json
{
  "ok": true,
  "items": [
    {
      "incidenteId": "INC_12ba1",
      "tipo": "Seguridad",
      "estado": "pendiente",
      "ubicacion": "Entrada A",
      "urgencia": "alta",
      "descripcion": "Persona sospechosa...",
      "fechaCreacion": "2025-11-15T10:30:00.000Z"
    }
  ]
}
```

## 5. Obtener Incidente

```bash
curl -X GET https://tu-api-gateway-url/dev/incidentes/INC_12ba1 \
  -H "Authorization: Bearer JWT_TOKEN"
```

**Respuesta:**
```json
{
  "ok": true,
  "incidente": {
    "incidenteId": "INC_12ba1",
    "tipo": "Seguridad",
    "descripcion": "Persona sospechosa...",
    "estado": "pendiente",
    "ubicacion": "Entrada A",
    "urgencia": "alta",
    "fechaCreacion": "2025-11-15T10:30:00.000Z",
    "historial": [
      {
        "accion": "creado",
        "fecha": "2025-11-15T10:30:00.000Z"
      }
    ]
  }
}
```

## 6. Actualizar Estado

```bash
curl -X PATCH https://tu-api-gateway-url/dev/incidentes/INC_12ba1/estado \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer JWT_TOKEN" \
  -d '{
    "nuevoEstado": "en_atencion"
  }'
```

**Respuesta:**
```json
{
  "ok": true,
  "incidenteId": "INC_12ba1",
  "estado": "en_atencion"
}
```

## 7. WebSocket - Conectar

```javascript
const ws = new WebSocket('wss://tu-websocket-url/dev');

ws.onopen = () => {
  console.log('Conectado al WebSocket');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Notificación recibida:', data);
  // { evento: "estado_actualizado", incidenteId: "INC_12ba1", nuevoEstado: "en_atencion" }
};

ws.onerror = (error) => {
  console.error('Error en WebSocket:', error);
};

ws.onclose = () => {
  console.log('Desconectado del WebSocket');
};
```

## Estados válidos para incidentes

- `pendiente` - Incidente creado, esperando atención
- `en_atencion` - Personal está atendiendo el incidente
- `resuelto` - Incidente resuelto
- `cancelado` - Incidente cancelado
