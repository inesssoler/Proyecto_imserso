import pandas as pd
import numpy as np
import psycopg2
from faker import Faker
from sqlalchemy import create_engine
from config import config

# Conexión a la base de datos
'''
connection_params = {
    'dbname': config['database'],
    'user': config['user'],
    'password': config['password],
    'host': 'localhost',
    'port': '5432'
}
'''

engine = create_engine(f"postgresql+psycopg2://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}")

solicitudes_df = pd.read_sql('SELECT * FROM public.solicitudes', con=engine)
ciudades_df = pd.read_sql('SELECT * FROM public.ciudades', con=engine)
preferencias_df = pd.read_sql('SELECT * FROM public.preferencias', con=engine)
destino_df = pd.read_sql('SELECT * FROM public.destinos', con=engine)
hoteles_df = pd.read_sql('SELECT * FROM public.hoteles', con=engine)

#################################CRITERIOS DE PUNTUACIÓN#################################
def calcular_puntaje(solicitudes_df):
    puntaje = 0

    # Puntuación según la edad
    if 65 <= solicitudes_df['edad'] <= 75:
        puntaje += 10
    elif 76 <= solicitudes_df['edad'] <= 85:
        puntaje += 15
    elif solicitudes_df['edad'] > 86:
        puntaje += 20

    # Puntuación por estado civil
    puntaje += 10 if solicitudes_df['soltero_o_viudo'] else 0

    # Puntuación por vivir en residencia de mayores
    puntaje += 15 if solicitudes_df['vive_en_residencia'] else 0

    # Puntuación por discapacidad
    if 30 <= solicitudes_df['discapacidad'] <= 41:
        puntaje += 5
    elif 42 <= solicitudes_df['discapacidad'] <= 53:
        puntaje += 10
    elif 54 <= solicitudes_df['discapacidad'] <= 65:
        puntaje += 15
    elif 66 <= solicitudes_df['discapacidad'] <= 77:
        puntaje += 20
    elif solicitudes_df['discapacidad'] > 78:
        puntaje += 25

    # Puntuación por acceso a transporte
    puntaje += 1 if solicitudes_df['acceso_transporte'] else 5

    # Puntuación por provincia de residencia
    provincias_puntajes = {
        'alicante': 1,
        'castellón': 1,
        'valencia': 1,
        'murcia': 1,
        'almería': 1,
        'granada': 1,
        'huelva': 1,
        'sevilla': 1,
        'córdoba': 1,
        'jaén': 1,
        'málaga': 1,
        'cádiz': 1,
        'girona': 2,
        'barcelona': 2,
        'tarragona': 2,
        'lleida': 2,
        'ourense': 2,
        'lugo': 2,
        'pontevedra': 2,
        'a coruña': 2,
        'asturias': 2,
        'bilbao': 2,
        'álava': 2,
        'vizcaya': 2,
        'guipúzcoa': 2,
        'albacete': 3,
        'ciudad real': 3,
        'cuenca': 3,
        'guadalajara': 3,
        'toledo': 3,
        'badajoz': 3,
        'cáceres': 3,
        'madrid': 4,
        'huesca': 5,
        'zaragoza': 5,
        'teruel': 5,
        'la rioja': 5,
        'navarra': 5,
        'pamplona': 5,
        'cantabria': 5,
        'burgos': 6,
        'león': 6,
        'palencia': 6,
        'zamora': 6,
        'valladolid': 6,
        'soria': 6,
        'segovia': 6,
        'ávila': 6,
        'salamanca': 6,
        'baleares': 7,
        'las palmas': 7,
        'santa cruz de tenerife': 7,
        'ceuta': 7,
        'melilla': 7
    }
    puntaje += provincias_puntajes.get(solicitudes_df['provincia_residente'].lower(), 0)

    # Puntuación por uso de servicio anteriormente
    if solicitudes_df['imserso_anopasado'] and solicitudes_df['imserso_2021']:
            puntaje += 1
    elif solicitudes_df['imserso_anopasado'] and not solicitudes_df['imserso_2021']:
            puntaje += 5
    elif not solicitudes_df['imserso_anopasado'] and solicitudes_df['imserso_2021']:
            puntaje += 10
    else:
            puntaje += 25

    # Puntuación por pensión
    if 480 <= solicitudes_df['importe_pension'] <= 996:
        puntaje += 35
    elif 997 <= solicitudes_df['importe_pension'] <= 1513:
        puntaje += 20
    elif 1514 <= solicitudes_df['importe_pension'] <= 2030:
        puntaje += 10
    elif 2031 <= solicitudes_df['importe_pension'] <= 2547:
        puntaje += 5
    elif solicitudes_df['importe_pension'] > 2548:
        puntaje += 1

    return puntaje

