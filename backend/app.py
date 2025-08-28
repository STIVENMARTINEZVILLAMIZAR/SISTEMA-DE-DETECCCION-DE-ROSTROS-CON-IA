# backend/app.py
from flask import Flask, render_template, session, redirect, url_for
from auth import auth_bp
from routes_people import people_bp
from routes_events import events_bp
from db import engine, Base
from config import SECRET_KEY, CAMERA_SOURCE
from detection import CameraWorker, mjpeg_generator
import os
from flask_session import Session

# crear tablas
Base.metadata.create_all(bind=engine)

app = Flask(__name__, template_folder='../templates', static_folder='static')
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

app.register_blueprint(auth_bp)
app.register_blueprint(people_bp)
app.register_blueprint(events_bp)

# iniciar worker (empresa_id=None para demo) -> puedes cambiar para arrancar con empresa_id específica
camera_source = os.getenv('CAMERA_SOURCE', '0')
worker = CameraWorker(source=camera_source, camera_name='CAM1', empresa_id=None)
worker.start()

@app.route('/')
def index():
    if 'empresa_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('index.html', empresa=session.get('empresa_nombre',''))

@app.route('/stream')
def stream():
    return app.response_class(mjpeg_generator(worker), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
