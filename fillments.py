# TABLA SOLICITUDES

import random
from faker import Faker
import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text 
from config import config


# Adapta la librería 'Faker' al español castellano con nombres en dicho idioma
fake = Faker('es_ES')

# Cantidad de solicitantes a generar
num_registros = 1000

base_de_datos = []

# Crea los registros de forma individual
for _ in range(num_registros):
    datos = {
        'solicitud_id': _ + 1,
        'nombre': fake.first_name(),
        'apellidos': fake.last_name(),
        'edad': random.randint(60, 99),
        'provincia_residente': fake.state(),
        'telefono': fake.phone_number(),
        'discapacidad': fake.boolean(),
        'seguridad_social': fake.ssn(),
        'soltero_o_viudo': fake.boolean(),
        'vive_en_residencia': fake.boolean(),
        'viajara_con_acompanante': fake.boolean(),
        'acceso_transporte': fake.boolean(),
        'imserso_anopasado': fake.boolean(),
        'imserso_2021': fake.boolean(),
        'importe_pension': round(random.uniform(480, 3000))
    }
    if datos['discapacidad'] == True:
        datos['porcentaje_discapacidad'] = round(random.uniform(1, 85))
    else:
        datos['porcentaje_discapacidad'] = 0
    
    # Añade los registros a la lista
    base_de_datos.append(datos)

# Crea un DataFrame a partir de la lista
solicitudes_df = pd.DataFrame(base_de_datos)


#Tabla 'destinos'
tipos_todos = []

tipo_insular = {
    'tipo_destino_id': 1,
    'tipo_destino': 'Costa Insular',
    'duracion': '8-10 días'
}
tipo_peninsular = {
    'tipo_destino_id': 2,
    'tipo_destino': 'Costa Peninsular',
    'duracion': '8-10 días'
}

tipo_escapada = {
    'tipo_destino_id': 3,
    'tipo_destino': 'Turismo de Escapada',
    'duracion': '4-5 días'
}

tipos_todos.append(tipo_insular)
tipos_todos.append(tipo_peninsular)
tipos_todos.append(tipo_escapada)

tipo_destinos_df = pd.DataFrame(tipos_todos)




#TABLA 'ciudades'

ciudades_todas=[]

costa_peninsular = ['Benidorm', 'Torrevieja', 'Denia', 'Jávea', 'El Albir', 'Calpe', 'Peñíscola', 'Benicassim', 'Vinaros', 'Gandía', 'Alboraya', 'Cullera', 'La Manga', 'Roquetas del Mar', 'Mojacar', 'Almuñécar', 'Matalascañas', 'Punta Umbría', 'Torremolinos', 'Marbella', 'Fuengirola', 'Benalmádena', 'Cadiz', 'Calella', 'Pineda del Mar', 'Santa Susana', 'Lloret del Mar', 'Salou', 'Cambrils', 'Comarruga', 'Finestrat', 'Altea', 'Elche', 'Murcia', 'Los Urrutias', 'Aguadulce', 'Isla Antilla', 'Isla Cristina', 'Isla Canela', 'Estepona', 'Conil De La Frontera', 'Chiclana De La Frontera', 'Puerto De Santa María', 'Chipiona', 'Mataro', 'Malgrat De Mar', 'Tossa De Mar', 'Platja DAro', 'San Carlos de la Rapita', 'La Pineda-Vilaseca', 'Miami Platja']

costa_insular = ['Puerto de Alcudia', 'Playa de Muro', 'Palmanova', 'El Arenal', 'Magaluf', 'Cala Rajada', 'Mercadal', 'Ciudadela', 'Punta Prima', 'Santa Eulalia', 'Es Canar', 'San Antonio', 'San Carlos', 'Puerto Rico', 'Las Palmas D.G.C.', 'Playa Del Inglés', 'Maspalomas', 'Costa Teguise', 'Puerto de la Cruz', 'Las Caletillas', 'Los Realejos', 'San Miguel De Abona', 'Costa Calma', 'Caleta De Fuste', 'Pajara', 'Fuerteventura']

