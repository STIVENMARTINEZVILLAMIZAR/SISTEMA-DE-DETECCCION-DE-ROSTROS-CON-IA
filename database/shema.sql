CREATE DATABASE IF NOT EXISTS seguridad_facial CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE seguridad_facial;

CREATE TABLE empresas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL, -- login
    password_hash VARCHAR(255) NOT NULL,
    notify_email VARCHAR(100) DEFAULT NULL, -- correo para alertas
    notify_phone VARCHAR(40) DEFAULT NULL,  -- número internacional sin +
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE personas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    cargo VARCHAR(100),
    employee_id VARCHAR(80),
    empresa_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE
);

CREATE TABLE face_embeddings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT NOT NULL,
    model VARCHAR(50) DEFAULT 'Facenet512',
    embedding LONGTEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES personas(id) ON DELETE CASCADE
);

CREATE TABLE eventos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    persona_id INT NULL,
    label VARCHAR(150),
    es_desconocido BOOLEAN DEFAULT FALSE,
    similarity FLOAT NULL,
    camera VARCHAR(120) DEFAULT 'CAM1',
    snapshot LONGBLOB NULL,
    empresa_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (persona_id) REFERENCES personas(id) ON DELETE SET NULL,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE
);
