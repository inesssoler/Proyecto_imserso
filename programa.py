import pandas as pd
import numpy as np
import psycopg2
from faker import Faker
from sqlalchemy import create_engine, text
from config import config
import time

# Para darle tiempo al contenedor de postgres para levantarse por completo antes de ejecutar el script
time.sleep(10)

# Conexión 
engine = create_engine(f"postgresql+psycopg2://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}")

conn = engine.connect()
query_solicitudes = text('SELECT * FROM public.solicitudes')
query_ciudades = text('SELECT * FROM public.ciudades')
query_preferencias = text('SELECT * FROM public.preferencias')
query_destino = text('SELECT * FROM public.destinos')
query_hoteles = text('SELECT * FROM public.hoteles')

solicitudes_df = pd.read_sql(query_solicitudes, con=conn)
ciudades_df = pd.read_sql(query_ciudades, con=conn)
preferencias_df = pd.read_sql(query_preferencias, con=conn)
destino_df = pd.read_sql(query_destino, con=conn)
hoteles_df = pd.read_sql(query_hoteles, con=conn)

conn.close()

################################# CRITERIOS DE PUNTUACIÓN #########################################
def calcular_puntaje(solicitudes_df):
    puntaje = 0

    # Puntaje según la edad
    if 65 <= solicitudes_df['edad'] <= 75:
        puntaje += 10
    elif 76 <= solicitudes_df['edad'] <= 85:
        puntaje += 15
    elif solicitudes_df['edad'] > 86:
        puntaje += 20

    # Puntaje por estado civil
    puntaje += 10 if solicitudes_df['soltero_o_viudo'] else 0

    # Puntaje por residencia en mayores
    puntaje += 15 if solicitudes_df['vive_en_residencia'] else 0

    # Puntaje por discapacidad
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

    # Puntaje por acceso al transporte
    puntaje += 1 if solicitudes_df['acceso_transporte'] else 5

    # Puntaje por provincia
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


    # Puntaje por año de viaje
    if solicitudes_df['imserso_anopasado'] and solicitudes_df['imserso_2021']:
            puntaje += 1
    elif solicitudes_df['imserso_anopasado'] and not solicitudes_df['imserso_2021']:
            puntaje += 5
    elif not solicitudes_df['imserso_anopasado'] and solicitudes_df['imserso_2021']:
            puntaje += 10
    else:
            puntaje += 25

    # Puntaje por pensión
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

# Aplicar la función calcular_puntaje a cada fila del DataFrame y agregar los resultados a una nueva tabla llamada 'puntuaciones'
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

    # Insertar tabla 'puntuaciones'

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

    query_puntuaciones = text('SELECT * FROM public.puntuaciones')
    puntuaciones_df = pd.read_sql(query_puntuaciones, con=engine)

except Exception as e:
    print(f"Error: {e}")

finally:
    # Cierra el cursor y la conexión
    if 'cursor' in locals():
        cursor.close()



################################# ASIGNACIÓN DE HOTELES #########################################
# Ordenar el DataFrame por la columna 'puntaje' de mayor a menor
puntuaciones_df = puntuaciones_df.sort_values(by='puntaje', ascending=False)

# Funcion para asignar los hoteles
def asignar_hoteles(puntuaciones_df, hoteles_df, preferencias_df, primer_recorrido=True):

    # Agrupar hoteles por ciudad para contar las plazas
    total_plazas_por_provincia = hoteles_df.groupby('ciudad')['plazas'].sum().reset_index()

    for index, persona in preferencias_df.iterrows():
        # Obtener las preferencias de la persona
        preferencias = persona[['opcion_1', 'opcion_2', 'opcion_3', 'opcion_4', 'opcion_5']]

        hoteles_asignados = []

        for preferencia in preferencias:
             # Verificar si hay plazas disponibles en la ciudad de la preferencia
            plazas_disponibles_provincia = total_plazas_por_provincia[total_plazas_por_provincia['ciudad'] == preferencia]['plazas'].values
            if len(plazas_disponibles_provincia) > 0 and plazas_disponibles_provincia[0] > 0:
                # Filtrar hoteles disponibles en la ciudad de la preferencia
                hoteles_disponibles = hoteles_df[(hoteles_df['ciudad'] == preferencia) & (hoteles_df['plazas'] > 0)]

            # Excluir hoteles que ya han sido asignados a esta persona
            hoteles_disponibles = hoteles_disponibles[~hoteles_disponibles['hotel'].isin(hoteles_asignados)]

            for _ in range(2):  # Intentar asignar hasta dos hoteles
                if not hoteles_disponibles.empty and len(hoteles_asignados) < 2:
                    # Seleccionar el hotel con más plazas disponibles y asignar según el puntaje
                    hotel_asignado = hoteles_disponibles.loc[hoteles_disponibles['plazas'].idxmax()]

                    # Actualizar las plazas disponibles del hotel y ciudad
                    plazas_a_restar = 2 if solicitudes_df['viajara_con_acompanante'].iloc[index] else 1
                    hoteles_df.loc[hoteles_df['hotel_id'] == hotel_asignado['hotel_id'], 'plazas'] -= plazas_a_restar

                    # Asignar hotel en el dataframe 'puntuaciones'
                    if (puntuaciones_df['solicitud_id'] == persona['solicitud_id']).any():
                        puntuaciones_df.at[index, f'hotel_asignado_{_ + 1}'] = hotel_asignado['hotel']


                    # Eliminar el hotel asignado de la lista de disponibles
                    hoteles_disponibles = hoteles_disponibles[~(hoteles_disponibles['hotel_id'] == hotel_asignado['hotel_id'])]
                    # Actualizar plazas disponibles en total_plazas_por_ciudad
                    total_plazas_por_provincia.loc[total_plazas_por_provincia['ciudad'] == preferencia, 'plazas'] -= plazas_a_restar

                else:
                    break  # Salir si no hay más hoteles disponibles

    # Si es el primer recorrido, realizar un segundo recorrido
    if primer_recorrido:
        # Realizar una copia profunda de los DataFrames para evitar problemas de referencia
        puntuaciones_df_copia = puntuaciones_df.copy(deep=True)
        hoteles_df_copia = hoteles_df.copy(deep=True)

        # Llamar recursivamente a la función para un segundo recorrido
        asignaciones_df_adicional = asignar_hoteles(puntuaciones_df_copia, hoteles_df_copia, preferencias_df, primer_recorrido=False)

        # Combinar las asignaciones adicionales con las existentes
        puntuaciones_df = pd.concat([puntuaciones_df, asignaciones_df_adicional], ignore_index=True)

    return puntuaciones_df


# Llamar a la función asignar_hoteles
resultado = asignar_hoteles(puntuaciones_df, hoteles_df, preferencias_df)


# CONEXION E INSERCIÓN DE LOS DATOS A LA TABLA 'PUNTUACIONES'

try:
    connection = psycopg2.connect(
        host=config['host'],
        database=config['database'],
        user=config['user'],
        password=config['password']
    )

    cursor = connection.cursor()

    # Insertar tabla 'puntuaciones'

    # Iterar sobre los resultados previos
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
    if 'connection' in locals():
        connection.close()