# Aplica la función "calcular_puntaje" a cada fila del DF y agrega los resultados a una nueva tabla llamada 'puntuaciones'
puntuaciones_df = pd.DataFrame(solicitudes_df[['solicitud_id', 'nombre', 'apellidos']])
puntuaciones_df['puntaje'] = solicitudes_df.apply(calcular_puntaje, axis=1)

# CONEXION E INSERCIÓN DE LOS DATOS A LA TABAL 'PUNTUACIONES'

try:
    connection = psycopg2.connect(
        host=config['host'],
        database=config['database'],
        user=config['user'],
        password=config['password']
    )

    cursor = connection.cursor()

    # Inserta la tabla 'puntuaciones'

    for persona in puntuaciones_df.itertuples(index=False):
        insert_puntuaciones_query = """
        INSERT INTO public.puntuaciones 
        (solicitud_id, nombre, apellidos, puntaje)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING;  -- Evita duplicados
        """

        cursor.execute(insert_puntuaciones_query, (
            persona.solicitud_id,
            persona.nombre,
            persona.apellidos,
            persona.puntaje
        ))

    # Guarda los cambios en la base de datos
    connection.commit()

    puntuaciones_df = pd.read_sql('SELECT * FROM public.puntuaciones', con=engine)

except Exception as e:
    print(f"Error: {e}")

finally:
    # Cierra el cursor y la conexión
    if 'cursor' in locals():
        cursor.close()

################################# ASIGNACIÓN DE HOTELES #########################################
# Ordena el DF por la columna 'puntaje' de mayor a menor
puntuaciones_df = puntuaciones_df.sort_values(by='puntaje', ascending=False)

