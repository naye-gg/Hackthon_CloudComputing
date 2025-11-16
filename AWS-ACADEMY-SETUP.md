# Configurar AWS Academy Credentials para Serverless

## 🔐 Paso 1: Obtener Credenciales de AWS Academy

1. Entra a tu **AWS Academy Learner Lab**
2. Haz clic en **"AWS Details"**
3. Haz clic en **"Show"** en AWS CLI credentials
4. Copia TODO el bloque que aparece (se ve así):

```ini
[default]
aws_access_key_id=ASIAXXXXXXXXXXX
aws_secret_access_key=xxxxxxxxxxxxxxxxxxxxx
aws_session_token=IQoJb3JpZ2luX2VjEPz//////////wEaCXVzLWVhc3QtMSJHMEU...
```

## 🛠️ Paso 2: Configurar en Windows

### Opción A: Archivo de Credenciales (Recomendado)

```powershell
# Crear carpeta .aws si no existe
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.aws"

# Abrir el archivo de credenciales
notepad "$env:USERPROFILE\.aws\credentials"
```

**Pega el contenido** que copiaste de AWS Academy y guarda.

### Opción B: Variables de Entorno (Temporal)

```powershell
# Reemplaza con tus valores de AWS Academy
$env:AWS_ACCESS_KEY_ID="ASIAXXXXXXXXXXX"
$env:AWS_SECRET_ACCESS_KEY="xxxxxxxxxxxxxxxxxxxxx"
$env:AWS_SESSION_TOKEN="IQoJb3JpZ2luX2VjEPz//////////..."
$env:AWS_DEFAULT_REGION="us-east-1"
```

## ✅ Paso 3: Verificar Configuración

```powershell
# Verificar que funciona
aws sts get-caller-identity
```

Deberías ver algo como:
```json
{
    "UserId": "AIDAXXXXXXXXX:voclabs/user12345",
    "Account": "123456789012",
    "Arn": "arn:aws:sts::123456789012:assumed-role/..."
}
```

## 🚀 Paso 4: Desplegar

```powershell
# Ahora sí funcionará
npm run deploy
```

## ⚠️ IMPORTANTE sobre AWS Academy

### Limitaciones:
1. **Credenciales temporales** - Expiran cada 3-4 horas
2. **No puedes crear usuarios IAM** - Usa solo las credenciales del lab
3. **Región fija** - Generalmente `us-east-1`
4. **Permisos limitados** - Algunos recursos pueden fallar

### Si no funciona `serverless deploy`:

Alternativa manual en la consola AWS:

1. **Crear tablas DynamoDB** manualmente
2. **Crear funciones Lambda** una por una
3. **Crear API Gateway** manualmente
4. **Subir código** como .zip a Lambda

## 🔄 Refrescar Credenciales

Cuando expiren (verás errores de autenticación):

```powershell
# Vuelve a AWS Academy → AWS Details → Show
# Copia las nuevas credenciales
# Actualiza el archivo .aws/credentials
```

## 🎯 Alternativa: Version Express en EC2

Si AWS Academy te da muchos problemas con Lambda, te creo la versión Express que es más compatible con las limitaciones del lab.

**¿Qué prefieres?**
- Intentar con credenciales de Academy
- Crear versión Express para EC2
