from flask import Flask, render_template, url_for, request, redirect, send_file, jsonify
import csv
import requests
import os
from datetime import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static')

# Setup CORS
CORS(app)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize security headers
Talisman(app,
         content_security_policy={
             'default-src': "'self'",
             'img-src': '*',
             'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
             'style-src': ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com'],
             'font-src': ["'self'", 'https://fonts.gstatic.com'],
         },
         force_https=False)

# Configuration
app.config.update(
    CSV_FILE=os.path.join('data', 'database.csv'),
    RESUME_PATH=os.path.join(
        'static', 'assets', 'docs', 'Kaustubh_Resume.pdf'),
    NTFY_SERVER=os.getenv('NTFY_SERVER', 'Kaustubh43_WebsiteAlerts')
)


@app.route('/')
def my_home():
    return render_template('index.html')


@app.route('/<string:page_name>')
def html_page(page_name):
    return render_template(page_name)


def write_to_csv(data):
    """Write form data to CSV with proper error handling"""
    try:
        os.makedirs('data', exist_ok=True)
        filepath = app.config['CSV_FILE']

        file_exists = os.path.exists(filepath)

        with open(filepath, newline='', mode='a') as database2:
            fieldnames = ['email', 'subject', 'message', 'timestamp']
            writer = csv.DictWriter(database2, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow({
                'email': data.get('email', ''),
                'subject': data.get('subject', ''),
                'message': data.get('message', ''),
                'timestamp': datetime.now().isoformat()
            })

        notify(data.get('email', ''), data.get(
            'subject', ''), data.get('message', ''))
        return True
    except Exception as e:
        app.logger.error(f"Error writing to CSV: {str(e)}")
        return False


def notify(email, subject, data):
    """Send push notifications with error handling"""
    try:
        server_name = app.config['NTFY_SERVER']
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data_received = {
            "message": f"Query from {email} regarding {subject}",
            "timestamp": timestamp,
            "query_details": data[:500]
        }

        response = requests.post(
            f"https://ntfy.sh/{server_name}",
            json=data_received,
            headers={
                "Title": "New Query Received",
                "Priority": "high",
                "Tags": "tada",
                "X-Request-Timestamp": timestamp
            },
            timeout=5
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Notification error: {str(e)}")
        return False


@app.route('/submit_form', methods=['POST', 'GET'])
@limiter.limit("5 per minute")
def submit_form():
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            if write_to_csv(data):
                return redirect('/thankyou.html')
            return 'Error saving to database', 500
        except Exception as e:
            app.logger.error(f"Form submission error: {str(e)}")
            return 'Error processing form', 500
    return 'Method not allowed', 405


@app.route('/download')
def downloadFile():
    try:
        path = app.config['RESUME_PATH']
        if not os.path.exists(path):
            return "Resume file not found", 404

        return send_file(
            path,
            as_attachment=True,
            download_name=f"Kaustubh_Resume_{datetime.now().strftime('%Y%m%d')}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        app.logger.error(f"Download error: {str(e)}")
        return "Error downloading file", 500


@app.route('/health')
def health_check():
    """Health check endpoint for Docker"""
    return jsonify({"status": "healthy"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
