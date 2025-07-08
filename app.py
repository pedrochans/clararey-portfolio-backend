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
        msg['To'] = 'clarareigle5@gmail.com'
        msg['Reply-To'] = email
        msg['Subject'] = f"Portfolio: Mensaje de {nombre} {apellido}"
        
        # HTML del email
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333; border-bottom: 2px solid #007bff;">
                Nuevo mensaje desde tu Portfolio
            </h2>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Nombre:</strong> {nombre} {apellido}</p>
                <p><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
            </div>
            <div style="margin: 20px 0;">
                <h3>Mensaje:</h3>
                <div style="background: white; padding: 15px; border-left: 4px solid #007bff;">
                    <p style="white-space: pre-wrap;">{mensaje}</p>
                </div>
            </div>
            <hr>
            <p style="font-size: 12px; color: #666; text-align: center;">
                Enviado desde el formulario de contacto del portfolio
            </p>
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

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