# Define la función para asignar los hoteles
def asignar_hoteles(puntuaciones_df, hoteles_df, preferencias_df, primer_recorrido=True):
   
    # Agrupa los hoteles por ciudad para contar las plazas
    total_plazas_por_provincia = hoteles_df.groupby('ciudad')['plazas'].sum().reset_index()

    for index, persona in preferencias_df.iterrows():
        # Obtiene las preferencias de la persona
        preferencias = persona[['opcion_1', 'opcion_2', 'opcion_3', 'opcion_4', 'opcion_5']]

        hoteles_asignados = []

        # Verifica si ya se le asignó un hotel en el primer recorrido
        asignado_en_primer_recorrido = (
            not puntuaciones_df['hotel_asignado_1'].isnull().iloc[index] or
            not puntuaciones_df['hotel_asignado_2'].isnull().iloc[index]
        )

        # Si no se le asignó en el primer recorrido, establece nuevas preferencias
        if not asignado_en_primer_recorrido and primer_recorrido:
            # Establecer nuevas preferencias (puedes adaptar esto según tus necesidades)
            preferencias = np.random.choice(ciudades_df['ciudad'], size=5, replace=False)

        for preferencia in preferencias:
            # Verifica si hay plazas disponibles en la ciudad de la preferencia
            plazas_disponibles_provincia = total_plazas_por_provincia[
                total_plazas_por_provincia['ciudad'] == preferencia]['plazas'].values

            if len(plazas_disponibles_provincia) > 0 and plazas_disponibles_provincia[0] > 0:
                # Filtra hoteles disponibles en la ciudad de la preferencia
                hoteles_disponibles = hoteles_df[(hoteles_df['ciudad'] == preferencia) & (hoteles_df['plazas'] > 0)]

                # Excluye hoteles que ya hayan sido asignados a ese viajero
                hoteles_disponibles = hoteles_disponibles[~hoteles_disponibles['hotel'].isin(hoteles_asignados)]

                for i in range(2):  # Intenta asignar hasta dos hoteles
                    if not hoteles_disponibles.empty and len(hoteles_asignados) < 2:
                        # Selecciona el hotel con más plazas disponibles y asigna según el puntaje
                        hotel_asignado = hoteles_disponibles.loc[hoteles_disponibles['plazas'].idxmax()]

                        # Actualiza las plazas disponibles del hotel y ciudad
                        plazas_a_restar = 2 if solicitudes_df['viajara_con_acompanante'].iloc[index] else 1
                        hoteles_df.loc[hoteles_df['hotel_id'] == hotel_asignado['hotel_id'], 'plazas'] -= plazas_a_restar

                        # Asigna hotel en el DF 'puntuaciones'
                        if (puntuaciones_df['solicitud_id'] == persona['solicitud_id']).any():
                            column_name = f'hotel_asignado_{i + 1}' if primer_recorrido else f'hotel_asignado_{i + 3}'
                            puntuaciones_df.at[index, column_name] = hotel_asignado['hotel']

                        # Elimina el hotel asignado de la lista de disponibles
                        hoteles_disponibles = hoteles_disponibles[~(hoteles_disponibles['hotel_id'] == hotel_asignado['hotel_id'])]
                        # Actualiza plazas disponibles en total_plazas_por_ciudad
                        total_plazas_por_provincia.loc[
                            total_plazas_por_provincia['ciudad'] == preferencia, 'plazas'] -= plazas_a_restar

                        # Agrega el hotel asignado a la lista de hoteles asignados
                        hoteles_asignados.append(hotel_asignado['hotel'])

                    else:
                        break  # Sale si no hay más hoteles disponibles

    # Si es el primer recorrido, realiza un segundo recorrido
    if primer_recorrido:
        puntuaciones_df_copia = puntuaciones_df.copy(deep=True)
        hoteles_df_copia = hoteles_df.copy(deep=True)

        # Llama recursivamente a la función para un segundo recorrido
        asignaciones_df_adicional = asignar_hoteles(
            puntuaciones_df_copia, hoteles_df_copia, preferencias_df, primer_recorrido=False)

        # Combina las asignaciones adicionales con las que ya existen
        puntuaciones_df = pd.concat([puntuaciones_df, asignaciones_df_adicional], ignore_index=True)

    return puntuaciones_df

# Llama a la función asignar_hoteles
resultado = asignar_hoteles(puntuaciones_df, hoteles_df, preferencias_df)
print(f'Dataframe puntuaciones: {resultado}')
print(f'Dataframe puntuaciones: {puntuaciones_df}')

#print(f'puntuaciones def: {solicitudes_df}')

# CONEXION E INSERCIÓN DE LOS DATOS A LA TABAL 'PUNTUACIONES'

try:
    connection = psycopg2.connect(
        host=config['host'],
        database=config['database'],
        user=config['user'],
        password=config['password']
    )

    cursor = connection.cursor()

    # Inserta tabla 'puntuaciones'

    # Itera sobre los resultados previos
    for persona in resultado.itertuples(index=False):
        insert_asignaciones_query = """
        INSERT INTO public.asignaciones 
        (solicitud_id, nombre, apellidos, puntaje, hotel_asignado_1, hotel_asignado_2)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (solicitud_id) DO NOTHING;  -- Evita duplicados
        """     

        cursor.execute(insert_asignaciones_query, (
            persona.solicitud_id,
            persona.nombre,
            persona.apellidos,
            persona.puntaje,
            persona.hotel_asignado_1,
            persona.hotel_asignado_2
        ))    

    # Guarda los cambios en la base de datos
    connection.commit()

except Exception as e:
    print(f"Error: {e}")

finally:
    # Cierra el cursor y la conexión
    if 'cursor' in locals():
        cursor.close()
