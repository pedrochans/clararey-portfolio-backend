import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import re

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configurar CORS para el frontend
CORS(app, origins=[
    "*"  # En producción, cambiar por dominios específicos
])

def validate_email(email):
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def send_email(nombre, apellido, email, mensaje):
    """Enviar email usando Gmail SMTP"""
    try:
        # Configuración desde variables de entorno
        smtp_user = os.getenv('EMAIL_USER')
        smtp_password = os.getenv('EMAIL_PASSWORD')
        
        if not smtp_user or not smtp_password:
            raise Exception("Variables de entorno EMAIL_USER o EMAIL_PASSWORD no configuradas")
        
        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = 'chans_99@yahoo.es'
        msg['Reply-To'] = email
        msg['Subject'] = f"Portfolio: Mensaje de {nombre} {apellido}"
        
        # HTML del email CON logo desde tu web
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f9f9f9;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <!-- Header con logo -->
                <div style="text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #eee;">
                    <img src="https://clararey-portfolio.vercel.app/img/00_logo_cr.jpg" alt="Clara Rey Logo" style="width: 80px; height: 80px; border-radius: 50%; margin-bottom: 15px; object-fit: cover; box-shadow: 0 2px 8px rgba(0,0,0,0.1); display: block; margin-left: auto; margin-right: auto;">
                    <h1 style="color: #333; margin: 0; font-size: 24px; font-weight: 300;">Clara Rey Portfolio</h1>
                    <p style="color: #666; margin: 5px 0 0 0; font-size: 14px;">Nuevo mensaje de contacto</p>
                </div>
                
                <h2 style="color: #333; margin-bottom: 20px; font-size: 20px;">
                    Mensaje de {nombre} {apellido}
                </h2>
                
                <div style="margin-bottom: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 5px;">
                    <p style="margin: 5px 0;"><strong>Nombre completo:</strong> {nombre} {apellido}</p>
                    <p style="margin: 5px 0;"><strong>Email de contacto:</strong> <a href="mailto:{email}" style="color: #007bff; text-decoration: none;">{email}</a></p>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; border-left: 4px solid #007bff;">
                    <h3 style="color: #333; margin-top: 0; font-size: 16px;">Mensaje:</h3>
                    <p style="color: #555; line-height: 1.6; white-space: pre-wrap; margin: 10px 0 0 0;">{mensaje}</p>
                </div>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                
                <div style="text-align: center;">
                    <p style="color: #666; font-size: 12px; margin: 0;">
                        Este mensaje fue enviado desde el formulario de contacto del portfolio de Clara Rey
                    </p>
                    <p style="color: #666; font-size: 12px; margin: 5px 0 0 0;">
                        Responde directamente a este email para contactar con {nombre}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Enviar email
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            
        return True
    except Exception as e:
        print(f"Error enviando email: {str(e)}")
        return False

@app.route("/")
def home():
    """Página de inicio del API"""
    return {
        "service": "Portfolio Clara Rey - Backend",
        "status": "active",
        "endpoints": {
            "POST /contact": "Enviar mensaje de contacto",
            "POST /api/contact": "Enviar mensaje de contacto (alternativo)",
            "GET /health": "Estado del servicio",
            "GET /api/health": "Estado del servicio (alternativo)"
        }
    }

@app.route("/contact", methods=['POST'])
def contact():
    """Endpoint para recibir mensajes del formulario"""
    try:
        # Verificar JSON
        if not request.is_json:
            return jsonify({"success": False, "error": "Formato JSON requerido"}), 400
        
        data = request.get_json()
        
        # Validar campos requeridos
        required = ['nombre', 'apellido', 'email', 'mensaje']
        for field in required:
            if not data.get(field, '').strip():
                return jsonify({"success": False, "error": f"Campo '{field}' requerido"}), 400
        
        # Limpiar datos
        nombre = data['nombre'].strip()[:100]
        apellido = data['apellido'].strip()[:100]
        email = data['email'].strip()[:200]
        mensaje = data['mensaje'].strip()[:2000]
        
        # Validaciones
        if len(nombre) < 2 or len(apellido) < 2:
            return jsonify({"success": False, "error": "Nombre y apellido muy cortos"}), 400
            
        if not validate_email(email):
            return jsonify({"success": False, "error": "Email inválido"}), 400
            
        if len(mensaje) < 10:
            return jsonify({"success": False, "error": "Mensaje muy corto (mín 10 caracteres)"}), 400
        
        # Enviar email
        if send_email(nombre, apellido, email, mensaje):
            return jsonify({"success": True, "message": "Mensaje enviado correctamente"})
        else:
            return jsonify({"success": False, "error": "Error al enviar mensaje"}), 500
            
    except Exception as e:
        print(f"Error en /contact: {str(e)}")
        return jsonify({"success": False, "error": "Error interno del servidor"}), 500

@app.route("/health")
def health():
    """Health check para Render"""
    return {"status": "healthy"}

# Rutas alternativas para compatibilidad con frontend
@app.route("/api/contact", methods=['POST'])
def api_contact():
    """Endpoint alternativo para el frontend (redirige a contact)"""
    return contact()

@app.route("/api/health")
def api_health():
    """Health check alternativo para el frontend"""
    return health()

def create_app():
    return app

# Soporte para gunicorn y ejecución directa
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    # Eliminar debug=True para reducir warnings en desarrollo
    app.run(host='0.0.0.0', port=port, debug=False)