escapada = ['Madrid', 'San Lorenzo del Escorial', 'Pinto', 'Aranjuez', 'Huesca', 'Teruel', 'Zaragoza', 'Oviedo', 'Gijón', 'Cabuérniga', 'Ciudad Real', 'Cuenca', 'Guadalajara', 'Toledo', 'Albacete', 'Ávila', 'Burgos', 'Zamora', 'Soria', 'Segovia', 'Salamanca', 'Valladolid', 'Palencia', 'Suances', 'Torrelavega', 'Santander', 'Santoña', 'Can Pastilla', 'Almería', 'Granada', 'Mijas', 'Jerez', 'Jaén', 'Córdoba', 'Sevilla', 'Barcelona', 'Girona', 'Tarragona', 'Reus', 'Alicante', 'Valencia', 'Talavera De La Reina', 'León', 'Cáceres', 'Badajoz', 'Mérida', 'Orense', 'La Coruña', 'Lugo', 'Santiago De Compostela', 'Pamplona', 'San Sebastián', 'Bilbao', 'Eibar', 'Ceuta', 'Haro']

for ciudad in costa_insular:
    datos = {
        'ciudad': ciudad,
        'tipo_destino_id': 1
    }
    ciudades_todas.append(datos)

for ciudad in costa_peninsular:
    datos = {
        'ciudad': ciudad,
        'tipo_destino_id': 2
    }
    ciudades_todas.append(datos)

for ciudad in escapada:
    datos = {
        'ciudad': ciudad,
        'tipo_destino_id': 3
    }
    ciudades_todas.append(datos)

ciudades_df = pd.DataFrame(ciudades_todas)
ciudades_df['ciudades_id'] = ciudades_df.index

# TABLA PREFERENCIAS

personas = []
for i in range(1, 1001):
    preferencias_id = i
    ciudades_indices = random.sample(ciudades_df.index.tolist(), 5)
    ciudades_nombres = [ciudades_df.loc[idx, 'ciudad'] for idx in ciudades_indices]
    personas.append([preferencias_id] + ciudades_indices + ciudades_nombres)

# Crear un DataFrame con la lista de personas y los índices de ciudades
columnas = ['preferencias_id', 'ciudades_id_1', 'ciudades_id_2', 'ciudades_id_3', 'ciudades_id_4', 'ciudades_id_5',
            'ciudad_1', 'ciudad_2', 'ciudad_3', 'ciudad_4', 'ciudad_5']
df_preferencias = pd.DataFrame(personas, columns=columnas)


# Agregar la columna 'solicitud_id' con identificador único para cada solicitud
df_preferencias['solicitud_id'] = df_preferencias.index + 1



# TABLA HOTELES


