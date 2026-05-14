CREATE DATABASE CoffeeGoodVibes;
USE CoffeeGoodVibes;

CREATE TABLE Usuario (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL,
    telefono VARCHAR(15)
);

CREATE TABLE Local (
    id_local INT PRIMARY KEY AUTO_INCREMENT,
    nombre_local VARCHAR(100) NOT NULL,
    direccion VARCHAR(200) NOT NULL,
    telefono VARCHAR(15)
);

CREATE TABLE Cliente (
    id_cliente INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT UNIQUE NOT NULL,

    FOREIGN KEY (id_usuario)
        REFERENCES Usuario(id_usuario)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
CREATE TABLE Trabajador (
    id_trabajador INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT UNIQUE NOT NULL,
    puesto VARCHAR(50),
    salario DECIMAL(10 , 2 ),
    id_local INT NOT NULL,
    FOREIGN KEY (id_usuario)
        REFERENCES Usuario (id_usuario)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (id_local)
        REFERENCES Local (id_local)
        ON DELETE RESTRICT ON UPDATE CASCADE
);
CREATE TABLE TarjetaPuntos (
    id_tarjeta INT PRIMARY KEY AUTO_INCREMENT,
    puntos INT DEFAULT 0,
    fecha_creacion DATE,
    id_cliente INT UNIQUE NOT NULL,

    FOREIGN KEY (id_cliente)
        REFERENCES Cliente(id_cliente)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
CREATE TABLE TarjetaTrabajador (
    id_tarjeta_trabajador INT PRIMARY KEY AUTO_INCREMENT,
    codigo VARCHAR(50) UNIQUE,
    fecha_emision DATE,
    id_trabajador INT UNIQUE NOT NULL,

    FOREIGN KEY (id_trabajador)
        REFERENCES Trabajador(id_trabajador)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
CREATE TABLE Orden (
    id_orden INT PRIMARY KEY AUTO_INCREMENT,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10,2) NOT NULL,
    estado VARCHAR(30) DEFAULT 'Pendiente',
    id_cliente INT NOT NULL,
    id_trabajador INT NULL,

    FOREIGN KEY (id_cliente)
        REFERENCES Cliente(id_cliente)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    FOREIGN KEY (id_trabajador)
        REFERENCES Trabajador(id_trabajador)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE Producto (
    id_producto INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    tamano VARCHAR(10),
    descripcion VARCHAR(255),
    precio DECIMAL(10,2) NOT NULL,
    precio_puntos INT,
    categoria VARCHAR(50),
    stock INT DEFAULT 0,
    id_local INT NOT NULL,
    imagen_url VARCHAR(255) DEFAULT 'default_cafe.png',

    FOREIGN KEY (id_local)
        REFERENCES Local(id_local)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);



CREATE TABLE DetalleOrden (
    id_detalle INT PRIMARY KEY AUTO_INCREMENT,
    id_orden INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (id_orden)
        REFERENCES Orden(id_orden)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY (id_producto)
        REFERENCES Producto(id_producto)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);


CREATE TABLE Promocion (
    id_promocion INT PRIMARY KEY AUTO_INCREMENT,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    descuento_porcentaje DECIMAL(5,2),
    activo BOOLEAN DEFAULT TRUE
);


INSERT INTO Local (nombre_local, direccion, telefono) 
VALUES ('Good Vibes Centro', 'Av. Universidad 123', '6561234567');

INSERT INTO Producto (nombre, descripcion, precio, categoria, stock, id_local, tamano, precio_puntos) 
VALUES 
('Café Expreso', 'Intenso y aromático', 23.00, 'Calientes', 100, 1, 'Ch', 500),
('Shaky Coffee', 'Café helado con espuma', 70.00, 'Fríos', 50, 1, 'G', 1200),
('Brown Sugar Expresso', 'Intenso y dulce', 59.30, 'Frios', 3, 1, 'G', 460);

ALTER TABLE Producto ADD COLUMN imagen_url VARCHAR(255) DEFAULT 'default_cafe.png';
UPDATE Producto SET imagen_url = 'frapuchino.png' WHERE id_producto = 3;
