from flask import Flask, render_template, session, redirect, url_for
from auth import auth_bp
from routes_people import people_bp
from routes_events import events_bp
from db import engine, Base
from config import SECRET_KEY
from detection import CameraWorker, mjpeg_generator
import os
from flask_session import Session

Base.metadata.create_all(bind=engine)

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '../templates'),
    static_folder=os.path.join(os.path.dirname(__file__), '../static')
)

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

app.register_blueprint(auth_bp)
app.register_blueprint(people_bp)
app.register_blueprint(events_bp)

# Guardar workers activos dinámicamente
workers = {}

@app.route('/')
def index():
    if 'empresa_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('index.html', empresa=session.get('empresa_nombre',''))

@app.route('/stream/<int:cam_id>')
def stream(cam_id):
    if cam_id not in workers:
        # crear worker solo si no existe
        workers[cam_id] = CameraWorker(source=cam_id, camera_name=f"CAM{cam_id}", empresa_id=None)
        workers[cam_id].start()

    worker = workers[cam_id]
    return app.response_class(
        mjpeg_generator(worker),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
