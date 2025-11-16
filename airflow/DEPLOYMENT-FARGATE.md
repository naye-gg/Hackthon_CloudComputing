# 🚀 Guía de Despliegue: Apache Airflow en AWS ECS Fargate

## 📋 Arquitectura

```
Apache Airflow (ECS Fargate)
├── Webserver (UI)
├── Scheduler (Orchestrator)
└── PostgreSQL RDS (Metadata DB)
      ↓
Lambda Functions (Backend)
      ↓
DynamoDB (Data)
```

## 🎯 Opción 1: Docker Local (Desarrollo)

### 1. Configurar Credenciales

```powershell
# En la carpeta airflow/
cp .env.example .env

# Editar .env con tus credenciales de AWS Academy
notepad .env
```

### 2. Iniciar Airflow

```powershell
cd airflow
docker-compose up -d
```

### 3. Acceder a Airflow UI

```
URL: http://localhost:8080
Usuario: admin
Contraseña: admin
```

### 4. Verificar DAGs

Los 3 DAGs deberían aparecer automáticamente:
- `clasificar_incidentes` - Cada 5 minutos
- `enviar_notificaciones` - Cada 3 minutos
- `generar_reportes` - Cada 6 horas

### 5. Activar DAGs

En la UI de Airflow, activa cada DAG con el toggle switch.

---

## 🐳 Opción 2: Desplegar en ECS Fargate (AWS Academy)

### Paso 1: Crear Repositorio ECR

```powershell
# Crear repositorio para la imagen Docker
aws ecr create-repository --repository-name alerta-utec-airflow
```

### Paso 2: Build y Push de la Imagen

```powershell
# Obtener URI del repositorio
$REPO_URI = (aws ecr describe-repositories --repository-names alerta-utec-airflow --query 'repositories[0].repositoryUri' --output text)

# Login a ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $REPO_URI

# Build de la imagen
cd c:\Users\karol\BackendHack
docker build -f airflow/Dockerfile -t alerta-utec-airflow .

# Tag de la imagen
docker tag alerta-utec-airflow:latest ${REPO_URI}:latest

# Push a ECR
docker push ${REPO_URI}:latest
```

### Paso 3: Crear Base de Datos RDS (PostgreSQL)

**Opción A: Consola AWS**
1. Ir a RDS → Create database
2. PostgreSQL 14
3. Free tier / db.t3.micro
4. Database name: `airflow`
5. Username: `airflow`
6. Password: `airflow123`
7. Public access: Yes (para desarrollo)
8. Security Group: Permitir puerto 5432

**Opción B: CLI**

```powershell
aws rds create-db-instance `
  --db-instance-identifier alerta-utec-airflow-db `
  --db-instance-class db.t3.micro `
  --engine postgres `
  --master-username airflow `
  --master-user-password airflow123 `
  --allocated-storage 20 `
  --publicly-accessible `
  --db-name airflow
```

### Paso 4: Crear Task Definition para ECS

Crear archivo `task-definition.json`:

```json
{
  "family": "alerta-utec-airflow",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::429096294781:role/LabRole",
  "taskRoleArn": "arn:aws:iam::429096294781:role/LabRole",
  "containerDefinitions": [
    {
      "name": "airflow-webserver",
      "image": "TU_REPO_URI:latest",
      "essential": true,
      "command": ["webserver"],
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN",
          "value": "postgresql+psycopg2://airflow:airflow123@TU_RDS_ENDPOINT:5432/airflow"
        },
        {
          "name": "AIRFLOW__CORE__EXECUTOR",
          "value": "LocalExecutor"
        },
        {
          "name": "AIRFLOW__CORE__LOAD_EXAMPLES",
          "value": "false"
        },
        {
          "name": "AWS_DEFAULT_REGION",
          "value": "us-east-1"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/alerta-utec-airflow",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "webserver"
        }
      }
    },
    {
      "name": "airflow-scheduler",
      "image": "TU_REPO_URI:latest",
      "essential": true,
      "command": ["scheduler"],
      "environment": [
        {
          "name": "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN",
          "value": "postgresql+psycopg2://airflow:airflow123@TU_RDS_ENDPOINT:5432/airflow"
        },
        {
          "name": "AIRFLOW__CORE__EXECUTOR",
          "value": "LocalExecutor"
        },
        {
          "name": "AIRFLOW__CORE__LOAD_EXAMPLES",
          "value": "false"
        },
        {
          "name": "AWS_DEFAULT_REGION",
          "value": "us-east-1"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/alerta-utec-airflow",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "scheduler"
        }
      }
    }
  ]
}
```

