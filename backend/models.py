# backend/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, TIMESTAMP, text, LargeBinary, Boolean, Text
from sqlalchemy.orm import relationship
from db import Base

class Empresa(Base):
    __tablename__ = 'empresas'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    notify_phone = Column(String(40), nullable=True)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    personas = relationship('Persona', back_populates='empresa')

class Persona(Base):
    __tablename__ = 'personas'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    cargo = Column(String(100))
    employee_id = Column(String(80))
    empresa_id = Column(Integer, ForeignKey('empresas.id'))
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    empresa = relationship('Empresa', back_populates='personas')
    embeddings = relationship('FaceEmbedding', back_populates='person', cascade='all, delete-orphan')

class FaceEmbedding(Base):
    __tablename__ = 'face_embeddings'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('personas.id'), nullable=False)
    model = Column(String(50), default='Facenet512')
    embedding = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    person = relationship('Persona', back_populates='embeddings')

class Evento(Base):
    __tablename__ = 'eventos'
    id = Column(Integer, primary_key=True)
    persona_id = Column(Integer, ForeignKey('personas.id'), nullable=True)
    label = Column(String(150))
    es_desconocido = Column(Boolean, default=False)
    similarity = Column(Float, nullable=True)
    camera = Column(String(120), default='CAM1')
    snapshot = Column(LargeBinary, nullable=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'))
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
