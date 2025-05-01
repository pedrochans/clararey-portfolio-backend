import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
TO_EMAIL = 'chans_99@yahoo.es'

@app.route('/api/contact', methods=['POST'])
def contact_form():
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['nombre', 'apellido', 'email', 'mensaje']
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'error': 'Faltan campos requeridos'}), 400
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = f"Portfolio Clara Rey <{SMTP_USERNAME}>"
        msg['To'] = TO_EMAIL
        msg['Reply-To'] = data['email']
        msg['Subject'] = f"Nuevo mensaje de {data['nombre']} {data['apellido']}"
        
        # Email body
        email_body = f"""
        <html>
        <body>
            <h2>Nuevo mensaje desde el portfolio de Clara Rey</h2>
            <p><strong>Nombre:</strong> {data['nombre']} {data['apellido']}</p>
            <p><strong>Email:</strong> {data['email']}</p>
            <p><strong>Mensaje:</strong></p>
            <p>{data['mensaje']}</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(email_body, 'html'))
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully from {data['email']}")
        return jsonify({'success': True, 'message': 'Mensaje enviado con éxito'})
    
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
