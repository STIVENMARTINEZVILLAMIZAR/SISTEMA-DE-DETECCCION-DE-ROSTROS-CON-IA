# backend/routes_events.py
from flask import Blueprint, jsonify, session, request, Response, render_template, redirect, url_for
from db import SessionLocal
from models import Evento
from sqlalchemy import desc

events_bp = Blueprint('events_bp', __name__, template_folder='../templates')

@events_bp.route('/events', methods=['GET'])
def events_page():
    if 'empresa_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('events.html')

@events_bp.route('/api/events', methods=['GET'])
def list_events():
    if 'empresa_id' not in session:
        return jsonify([]), 401
    empresa_id = session['empresa_id']
    s = SessionLocal()
    try:
        q = s.query(Evento).filter(Evento.empresa_id == empresa_id).order_by(desc(Evento.id)).limit(300).all()
        out = []
        for e in q:
            out.append({
                'id': e.id,
                'persona_id': e.persona_id,
                'label': e.label,
                'es_desconocido': e.es_desconocido,
                'similarity': e.similarity,
                'camera': e.camera,
                'created_at': str(e.created_at),
                'snapshot': f"/events/snapshot/{e.id}" if e.snapshot else None
            })
        return jsonify(out)
    finally:
        s.close()

@events_bp.route('/events/snapshot/<int:eid>')
def get_snapshot(eid):
    if 'empresa_id' not in session:
        return '', 401
    s = SessionLocal()
    try:
        e = s.get(Evento, eid)
        if not e or e.empresa_id != session['empresa_id'] or not e.snapshot:
            return '', 404
        return Response(e.snapshot, mimetype='image/jpeg')
    finally:
        s.close()
