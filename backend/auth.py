# backend/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import SessionLocal, Base, engine
from models import Empresa
from sqlalchemy import select

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        notify_phone = request.form.get('notify_phone')  # opcional
        if not (nombre and email and password):
            flash("Llena todos los campos")
            return redirect(url_for('auth.register'))
        hash_pw = generate_password_hash(password)
        s = SessionLocal()
        try:
            q = s.execute(select(Empresa).where(Empresa.email == email)).scalars().first()
            if q:
                flash("Email ya registrado")
                return redirect(url_for('auth.register'))
            emp = Empresa(nombre=nombre, email=email, password_hash=hash_pw, notify_phone=notify_phone)
            s.add(emp)
            s.commit()
            flash("Registrado. Entra con tus credenciales.")
            return redirect(url_for('auth.login'))
        finally:
            s.close()
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        s = SessionLocal()
        try:
            emp = s.execute(select(Empresa).where(Empresa.email == email)).scalars().first()
            if emp and check_password_hash(emp.password_hash, password):
                session['empresa_id'] = emp.id
                session['empresa_nombre'] = emp.nombre
                return redirect(url_for('index'))
            flash("Credenciales inválidas")
            return redirect(url_for('auth.login'))
        finally:
            s.close()
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
