# Backend Portfolio Clara Rey

Backend en Flask para manejar el formulario de contacto del portfolio.

## Funcionalidades

- ✅ Recibe datos del formulario de contacto
- ✅ Valida los campos requeridos
- ✅ Envía emails usando Gmail SMTP
- ✅ Maneja CORS para el frontend
- ✅ Configurado para Render

## Variables de Entorno Necesarias

Crea un archivo `.env` basado en `.env.example`:

```bash
EMAIL_USER=tu_email@gmail.com
EMAIL_PASSWORD=tu_password_de_aplicacion_gmail
```

## Configurar Gmail

1. Ve a [myaccount.google.com](https://myaccount.google.com)
2. Ir a Seguridad → Verificación en 2 pasos (debe estar activada)
3. Ir a Contraseñas de aplicaciones
4. Crear nueva contraseña para "Aplicación personalizada"
5. Usar esa contraseña en `EMAIL_PASSWORD`

## Deploy en Render

1. Conectar repositorio en Render
2. Configurar variables de entorno
3. Render detectará automáticamente el `render.yaml`

## Endpoints

- `GET /` - Info del servicio
- `POST /contact` - Recibir formulario de contacto
- `GET /health` - Health check

## Uso Local

```bash
pip install -r requirements.txt
python app.py
```