hoteles =['Alua Bocaccio','Aluasun Continental Park','Aluason Torrenova','Caribbean Bay','Habana Bay','Linda','Mediterranean Bay','Palma Bay',
    'Ritort','Samos','Atlantic Park','Triton beach','Linda','Mll Mediterranean Bay Adults Only','Aguamarina I','Aguamarina II',
    'Cala Galdana','Sur Menorca','Almirante Ferragut','Atlantic','Coral Beach','Ereso','Es Pla','San Antonio','Invisa Figueral Resort','Invisa La Cala',
    'Altamadores','Altamar','Concorde','Occidental Las Canteras','Green Field','Koala Garden','Astoria','Blue Sea Costa Teguise Gardens','Alua Parque San Antonio',
    'Alua Tenerife','Aluasoul Orotava Valley','Catalonia Las Vegas','Checkin Concordia Playa','HC Hotel Magec','Marquesa','Parque Vacacional Eden',
    'Valle Orotava','Catalonia Punta del Rey','Panorámica Garden','Barceló Tenerife','Royal Suite','Chatur Costa Caleta','Hotel Royal Suite','Smy Tahona Fuerteventura',
    'Alua Golf Trinidad','Bahía Serena','Best Roquetas','Best Sabinal','El Palmeral','Best Mojacar','Ele Andarax','Portomagno',
    'Vertice Indalo Almeria','Chinasol','Toboso','Checkin Camino De Granada','Dunas de Doñana Golf Resort','Flamero','Gran Hotel del Coto','Pato Amarillo',
    'Ilunion Islantilla','Occidental Isla Cristina','Playacanela','Aluasoul Costa Málaga','Aluasun Costa Park','Marconfort Griego','Parasol Garden',
    'Puente Real','Aluasun Marbella Park','Globales Gardenia','Las Palmeras', 'Medplaya Bali','Medplaya Balmoral','Paraiso Beach','Ilunion Mijas',
    'Ilunion Calas De Conil','Ilunion Sancti Petri','Melia Atlantera','Puerto Sherry','Vertice Chipiona Mar','Nh Avenida Jerez','Condestable Iranzo',
    'Crisol Jardines De Córdoba','Exe Las Adelfas','Castillo','Catalonia Hispalis''Htop Amaika & Spa', 'Htop Calella Palace Family & Spa', 'Santa Mónica',
    'Htop Pineda Palace','Mercury','Ciudad de Mataro','Ibersol Sorra Dor', 'Luna Park Yoga & Spa','Exe Cristal Palace','Garbi Park', 
    'Gran Garbi', 'Htop Royal Star & Spa', 'Samba','Surf-Mar','Tossa Beach Center','Caleta Palace','Platja Park','Best Western P. Cmc Girona',
    'Best Da Vinci', 'Best Los Ángeles', 'Best Mediterráneo', 'Best San Diego', 'Calypso','Htop Molinos Park', 'Medplaya Pirámide Salou','Oasis Park',
    'Best Cambrils','La Rapita','Natura Park','Estival Park Silmar','Medplaya Pino Alto','Ciutat De Tarragona','Gaudi','Dominio de Benidorm con Acapulco', 'Benidorm East',
    'Brasil','Caballo de Oro','Cabana','Carlos I','Cuco','Dynastic' ,'Fiesta Park' ,'Gala Placidia' ,'Golden' ,'Gran Hotel Bali' ,'Jaime I',
    'Joya', 'Lido' ,'Los Álamos' ,'Magic Cristal Park' ,'Magic Rock Gardens' ,'Mareny Benidorm', 'Melina' ,'Mont Park' ,'Montesol' ,'Oasis Plaza', 
    'Olympus' ,'Port Vista Oro' ,'Poseidón Playa' , 'Poseidón Resort', 'Sol y Sombra' ,'Tropic Relax','Alone','Playas Torrevieja','Port Denia',
	'Villa Naranjo','Sun Palace Albir','Port Europa','Roca Esmeralda','Cap Negret' ,'Port Elche' ,'Port Alicante' ,'Aparthotel & Spa Acualandia', 
    'Gran Hotel Peñíscola', 'Aparthotel & Spa Acuazul', 'RH Casablanca Suites' , 'RH Don Carlos & Spa','Intur Orange' ,'RH Vinarós Playa' ,
    'Porto','RH Bayren Park','RH Gijón','Safari','Tres Anclas','Villa Luz','Sicania','Olympia','Port Feria','La Mirage','Aluason Doblemar',
    'Entremares','Izan Cavanna','Occidental Mar Menor','Allegro Murcia Azarbe','Miranda Suizo','Florida','Villa De Pinto','Equo Aranjuez','Axor Feria',
    'Pedro I De Aragon','Rey Sancho Ramírez','Albarracín','Civera','Reina Cristina','Mora','Eurostars Zaragoza','Eurostars Boston',
    'Exe Oviedo Centro','Arbeyal','Arha Villa De Suances','Torresport','Arha Santander','Arha Villa de Santoña','Arha Reserva Del Saja','Nh Ciudad Real',
    'Exe Cuenca', 'Guadalajara & Conference Center','Perales','Be Live City Center Talavera','Eurostars Toledo','Reina Victoria','Cuatro Postes',
    'Puerta De Gredos','Exe Puerta de Burgos','Corona de Castilla','Rey Arturo','Alda Mercado De Zamora','Alfonso Viii Soria','Ele Acueducto',
    'Leon Camino','Olid','Rey Sancho','Gran Hotel Corona Sol','Extremadura Hotel','Ilunion Golf Badajoz','Gran Hotel Corona Sol','Exe Auriense',
    'Exe Coruña','Mendez Nuñez','Ciudad De Compostela','Sancho Ramirez','Barcelo Costa Vasca','Occidental Bilbao','Unzaga Plaza','Ceuta Puerta De Africa','Ciudad De Haro'
]
lista_ciudades = ['Puerto de Alcudia', 'Playa de Muro', 'Palmanova', 'El Arenal', 'El Arenal', 'El Arenal', 'El Arenal', 'El Arenal',
    'Magaluf', 'Magaluf', 'Cala Rajada', 'Can Pastilla', 'El Arenal', 'Mercadal', 'Mercadal', 'Ciudadela', 'Punta Prima', 'Ciudadela',
    'Santa Eulalia', 'Es Canar', 'Es Canar', 'San Antonio', 'San Carlos', 'Santa Eulalia', 'Puerto Rico', 'Puerto Rico',
    'Las Palmas D.G.C.', 'Las Palmas D.G.C.', 'Playa Del Inglés', 'Maspalomas', 'Las Palmas D.G.C.', 'Costa Teguise',
    'Puerto de la Cruz', 'Puerto de la Cruz', 'Puerto de la Cruz', 'Puerto de la Cruz', 'Puerto de la Cruz',
    'Puerto de la Cruz', 'Puerto de la Cruz', 'Puerto de la Cruz', 'Puerto de la Cruz', 'Las Caletillas', 'Los Realejos',
    'San Miguel De Abona', 'Costa Calma', 'Caleta De Fuste', 'Pajara', 'Fuerteventura', 'Roquetas del Mar',
    'Roquetas del Mar', 'Roquetas del Mar', 'Roquetas del Mar', 'Roquetas del Mar', 'Mojacar', 'Aguadulce', 'Aguadulce',
    'Almería', 'Almuñécar', 'Almuñécar', 'Granada', 'Matalascañas', 'Matalascañas', 'Matalascañas', 'Punta Umbría',
    'Isla Antilla', 'Isla Cristina', 'Isla Canela', 'Torremolinos', 'Torremolinos', 'Torremolinos', 'Torremolinos',
    'Torremolinos', 'Marbella', 'Fuengirola', 'Fuengirola', 'Benalmádena', 'Benalmádena', 'Estepona', 'Mijas',
    'Conil De La Frontera', 'Chiclana De La Frontera', 'Cadiz', 'Puerto De Santa María', 'Chipiona', 'Jerez', 'Jaén',
    'Córdoba', 'Córdoba', 'Córdoba', 'Sevilla', 'Calella', 'Calella', 'Calella', 'Pineda del Mar', 'Santa Susana',
    'Mataro', 'Malgrat De Mar', 'Malgrat De Mar', 'Barcelona', 'Lloret del Mar', 'Lloret del Mar', 'Lloret del Mar',
    'Lloret del Mar', 'Lloret del Mar','Tossa De Mar', 'Platja DAro', 'Platja DAro', 'Girona', 'Salou', 'Salou', 'Salou', 'Salou',
    'Salou', 'Salou', 'Salou', 'Salou', 'Cambrils', 'San Carlos de la Rapita', 'Comarruga', 'La Pineda-Vilaseca',
    'Miami Platja', 'Tarragona', 'Reus', 'Benidorm', 'Benidorm', 'Benidorm', 'Benidorm', 'Benidorm', 'Benidorm',
    'Benidorm', 'Benidorm', 'Benidorm', 'Benidorm', 'Benidorm', 'Benidorm', 'Benidorm', 'Benidorm', 'Benidorm',
    'Benidorm', 'Benidorm', 'Benidorm', 'Benidorm', 'Benidorm', 'Benidorm', 'Benidorm', 'Benidorm', 'Benidorm',
    'Benidorm', 'Benidorm', 'Benidorm', 'Benidorm', 'Benidorm',
    'Finestrat', 'Torrevieja', 'Denia', 'Jávea', 'El Albir', 'Calpe', 'Calpe',
    'Altea', 'Elche', 'Alicante', 'Peñíscola', 'Peñíscola', 'Peñíscola', 'Peñíscola', 'Peñíscola', 'Benicassim',
    'Vinaros', 'Gandía', 'Gandía', 'Gandía', 'Gandía', 'Gandía', 'Gandía', 'Cullera', 'Alboraya', 'Valencia', 'Murcia', 'La Manga',
    'La Manga', 'La Manga', 'Los Urrutias', 'Murcia', 'San Lorenzo del Escorial', 'San Lorenzo del Escorial', 'Pinto',
    'Aranjuez', 'Madrid', 'Huesca', 'Huesca', 'Teruel', 'Teruel', 'Teruel', 'Teruel', 'Zaragoza', 'Zaragoza',
    'Oviedo', 'Gijón', 'Suances', 'Torrelavega', 'Santander', 'Santoña', 'Cabuérniga', 'Ciudad Real', 'Cuenca',
    'Guadalajara', 'Toledo', 'Toledo', 'Toledo', 'Talavera De La Reina', 'Albacete', 'Ávila', 'Ávila', 'Burgos',
    'Burgos', 'Burgos', 'Zamora', 'Soria', 'Segovia', 'León', 'Valladolid', 'Palencia', 'Salamanca', 'Cáceres',
    'Badajoz', 'Mérida', 'Orense', 'La Coruña', 'Lugo', 'Santiago De Compostela', 'Pamplona', 'San Sebastián',
    'Bilbao', 'Eibar', 'Ceuta', 'Haro'
]

