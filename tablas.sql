DROP TABLE IF EXISTS public.solicitudes;
DROP TABLE IF EXISTS public.destinos;
DROP TABLE IF EXISTS public.ciudades;
DROP TABLE IF EXISTS public.preferencias;
DROP TABLE IF EXISTS public.hoteles;
DROP TABLE IF EXISTS public.puntuaciones;
DROP TABLE IF EXISTS public.asignaciones;


-- Table: "Solicitudes"
CREATE TABLE public.solicitudes
(
    solicitud_id bigint PRIMARY KEY,
    nombre varchar(50),
    apellidos varchar(60),
    edad smallint,
    provincia_residente varchar(50),
    telefono varchar(50),
    discapacidad boolean,
    seguridad_social varchar(50),
    soltero_o_viudo boolean,
    vive_en_residencia boolean,
    viajara_con_acompanante boolean,
    acceso_transporte boolean,
    imserso_anopasado boolean,
    imserso_2021 boolean,
    importe_pension smallint,
    porcentaje_discapacidad smallint
);

-- Table: "destinos"
CREATE TABLE public.destinos
(
    tipo_destino_id smallint PRIMARY KEY,
    tipo_destino varchar(25),
    duracion varchar(15)
);

-- Table: "ciudades"
CREATE TABLE public.ciudades
(
    ciudades_id bigint PRIMARY KEY,
    ciudad varchar(40),
    tipo_destino_id smallint,
    FOREIGN KEY (tipo_destino_id) REFERENCES destinos(tipo_destino_id)
);


-- Table: "preferencias"
CREATE TABLE public.preferencias
(
    preferencias_id bigint PRIMARY KEY,
    opcion_1 varchar(40),
    opcion_2 varchar(40),
    opcion_3 varchar(40),
    opcion_4 varchar(40),
    opcion_5 varchar(40),
    opcion_id_1 bigint,
    opcion_id_2 bigint,
    opcion_id_3 bigint,
    opcion_id_4 bigint,
    opcion_id_5 bigint,
    solicitud_id bigint,
    FOREIGN KEY (opcion_id_1) REFERENCES ciudades(ciudades_id),
    FOREIGN KEY (opcion_id_2) REFERENCES ciudades(ciudades_id),
    FOREIGN KEY (opcion_id_3) REFERENCES ciudades(ciudades_id),
    FOREIGN KEY (opcion_id_4) REFERENCES ciudades(ciudades_id),
    FOREIGN KEY (opcion_id_5) REFERENCES ciudades(ciudades_id),
    FOREIGN KEY (solicitud_id) REFERENCES solicitudes(solicitud_id)
);


-- Table: "hoteles"
CREATE TABLE public.hoteles
(
    hotel_id bigint PRIMARY KEY,
    hotel varchar(60),
    plazas smallint,
    ciudad varchar(40),
    ciudades_id bigint,
    FOREIGN KEY (ciudades_id) REFERENCES ciudades(ciudades_id)
);


-- Table: "puntuaciones"
CREATE TABLE public.puntuaciones
(
    solicitud_id bigint PRIMARY KEY,
    nombre varchar(50),
    apellidos varchar(60),
    puntaje smallint,
    FOREIGN KEY (solicitud_id) REFERENCES solicitudes(solicitud_id)
);


-- Table: "asignaciones"
CREATE TABLE public.asignaciones
(
    solicitud_id bigint PRIMARY KEY,
    nombre varchar(50),
    apellidos varchar(60),
    puntaje smallint,
    hotel_asignado_1 varchar(150),
    hotel_asignado_2 varchar(150),
    FOREIGN KEY (solicitud_id) REFERENCES solicitudes(solicitud_id),
    FOREIGN KEY (puntaje) REFERENCES puntuaciones(puntaje)
);

