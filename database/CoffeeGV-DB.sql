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
    id_trabajador INT NOT NULL,

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
    descripcion VARCHAR(255),
    precio DECIMAL(10,2) NOT NULL,
    categoria VARCHAR(50),
    stock INT DEFAULT 0,
    id_local INT NOT NULL,

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