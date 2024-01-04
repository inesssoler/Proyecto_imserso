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


################################# CRITERIOS DE PUNTUACIÓN #################################
def calcular_puntaje(solicitudes_df):
    puntaje = 0

    # Puntuación según la edad
    if solicitudes_df['edad'] < 60:
        puntaje += 1
    elif 60 <= solicitudes_df['edad'] <= 78:
        puntaje += solicitudes_df['edad'] - 58
    else:
        puntaje += 20

    # Puntuación por discapacidad
    if solicitudes_df['discapacidad'] >= 33:
        puntaje += 10

    # Puntuación por situación económica
    tramos_ingresos = [
        (0, 484.61, 50),
        (484.61, 900, 45),
        (900, 1050, 40),
        (1050, 1200, 35),
        (1200, 1350, 30),
        (1350, 1500, 25),
        (1500, 1650, 20),
        (1650, 1800, 15),
        (1800, 1950, 10),
        (1950, 2100, 5),
        (2100, np.inf, 0)
    ]
    for tramo in tramos_ingresos:
        if tramo[0] <= solicitudes_df['importe_pension'] <= tramo[1]:
            puntaje += tramo[2]
            break

    # Puntuación por participación en años anteriores
    if solicitudes_df['imserso_anopasado'] and solicitudes_df['imserso_2021']:
        puntaje += 0
    elif solicitudes_df['imserso_anopasado'] and not solicitudes_df['imserso_2021']:
        puntaje += 5
    elif not solicitudes_df['imserso_anopasado'] and solicitudes_df['imserso_2021']:
        puntaje += 10
    else:
        puntaje += 25

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

    puntuaciones_df = pd.read_sql('SELECT * FROM public.puntuaciones', con=engine)

except Exception as e:
    print(f"Error: {e}")

finally:
    # Cierra el cursor y la conexión
    if 'cursor' in locals():
        cursor.close()



################################# ASIGNACIÓN DE HOTELES #########################################
# Ordenar el DataFrame por la columna 'puntaje' de mayor a menos
puntuaciones_df = puntuaciones_df.sort_values(by='puntaje', ascending=False)

# Funcion para asignar los hoteles
def asignar_hoteles(puntuaciones_df, hoteles_df, preferencias_df, primer_recorrido=True):
    # Agrupar hoteles por ciudad para contar las plazas
    total_plazas_por_provincia = hoteles_df.groupby('ciudad')['plazas'].sum().reset_index()

    for index, persona in preferencias_df.iterrows():
        # Obtener las preferencias de la persona
        preferencias = persona[['opcion_1', 'opcion_2', 'opcion_3', 'opcion_4', 'opcion_5']]

        hoteles_asignados = []
        hoteles_disponibles = pd.DataFrame()  # Inicializar como DataFrame vacío

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
                        
                        # Agregar el hotel a la lista de asignados
                        hoteles_asignados.append(hotel_asignado['hotel'])
                    else:
                        break  # Salir si no hay más hoteles disponibles

        # Si no se asignaron hoteles y es el primer recorrido, intentar asignar basándose en ciudades con plazas disponibles
        if len(hoteles_asignados) == 0 and primer_recorrido:
            ciudades_disponibles = total_plazas_por_provincia[total_plazas_por_provincia['plazas'] > 0]['ciudad'].tolist()
            for ciudad in ciudades_disponibles:
                hoteles_disponibles_ciudad = hoteles_df[(hoteles_df['ciudad'] == ciudad) & (hoteles_df['plazas'] > 0)]

                for _ in range(2):  # Intentar asignar hasta dos hoteles
                    if not hoteles_disponibles_ciudad.empty:
                        # Seleccionar el hotel con más plazas disponibles y asignar según el puntaje
                        hotel_asignado = hoteles_disponibles_ciudad.loc[hoteles_disponibles_ciudad['plazas'].idxmax()]

                        # Actualizar las plazas disponibles del hotel y ciudad
                        plazas_a_restar = 2 if solicitudes_df['viajara_con_acompanante'].iloc[index] else 1
                        hoteles_df.loc[hoteles_df['hotel_id'] == hotel_asignado['hotel_id'], 'plazas'] -= plazas_a_restar

                        # Asignar hotel en el dataframe 'puntuaciones'
                        if (puntuaciones_df['solicitud_id'] == persona['solicitud_id']).any():
                            puntuaciones_df.at[index, f'hotel_asignado_{_ + 1}'] = hotel_asignado['hotel']

                        # Eliminar el hotel asignado de la lista de disponibles
                        hoteles_disponibles_ciudad = hoteles_disponibles_ciudad[~(hoteles_disponibles_ciudad['hotel_id'] == hotel_asignado['hotel_id'])]
                        # Actualizar plazas disponibles en total_plazas_por_ciudad
                        total_plazas_por_provincia.loc[total_plazas_por_provincia['ciudad'] == ciudad, 'plazas'] -= plazas_a_restar

                    else:
                        break

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