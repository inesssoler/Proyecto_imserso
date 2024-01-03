> # **Data Project 1**
Este repositorio contiene toda la información del primer Data Project grupal del máster. El grupo está compuesto por Balma Agost, Borja Cabo, Javier Ruíz, Luis Segura e Inés Soler.

# Objetivos
El objetivo principal del proyecto es modernizar y hacer más justo el proceso de asignación de las plazas de hoteles ofrecidas por el Imserso. 
Para ello, hemos creado un sistema de puntuaciones basado en distintas variables que asignan mayor o menor preferencia a cada individuo a la hora de elegir plaza.

# Datos Utilizados
A continuación se pueden ver todos los datos que hemos utilizado y sus características.

| TABLA | VARIABLE | DESCRIPCIÓN | TIPO DE DATO | 
| ----- | -------- | ----------- | ------------ | ------ |
| Solicitudes | solicitud_id | ID de solicitud individual. | bigint |
| Solicitudes | nombre | Nombre de cada solicitante. | varchar(50) |
| Solicitudes | apellidos | Apellidos de cada solicitante. | text |
| Solicitudes | edad | Edad del solicitante. | smallint |
| Solicitudes | provincia_residente | Provincia de residencia del solicitante. | varchar(50) |
| Solicitudes | telefono | Teléfono de contacto del solicitante. | varchar(50) |
| Solicitudes | discapacidad | ¿Tiene alguna discapacida? | boolean |
| Solicitudes | porcentaje_discapacidad | Porcentaje de discapacidad (en caso de tener). | smallint |
| Solicitudes | seguridad_social | Número de la seguridad social del solicitante. | varchar(50) |
| Solicitudes | soltero_o_viudo | ¿El solicitante es soltero o viudo? |boolean |
| Solicitudes | vive_en_residencia | ¿Vive en una residencia de mayores? | boolean |
| Solicitudes | viajara_con_acompanante | ¿Viajará acompañado el solicitante? | boolean |
| Solicitudes | accesotransp | ¿Tiene acceso a transporte público o privado? | 
| Solicitudes | viaje2022 | ¿Viajó con el programa del imserso en el periodo anterior (2022)? | boolean |
| Solicitudes | viaje2021 | ¿Viajó con el programa del imserso en el año 2021? | boolean |
| Solicitudes | pension | Importe de la pensión mensual que recibe el solicitante. | smallint |
| Tdestino | tipo_destino | Tipo de destino: insular, peninsular o de escapada. | smallint |
| Tdestino | duracion | Duración de cada viaje según el tipo de destino al que corresponda. | text |
| Destinos | indice | ID de destino individual. | bigint |
| Destinos | destino | Ciudad de destino. | text |
| Destinos | tipo_destino | Unión con la tabla 'Tipo de destino'. | smallint |
| Preferencias | solicitud_id | ID de solicitud, correspondiente a la tabla 'Solicitudes' | bigint |
| Preferencias | opcion1 | Primera opción de destino del solicitante. | text |
| Preferencias | opcion2 | Segunda opción de destino del solicitante. | text |
| Preferencias | opcion3 | Tercera opción de destino del solicitante. | text |
| Preferencias | opcion4 | Cuarta opción de destino del solicitante. | text |
| Preferencias | opcion5 | Quinta opción de destino del solicitante. | text |
| Hoteles | hotel_id | ID de cada hotel. | bigint |
| Hoteles | hotel | Nombre de los hoteles disponibles para los viajes del imserso. | text |
| Hoteles | ciudad | Ciudad donde se encuentra cada hotel. | text |




# Origen de los Datos
Los datos han sido creados mayoritariamente de forma aleatoria haciendo uso de la librería 'faker' y del módulo 'random' de Python.
De los datos creados aleatoriamente, los siguientes han sido delimitados basándonos en información real:
- La edad solo puede estar en el rango de 60 a 99 años.
- El importe de las pensiones está en el rango entre 480 y 3,000€, que es el rango real de las pensiones en España.
- El porcentaje de discapacidad contempla hasta el 85%, ya que con un porcentaje superior a este se considera que la persona no está capacitada para viajar.

Por otra parte, los datos referentes a los diferentes tipos de destino y las posibles ciudades de cada tipo han sido extraidas de la siguiente página web: [Programa de Turismo Social del IMSERSO](https://www.turismosocial.com/Nuestros-Destinos/Listado-destinos~~.html?tourCat=Costa-Insular).

Y finalmente, hemos obtenido los datos de los hoteles que actualmente participan en el programa del IMSERSO: [Lista de Hoteles](https://www.preferente.com/noticias-de-hoteles/imserso-lista-completa-de-los-235-hoteles-de-mundiplan-y-turismo-social-321200.html)

# Variables incluidas en el Sistema de Puntuaciones

# Modelo de datos
Tabla Solicitudes
solicitud_id (clave primaria)
nombre
apellidos
edad
provincia_residente
telefono
discapacidad
seguridad_social
soltero_o_viudo
vive_en_residencia
viajara_con_acompanante
acceso_transporte
imserso_anopasado
imserso_2021
importe_pension
porcentaje_discapacidad
Tabla Destinos
tipo_destino_id (clave primaria)
tipo_destino
duracion
Tabla Ciudades
ciudades_id (clave primaria)
ciudad
tipo_destino_id (clave foránea referenciando a la tabla Destinos)
Tabla Preferencias
preferencias_id (clave primaria)
opcion_1
opcion_2
opcion_3
opcion_4
opcion_5
opcion_id_1 (clave foránea referenciando a la tabla Ciudades)
opcion_id_2 (clave foránea referenciando a la tabla Ciudades)
opcion_id_3 (clave foránea referenciando a la tabla Ciudades)
opcion_id_4 (clave foránea referenciando a la tabla Ciudades)
opcion_id_5 (clave foránea referenciando a la tabla Ciudades)
solicitud_id (clave foránea referenciando a la tabla Solicitudes)
Tabla Hoteles
hotel_id (clave primaria)
hotel
plazas
ciudad
ciudades_id (clave foránea referenciando a la tabla Ciudades)
Este modelo refleja la estructura de las tablas y las relaciones entre ellas. La información se organiza de manera que puedes relacionar las preferencias con las ciudades, las ciudades con los destinos, y los hoteles con las ciudades. Además, las solicitudes están relacionadas con las preferencias. Cada tabla tiene una clave primaria única, y las claves foráneas se utilizan para establecer relaciones entre las tablas.