hoteles_df = pd.DataFrame()
hoteles_df['hotel'] = hoteles
hoteles_df['ciudad'] = lista_ciudades
hoteles_df['hotel_id'] = hoteles_df.index
hoteles_df['plazas'] = random.randint(130, 220)

hoteles_df['ciudades_id'] = 0  # Inicializa la columna ciudades_id

# Iterar sobre cada fila en hoteles_df para asignar el ciudades_id correspondiente
for index, row in hoteles_df.iterrows():
    ciudad_actual = row['ciudad']
    
    # Buscar el ciudades_id correspondiente en ciudades_df según el nombre de la ciudad
    ciudades_id = ciudades_df.loc[ciudades_df['ciudad'] == ciudad_actual, 'ciudades_id'].values
    
    # Asignar el ciudades_id encontrado a la fila correspondiente en hoteles_df
    if len(ciudades_id) > 0:
        hoteles_df.at[index, 'ciudades_id'] = ciudades_id[0]



# CONEXION E INSERCIÓN DE LOS DATOS

try:
    connection = psycopg2.connect(
        host=config['host'],
        database=config['database'],
        user=config['user'],
        password=config['password']
    )

    cursor = connection.cursor()

    # Inserta la tabla 'solicitudes'
    for datos in solicitudes_df.itertuples(index=False):
        insert_query = """
        INSERT INTO public.solicitudes 
        (solicitud_id, nombre, apellidos, edad, provincia_residente, telefono, discapacidad, seguridad_social, soltero_o_viudo, vive_en_residencia, viajara_con_acompanante, acceso_transporte, imserso_anopasado, imserso_2021, importe_pension, porcentaje_discapacidad)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING;  -- Evita duplicados
        """

        cursor.execute(insert_query, (
            datos.solicitud_id,
            datos.nombre,
            datos.apellidos,
            datos.edad,
            datos.provincia_residente,
            datos.telefono,
            datos.discapacidad,
            datos.seguridad_social,
            datos.soltero_o_viudo,
            datos.vive_en_residencia,
            datos.viajara_con_acompanante,
            datos.acceso_transporte,
            datos.imserso_anopasado,
            datos.imserso_2021,
            datos.importe_pension,
            datos.porcentaje_discapacidad
        ))

    # Inserta la tabla 'destinos'
    for destinos in tipo_destinos_df.itertuples(index=False):
        insert_destinos_query = """
        INSERT INTO public.destinos 
        (tipo_destino_id, tipo_destino, duracion)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING;  -- Evita duplicados
        """

        cursor.execute(insert_destinos_query, (
            destinos.tipo_destino_id,
            destinos.tipo_destino,
            destinos.duracion
        ))

    # Inserta la tabla 'ciudades'
    for ciudades in ciudades_df.itertuples(index=False):
        insert_ciudades_query = """
        INSERT INTO public.ciudades 
        (ciudades_id, ciudad, tipo_destino_id)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING;  -- Evita duplicados
        """

        cursor.execute(insert_ciudades_query, (
            ciudades.ciudades_id,
            ciudades.ciudad,
            ciudades.tipo_destino_id
        ))


    # Inserta la tabla 'preferencias'
    for preferencia in df_preferencias.itertuples(index=False):
        insert_preferencia_query = """
        INSERT INTO public.preferencias 
        (preferencias_id, opcion_1, opcion_2, opcion_3, opcion_4, opcion_5,
        opcion_id_1, opcion_id_2, opcion_id_3, opcion_id_4, opcion_id_5, solicitud_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING;  -- Evita duplicados
        """

        cursor.execute(insert_preferencia_query, (
            preferencia.preferencias_id,
            preferencia.ciudad_1,
            preferencia.ciudad_2,
            preferencia.ciudad_3,
            preferencia.ciudad_4,
            preferencia.ciudad_5,
            preferencia.ciudades_id_1,
            preferencia.ciudades_id_2,
            preferencia.ciudades_id_3,
            preferencia.ciudades_id_4,
            preferencia.ciudades_id_5,
            preferencia.solicitud_id
        ))



    # Inserta la tabla 'hoteles'
    for hotel in hoteles_df.itertuples(index=False):
        insert_hoteles_query = """
        INSERT INTO public.hoteles 
        (hotel_id, hotel, plazas, ciudad, ciudades_id)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING;  -- Evita duplicados
        """

        cursor.execute(insert_hoteles_query, (
            hotel.hotel_id,
            hotel.hotel,
            hotel.plazas,
            hotel.ciudad,
            hotel.ciudades_id
        ))

    # Guarda los cambios en la base de datos
    connection.commit()

except Exception as e:
    print(f"Error: {e}")

finally:
    # Cierra el cursor y la conexión
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals():
        connection.close()