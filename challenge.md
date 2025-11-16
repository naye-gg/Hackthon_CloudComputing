Alerta UTEC
Desarrollar una plataforma serverless para reportar, monitorear y gestionar incidentes dentro del campus UTEC en tiempo real

Contexto
La Universidad de Ingeniería y Tecnología (UTEC), como toda institución educativa, enfrenta diversos incidentes dentro de su campus: desde problemas de infraestructura y fallas en los servicios, hasta situaciones de emergencia que requieren atención inmediata. Sin embargo, muchos de estos incidentes pasan desapercibidos o no son atendidos con la rapidez y eficacia necesarias por las áreas responsables.

Ante esta situación, la universidad los ha convocado para diseñar una solución tecnológica que permita reportar, gestionar y dar seguimiento a los incidentes dentro del campus de manera ágil, segura y centralizada, facilitando la comunicación entre los estudiantes, el personal administrativo y las autoridades competentes.

Objetivos del Proyecto
El objetivo principal del proyecto AlertaUTEC es desarrollar una plataforma 100% serverless que permita reportar, monitorear y gestionar incidentes dentro del campus universitario en tiempo real, optimizando la comunicación entre los usuarios y las autoridades correspondientes.

Objetivos específicos
•
Diseñar una arquitectura completamente serverless, aprovechando servicios gestionados en la nube (como Amplify, AWS Lambda, API Gateway, DynamoDB y S3) para garantizar escalabilidad, alta disponibilidad y bajo mantenimiento.
•
Implementar comunicación en tiempo real mediante WebSockets, permitiendo que los reportes, actualizaciones de estado y notificaciones de incidentes se sincronicen instantáneamente.
•
Orquestar y automatizar los flujos de procesamiento con Apache Airflow, gestionando tareas como la clasificación automática, envío de alertas y análisis de patrones.
•
Garantizar una experiencia fluida y segura para los usuarios, asegurando autenticación, control de roles y trazabilidad de cada incidente.
•
Proveer herramientas de análisis y visualización, idealmente usando AWS SageMaker para identificar tendencias y zonas críticas.
Requerimientos
1. Registro y autenticación de usuarios
• El sistema debe permitir registro e inicio de sesión mediante credenciales institucionales
• Se debe distinguir entre roles: estudiante, personal administrativo y autoridad
2. Reporte de incidentes
• Los usuarios deben poder crear reportes indicando tipo, ubicación, descripción y nivel de urgencia
• Cada incidente se almacena en una base de datos serverless (DynamoDB)
• Se genera automáticamente un identificador único por reporte
3. Actualización y seguimiento en tiempo real
• El sistema actualiza el estado de incidentes en tiempo real usando WebSockets
• Notificaciones instantáneas cuando un incidente cambia de estado
• Estados: pendiente, en atención, resuelto
4. Panel administrativo
• Visualizar un panel con todos los incidentes activos
• Permitir filtrar, priorizar y cerrar reportes
• Actualizaciones en tiempo real sin recargar la página
5. Orquestación de flujos con Apache Airflow
• Clasificación automática de incidentes por tipo o urgencia
• Envío de notificaciones a áreas responsables
• Generación periódica de reportes estadísticos
6. Gestión de notificaciones
• Alertas en tiempo real mediante WebSocket y notificaciones asíncronas (correo o SMS) según gravedad

7. Historial y trazabilidad
• Historial completo de acciones (creación, actualizaciones, responsables, fecha y hora)

8. Escalabilidad y resiliencia
• Componentes serverless y escalables automáticamente

9. Análisis Predictivo y visualización inteligente (Opcional)
• Integrar modelo de machine learning entrenado en AWS SageMaker
• Identificar patrones, zonas de riesgo y tendencias de recurrencia
• Predicciones sobre tipos de incidentes más probables en áreas y horarios específicos
📋 Recuerda
Lee las Bases del Desafío para conocer los requisitos específicos, los criterios de evaluación y la estructura del reto

Envía tu Solución