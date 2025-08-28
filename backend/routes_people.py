# backend/routes_people.py
from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from db import SessionLocal
from models import Persona, FaceEmbedding
from face_recognition import compute_embedding
import numpy as np, json, cv2

people_bp = Blueprint('people_bp', __name__, template_folder='../templates')

@people_bp.route('/people', methods=['GET'])
def people_page():
    if 'empresa_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('people.html')

@people_bp.route('/api/people', methods=['GET'])
def list_people():
    if 'empresa_id' not in session:
        return jsonify([]), 401
    empresa_id = session['empresa_id']
    s = SessionLocal()
    try:
        rows = s.query(Persona).filter(Persona.empresa_id == empresa_id).all()
        out = []
        for p in rows:
            out.append({'id': p.id, 'nombre': p.nombre, 'cargo': p.cargo, 'employee_id': p.employee_id, 'embeddings': len(p.embeddings)})
        return jsonify(out)
    finally:
        s.close()

@people_bp.route('/api/people', methods=['POST'])
def create_person():
    if 'empresa_id' not in session:
        return jsonify({'ok': False}), 401
    data = request.json
    s = SessionLocal()
    try:
        p = Persona(nombre=data.get('nombre') or data.get('full_name'),
                    cargo=data.get('cargo'),
                    employee_id=data.get('employee_id'),
                    empresa_id=session['empresa_id'])
        s.add(p)
        s.commit()
        return jsonify({'ok': True, 'id': p.id})
    finally:
        s.close()

@people_bp.route('/api/people/<int:pid>/photo', methods=['POST'])
def upload_face(pid):
    if 'empresa_id' not in session:
        return jsonify({'ok': False}), 401
    if 'file' not in request.files:
        return jsonify({'ok': False, 'error': 'file missing'}), 400
    file = request.files['file']
    img_bytes = file.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    emb = compute_embedding(img)
    if emb is None:
        return jsonify({'ok': False, 'error': 'face not found'}), 400
    s = SessionLocal()
    try:
        p = s.get(Persona, pid)
        if not p or p.empresa_id != session['empresa_id']:
            return jsonify({'ok': False, 'error': 'person not found'}), 404
        fe = FaceEmbedding(person_id=p.id, embedding=json.dumps(list(emb)))
        s.add(fe)
        s.commit()
        return jsonify({'ok': True, 'embedding_id': fe.id})
    finally:
        s.close()