### Paso 5: Crear CloudWatch Log Group

```powershell
aws logs create-log-group --log-group-name /ecs/alerta-utec-airflow
```

### Paso 6: Registrar Task Definition

```powershell
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

### Paso 7: Crear Cluster ECS

```powershell
aws ecs create-cluster --cluster-name alerta-utec-airflow-cluster
```

### Paso 8: Crear Servicio ECS

```powershell
# Obtener Subnet y Security Group de tu VPC
$SUBNET_ID = (aws ec2 describe-subnets --query 'Subnets[0].SubnetId' --output text)
$SG_ID = (aws ec2 describe-security-groups --query 'SecurityGroups[0].GroupId' --output text)

# Crear servicio
aws ecs create-service `
  --cluster alerta-utec-airflow-cluster `
  --service-name airflow-service `
  --task-definition alerta-utec-airflow `
  --desired-count 1 `
  --launch-type FARGATE `
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_ID],securityGroups=[$SG_ID],assignPublicIp=ENABLED}"
```

### Paso 9: Inicializar Base de Datos

Necesitas ejecutar una tarea one-time para inicializar Airflow:

```powershell
aws ecs run-task `
  --cluster alerta-utec-airflow-cluster `
  --task-definition alerta-utec-airflow `
  --launch-type FARGATE `
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_ID],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" `
  --overrides '{\"containerOverrides\":[{\"name\":\"airflow-webserver\",\"command\":[\"bash\",\"-c\",\"airflow db migrate && airflow users create --username admin --firstname Admin --lastname UTEC --role Admin --email admin@utec.edu.pe --password admin\"]}]}'
```

### Paso 10: Obtener URL Pública

```powershell
# Obtener ID de la tarea
$TASK_ARN = (aws ecs list-tasks --cluster alerta-utec-airflow-cluster --service-name airflow-service --query 'taskArns[0]' --output text)

# Obtener IP pública
aws ecs describe-tasks --cluster alerta-utec-airflow-cluster --tasks $TASK_ARN --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text | ForEach-Object {
    aws ec2 describe-network-interfaces --network-interface-ids $_ --query 'NetworkInterfaces[0].Association.PublicIp' --output text
}
```

Accede a: `http://IP_PUBLICA:8080`

---

## 📊 Verificar DAGs Funcionando

### En la UI de Airflow:

1. **DAGs** → Deberías ver los 3 DAGs
2. Activa cada uno con el toggle
3. **Graph View** → Ver el flujo de tareas
4. **Logs** → Ver ejecución en tiempo real

### Probar Manualmente:

```powershell
# Crear un incidente de prueba
Invoke-RestMethod -Uri "https://if1stu7r2g.execute-api.us-east-1.amazonaws.com/dev/incidentes" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"tipo":"Seguridad","descripcion":"Prueba Airflow","ubicacion":"Lab A","urgencia":"alta"}'
```

Espera 5 minutos y verifica en Airflow Logs que el DAG de clasificación lo procesó.

---

## 🔧 Troubleshooting

### Error: No se puede conectar a RDS
```powershell
# Verificar security group permite puerto 5432
aws ec2 authorize-security-group-ingress `
  --group-id $SG_ID `
  --protocol tcp `
  --port 5432 `
  --cidr 0.0.0.0/0
```

### Error: Task no inicia
```powershell
# Ver logs
aws logs tail /ecs/alerta-utec-airflow --follow
```

### Error: DAGs no aparecen
- Verificar que la imagen Docker tiene los DAGs en `/opt/airflow/dags`
- Rebuild y push la imagen

---

## 💰 Costos Estimados (AWS Academy - Gratis)

- ECS Fargate: Incluido en Academy
- RDS t3.micro: Incluido en Academy
- ECR: 500 MB gratis
- CloudWatch Logs: 5 GB gratis

---

## 🎯 Siguiente Paso: Integración con SageMaker

Para el análisis predictivo (opcional), conecta Airflow con SageMaker:

```python
# Nuevo DAG: airflow/dags/modelo_predictivo.py
from airflow.providers.amazon.aws.operators.sagemaker import SageMakerTrainingOperator
```

¿Necesitas ayuda con SageMaker para el análisis predictivo?
