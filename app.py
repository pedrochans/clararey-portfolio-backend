import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import re
import logging

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configurar CORS para permitir requests desde tu frontend
CORS(app, origins=[
    "https://clara-portfolio.netlify.app",  # Tu dominio de producción si usas Netlify
    "http://localhost:3000",  # Para desarrollo local
    "http://127.0.0.1:3000",  # Para desarrollo local
    "file://"  # Para archivos locales
])

# Configuración de email
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = os.getenv('EMAIL_USER')  # Tu email de Gmail
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')  # Tu contraseña de aplicación de Gmail
EMAIL_RECIPIENT = 'clarareigle5@gmail.com'  # Email donde recibirás los mensajes

def validate_email(email):
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(text):
    """Limpiar input del usuario"""
    if not text:
        return ""
    text = str(text).strip()
    return text[:1000]  # Limitar longitud

def send_email(nombre, apellido, email, mensaje):
    """Enviar email con los datos del formulario"""
    try:
        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_RECIPIENT
        msg['Reply-To'] = email
        msg['Subject'] = f"Nuevo mensaje del portfolio - {nombre} {apellido}"
        
        # Cuerpo del email en HTML
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                    Nuevo mensaje desde tu Portfolio
                </h2>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p><strong style="color: #2c3e50;">Nombre:</strong> {nombre} {apellido}</p>
                    <p><strong style="color: #2c3e50;">Email:</strong> 
                        <a href="mailto:{email}" style="color: #3498db;">{email}</a>
                    </p>
                </div>
                
                <div style="margin: 20px 0;">
                    <h3 style="color: #2c3e50;">Mensaje:</h3>
                    <div style="background-color: #ffffff; padding: 20px; border-left: 4px solid #3498db; margin: 10px 0;">
                        <p style="margin: 0; white-space: pre-wrap;">{mensaje}</p>
                    </div>
                </div>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="font-size: 12px; color: #666; text-align: center;">
                    Este mensaje fue enviado desde el formulario de contacto de tu portfolio web.
                </p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        
        # Crear conexión segura y enviar email
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
            
        logger.info(f"Email enviado exitosamente desde {email}")
        return True
    except Exception as e:
        logger.error(f"Error enviando email: {str(e)}")
        return False

@app.route("/")
def home():
    return {
        "message": "Backend del Portfolio de Clara Rey",
        "status": "funcionando correctamente",
        "version": "1.0",
        "endpoints": {
            "contact": "/contact (POST)",
            "health": "/health (GET)"
        }
    }

@app.route("/contact", methods=['POST', 'OPTIONS'])
def contact():
    """Endpoint para manejar el formulario de contacto"""
    # Manejar preflight CORS request
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # Verificar que sea una petición POST con JSON
        if not request.is_json:
            return jsonify({
                "success": False,
                "message": "Content-Type debe ser application/json"
            }), 400
        
        data = request.get_json()
        
        # Validar que todos los campos requeridos estén presentes
        required_fields = ['nombre', 'apellido', 'email', 'mensaje']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False,
                    "message": f"El campo '{field}' es requerido"
                }), 400
        
        # Obtener y limpiar datos
        nombre = sanitize_input(data.get('nombre'))
        apellido = sanitize_input(data.get('apellido'))
        email = sanitize_input(data.get('email'))
        mensaje = sanitize_input(data.get('mensaje'))
        
        # Validar email
        if not validate_email(email):
            return jsonify({
                "success": False,
                "message": "El formato del email no es válido"
            }), 400
        
        # Validar longitud de campos
        if len(nombre) < 2 or len(apellido) < 2:
            return jsonify({
                "success": False,
                "message": "Nombre y apellido deben tener al menos 2 caracteres"
            }), 400
        
        if len(mensaje) < 10:
            return jsonify({
                "success": False,
                "message": "El mensaje debe tener al menos 10 caracteres"
            }), 400
        
        # Verificar configuración de email
        if not EMAIL_USER or not EMAIL_PASSWORD:
            logger.error("Variables de entorno EMAIL_USER o EMAIL_PASSWORD no configuradas")
            return jsonify({
                "success": False,
                "message": "Servicio de email no configurado correctamente"
            }), 500
        
        # Enviar email
        if send_email(nombre, apellido, email, mensaje):
            return jsonify({
                "success": True,
                "message": "¡Mensaje enviado correctamente! Te responderé pronto."
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Error al enviar el mensaje. Por favor, intenta más tarde."
            }), 500
            
    except Exception as e:
        logger.error(f"Error en endpoint contact: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500

@app.route("/health")
def health():
    """Endpoint de salud para Render"""
    return {"status": "healthy", "service": "portfolio-backend"}, 200

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
