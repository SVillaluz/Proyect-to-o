DROP SCHEMA subastas2;

CREATE DATABASE IF NOT EXISTS subastas2;

USE subastas2;

CREATE TABLE datos_personales (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    apellido_paterno VARCHAR(100),
    apellido_materno VARCHAR(100),
    fecha_nacimiento DATE,
    domicilio TEXT,
    telefono VARCHAR(20),
    correo_electronico VARCHAR(100),
    RFC VARCHAR(20),
    contraseña VARBINARY(256)
);


CREATE TABLE inventario (
    id_articulo INT AUTO_INCREMENT PRIMARY KEY,
    tipo_articulo ENUM('Joyería', 'Automóvil', 'Muebles', 'Pinturas', 'Casas'),
    descripcion TEXT,
    caracteristicas TEXT,
    valor_estimado_encriptado VARBINARY(255), -- Valor cifrado
    estado ENUM('Disponible', 'En Subasta', 'Subastado', 'Vendido', 'Retirado'),
    fecha_registro DATE
);

CREATE TABLE vendedores (
    id_vendedor INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50),
    apellido_paterno VARCHAR(50),
    apellido_materno VARCHAR(50),
    telefono VARCHAR(15),
    correo_electronico VARCHAR(100) UNIQUE,
    fecha_contratacion DATE,
    status ENUM('Activo', 'Inactivo'),
    fecha_registro DATE
);

CREATE TABLE ventas (
    id_venta INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT,
    id_inventario INT,
    id_formas_pago INT,
    fecha_venta DATE,
    FOREIGN KEY (id_cliente) REFERENCES datos_personales(id_cliente),
    FOREIGN KEY (id_vendedor) REFERENCES vendedores(id_vendedor),
    FOREIGN KEY (id_inventario) REFERENCES inventario(id_inventario),
    FOREIGN KEY (id_formas_pago) REFERENCES formas_pago(id_formas_pago)
);


CREATE TABLE formas_pago (
    id_pago INT AUTO_INCREMENT PRIMARY KEY,
    id_venta INT,
    id_cliente INT,
    precio_final DECIMAL(12,2),
    forma_pago ENUM('Transferencia', 'Tarjeta de crédito', 'Efectivo', 'Cheque'),
    fecha_pago DATE,
    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta),
    FOREIGN KEY (id_cliente) REFERENCES datos_personales(id_cliente)
);

CREATE TABLE entregas (
    id_entrega INT AUTO_INCREMENT PRIMARY KEY,
    id_venta INT,
    id_cliente INT,
    fecha_entrega DATE,
    hora_entrega TIME,
    direccion_entrega TEXT,
    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta),
    FOREIGN KEY (id_cliente) REFERENCES datos_personales(id_cliente)
);

