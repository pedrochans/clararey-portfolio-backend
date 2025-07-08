# 🧪 **GUÍA PARA PROBAR EL BACKEND EN RENDER**

## **1. Probar el Health Check**
Visita directamente en el navegador:
```
https://TU-URL-DE-RENDER.onrender.com/health
```
Deberías ver: `{"status": "healthy"}`

## **2. Probar la Página Principal**
Visita:
```
https://TU-URL-DE-RENDER.onrender.com/
```
Deberías ver información del servicio y endpoints disponibles.

## **3. Probar el Endpoint de Contacto con cURL**

Abre terminal y ejecuta (reemplaza la URL por la tuya):

```bash
curl -X POST https://clararey-portfolio-backend.onrender.com/contact \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Prueba",
    "apellido": "Test",
    "email": "test@example.com",
    "mensaje": "Este es un mensaje de prueba para verificar que el formulario funciona correctamente."
  }'
```

## **4. Probar con Postman o Insomnia**

1. **Método**: POST
2. **URL**: `https://clararey-portfolio-backend.onrender.com/contact`
3. **Headers**: `Content-Type: application/json`
4. **Body (JSON)**:
```json
{
  "nombre": "Prueba",
  "apellido": "Test", 
  "email": "test@example.com",
  "mensaje": "Mensaje de prueba desde Postman"
}
```

## **5. Probar desde el Navegador (JavaScript Console)**

Ve a cualquier página web, abre las Developer Tools (F12), ve a Console y ejecuta:

```javascript
fetch('https://clararey-portfolio-backend.onrender.com/contact', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    nombre: 'Prueba',
    apellido: 'Browser',
    email: 'test@example.com',
    mensaje: 'Mensaje de prueba desde browser console'
  })
})
.then(response => response.json())
.then(data => console.log('Success:', data))
.catch(error => console.error('Error:', error));
```

## **📧 Verificar Emails**

Después de cualquier prueba exitosa, deberías recibir un email en `clarareigle5@gmail.com`.

## **❗ Problemas Comunes**

### **503 Service Unavailable**
- El servicio está iniciando (plan gratuito de Render)
- Espera 1-2 minutos y vuelve a intentar

### **Error 500**
- Variables de entorno no configuradas
- Ve a Render Dashboard → Environment → Variables

### **CORS Error** 
- Solo desde el browser
- El backend acepta requests desde cualquier origen

## **🔍 Ver Logs en Render**

1. Ve a tu servicio en Render Dashboard
2. Click en "Logs" 
3. Verás los mensajes del servidor en tiempo real

## **✅ Respuestas Esperadas**

**Éxito**:
```json
{
  "success": true,
  "message": "Mensaje enviado correctamente"
}
```

**Error de validación**:
```json
{
  "success": false,
  "error": "Campo 'nombre' requerido"
}
```

**Error de servidor**:
```json
{
  "success": false,
  "error": "Error interno del servidor"
}
```
