# Importamos módulos requeridos
import os
import random
import pygame

# Estados del juego
ESTADO_INICIO = "inicio"
ESTADO_INSTRUCCIONES = "instrucciones"
ESTADO_JUGANDO = "jugando"
ESTADO_DERROTA = "derrota"
ESTADO_VICTORIA = "victoria"

# Rutas a la carpeta de imágenes de pantallas
DIR_PANTALLAS = os.path.join(os.path.dirname(__file__), "assets", "fondos")

# Se específica el nombre del archivo para cada imagen de pantalla.
# El formato de imagen utilizado puede ser PNG, JPG/JPEG, BMP, o GIF.
PANTALLA_INICIO = "fondo_inicio.jpeg"
PANTALLA_INSTRUCCIONES = "fondo_instrucciones.jpeg"
PANTALLA_VICTORIA = "fondo_ganaste.jpeg"
PANTALLA_DERROTA = "fondo_perdiste.jpeg"
PANTALLA_NIVEL1 = "fondo_1.jpeg"
PANTALLA_NIVEL2 = "fondo_2.jpeg"
PANTALLA_NIVEL3 = "fondo_3.jpeg"

# Para evitar que el jugador se mueva demasiado rápido
RETRASO = 150

# Velocidad del movimiento de los enemigos (en milisegundos)
RETRASO_ENEMIGOS_PRIMER = 250

# Códigos de cada elemento del tablero
VACIO = 0
OBSTACULO = 1
JUGADOR = 2
MANZANA = 3
AGRANDAR = 4
CANT_AGRANDAR = 3

CANT_ENEMIGOS = 4

largo_victoria = 5

# Tamaño del tablero
# Si se cambian estas constantes, se debe modificar la definición
# del tablero que se encuentra en función reiniciar().
FILAS = 15
COLUMNAS = 15

#tamaño de la ventana (en pixeles)
ANCHO_VENTANA = 1040
ALTO_VENTANA = 800

#el tablero es un cuadrado fijo, independiente de la ventana
LADO_TABLERO=800

#lo que sobra a la derecha de la ventana es el ancho del panel
ANCHO_PANEL = ANCHO_VENTANA - LADO_TABLERO

def aparecer_aleatorio(tablero, id_elem, incluir_borde=True):
    """
    Coloca un elemento en una casilla vacía aleatoria del tablero.

    Parámetros:
        - tablero: El tablero con sus posiciones actuales.
        - id_elem: El número identificador del elemento que queremos colocar.

    Retorna:
        - (columna, fila): Tupla que indica posición en la que se colocó el elemento.
    """

    # Debemos detectar los espacios vacíos, para ello recorremos
    # el tablero y almacenamos tuplas de (columna, fila) las posiciones
    # en las que un elemento "VACIO" (el número 0 en este caso) se encuentre.
    vacios = []

    filas_rango = range(FILAS) if incluir_borde else range(1, FILAS - 1)
    columnas_rango = range(COLUMNAS) if incluir_borde else range(1, COLUMNAS - 1)
    # Forma vista en clases de recorrer el arreglo multidimensional.
    # Tanto fila como columna son números.
    for fila in range(FILAS):
        for columna in range(COLUMNAS):
            # Obtenemos el elemento que se encuentra en esa fila y columna.
            elem_pos = tablero[fila][columna]

            if elem_pos == VACIO:
                # Al utilizar los paréntesis () dentro de la función, lo estaremos
                # añadiendo como una tupla con la estructura (columna, fila).
                vacios.append((columna, fila))

    # También se puede utilizar comprensión de listas para rellenar el arreglo
    # a la vez que lo recorremos:
    #
    # vacios = [
    #     (columna, fila)
    #     for fila in range(FILAS)
    #     for columna in range(COLUMNAS)
    #     if tablero[fila][columna] == VACIO
    # ]

    # Si no hay casillas vacías, retornamos un valor especial.
    if len(vacios) == 0:
        return -1, -1

    # Usando la función random.choice(lista) podremos obtener una tupla
    # aleatoria desde el arreglo "vacios" que definimos anteriormente.
    columna, fila = random.choice(vacios)

    # Finalmente, colocamos el elemento al poner su número en la casilla
    # del tablero correspondiente.
    tablero[fila][columna] = id_elem

    return columna, fila


def poblar_tablero(tablero):
    for _ in range(CANT_ENEMIGOS):
        aparecer_aleatorio(tablero, OBSTACULO, False)
    """
    Coloca un obstáculo y la manzana en el tablero.

    Parámetros:
        - tablero: El tablero con sus posiciones actuales.
    """
    aparecer_aleatorio(tablero, MANZANA)

def dibujar_panel(screen, fuente, objetos_conseguidos):
    # Dibuja el panel lateral con información del juego.
    panel = pygame.Rect(LADO_TABLERO, 0, ANCHO_PANEL, ALTO_VENTANA)
    pygame.draw.rect(screen, "gray15", panel)

    x = LADO_TABLERO + 24

    titulo = fuente.render("MI JUEGO", True, "white")
    screen.blit(titulo, (x, 30))

    objetos_txt = fuente.render(f"Objetos: {objetos_conseguidos}/{CANT_AGRANDAR}", True, "gold")
    screen.blit(objetos_txt, (x, 100))

def refrescar_tablero(screen, tablero, img_personaje, fuente, objetos_conseguidos, escala_jugador):
    """
    Dibuja el estado actual del tablero en la pantalla.

    Parámetros:
        - screen: La pantalla sobre la cual estamos dibujando.
        - tablero: El tablero con sus posiciones actuales.
    """

    # Rellena la pantalla con el color gris, básicamente pintando
    # por encima de lo que estaba anteriormente.
    imagen = pygame.image.load("assets/fondos/fondo_1.jpeg").convert()
    imagen = pygame.transform.scale(imagen, (LADO_TABLERO, LADO_TABLERO))

    # Dibujamos la imagen en la pantalla en la coordenada (0, 0).
    screen.blit(imagen, (0, 0))

    pers = pygame.image.load("assets/personaje/personaje_frontal.png").convert_alpha()
    enemigo = pygame.image.load("assets/enemigos/enemigo_1.png").convert_alpha()

    # Podemos calcular el tamaño en pixeles que tendrá cada
    # casilla al dividir tanto la altura de la pantalla (screen.get_height())
    # como el ancho (screen.get_width()) por la cantidad de filas y columnas respectivamente.
    # Por ejemplo en este caso alto_elem sería 800 / 15 = 53.3, lo que nos indica que la
    # altura de cada elemento es de 53.3 píxeles.
    alto_elem = LADO_TABLERO / FILAS
    ancho_elem = LADO_TABLERO / COLUMNAS
    # Como el jugador es un círculo, se necesita el radio.
    radio = ancho_elem / 2

    # Posición en eje "y" en unidad de píxeles.
    pos_y = 0

    for i in range(FILAS):
        # Posición en eje "x" en unidad de píxeles.
        pos_x = 0
        for j in range(COLUMNAS):
            if tablero[i][j] == OBSTACULO:
                # Dibuja un rectángulo en la posición (pos_x, pos_y) y que sea
                # de tamaño (ancho_elem, alto_elem) y color negro.
                screen.blit(enemigo, [pos_x, pos_y])
            elif tablero[i][j] == JUGADOR:
                # Dibujamos un círculo verde en la posición (pos_x + radio, pos_y + radio),
                # con un radio definido por la variable "radio" (ancho_elem / 2).
                ancho_img = int(ancho_elem * escala_jugador)
                alto_img = int(alto_elem * escala_jugador)
                img_escalada = pygame.transform.scale(img_personaje, (ancho_img, alto_img))
                offset_x = (ancho_img - ancho_elem) / 2
                offset_y = (alto_img - alto_elem) / 2
                screen.blit(img_escalada, [pos_x - offset_x, pos_y - offset_y])
            elif tablero[i][j] == MANZANA:
                pygame.draw.rect(
                    screen,
                    "red",
                    # Acá reducimos el tamaño del rectángulo
                    # para identificarlo más fácilmente
                    pygame.Rect(
                        (pos_x + 15, pos_y + 15),
                        (ancho_elem - 30, alto_elem - 30),
                    ),
                )
            elif tablero[i][j] == AGRANDAR:
                pygame.draw.rect(
                    screen,
                    "gold",
                    # Objeto que al ser tocado aumenta el tamaño del jugador.
                    pygame.Rect(
                        (pos_x + 15, pos_y + 15),
                (ancho_elem - 30, alto_elem - 30),
                    ),
                )

            # Estamos recorriendo los píxeles de la pantalla, por lo que
            # debemos sumar el ancho y altura en pixeles de cada elemento que
            # ya hayamos recorrido para avanzar al siguiente.
            pos_x += ancho_elem
        pos_y += alto_elem

    # Refresca el contenido que se ve en pantalla.
    dibujar_panel(screen, fuente, objetos_conseguidos)
    pygame.display.flip()

def mover_enemigo():
    # Retorna una dirección aleatoria para el movimiento de un enemigo.
    return random.choice([
        (0, -1),  # arriba
        (0, 1),   # abajo
        (-1, 0),  # izquierda
        (1, 0)    # derecha
    ])

def avanzar_enemigos(tablero, pos_enemigos):
    # Mueve a cada enemigo un paso en una dirección aleatoria.
    for i in range(len(pos_enemigos)):
        pos_enemigo = pos_enemigos[i]

        col, fila = pos_enemigo

        dir_col, dir_fila = mover_enemigo()

        nueva_col = col + dir_col
        nueva_fila = fila + dir_fila

        if 0 <= nueva_col < COLUMNAS and 0 <= nueva_fila < FILAS:

            if tablero[nueva_fila][nueva_col] == VACIO:

                tablero[fila][col] = VACIO
                tablero[nueva_fila][nueva_col] = OBSTACULO
                pos_enemigos[i] = (nueva_col, nueva_fila)

    return pos_enemigos

def cambiar_direccion(keys, direccion_actual):
    """
    Cambia la dirección del jugador.

    Parámetros:
        - keys: Arreglo de teclas presionadas.
        - direccion_actual: La dirección en la que estaba avanzando justo antes de analizar
            si hubo un cambio de dirección.

    Retorna:
        - direccion_actual: La nueva dirección del jugador.
    """

    # Tecla W
    if keys[pygame.K_w]:
        # La tupla nos indica que horizontalmente (columnas) no hará nada (0) y
        # que verticalmente (filas) disminuirá el índice en el tablero (-1).
        return (0, -1)

    # Tecla S
    if keys[pygame.K_s]:
        # En este caso avanzará a través de las filas del tablero.
        return (0, 1)

    # Tecla A
    if keys[pygame.K_a]:
        # Retrocede por las columnas del tablero.
        return (-1, 0)

    # Tecla D
    if keys[pygame.K_d]:
        # Avanza por las columnas del tablero.
        return (1, 0)

    # Si no se presiona ninguna de las teclas anteriores, la dirección
    # será la misma que la anterior.
    return direccion_actual

def avanzar(tablero, pos_jugador, direccion, objetos_conseguidos):
    """
    Avanza el jugador un paso en la dirección dada.

    Parámetros:
        - tablero: El tablero con sus posiciones actuales.
        - pos_jugador: Tupla con la posición actual (índice con
            estructura (columna, fila)) del jugador en el tablero.
        - direccion: Tupla con la dirección en la que está avanzando actualmente el jugador.

    Retorna:
        - (resultado, nueva_pos_jugador): Retorna el resultado que se obtiene
            al avanzar (derrota, victoria o "ok" (no cambia de pantalla)) y la nueva posición del jugador.
    """

    # Obtenemos los componentes "x" e "y" de cada tupla recibida
    # con información de la dirección y posición del jugador.
    dir_col, dir_fila = direccion
    ind_actual_col, ind_actual_fila = (
        pos_jugador  # Tupla (columna, fila) que representa los índices en el tablero.
    )

    # Aplicamos la dirección a la posición del jugador.
    ind_nueva_col = ind_actual_col + dir_col
    ind_nueva_fila = ind_actual_fila + dir_fila

    # Verificamos que no haya choque con el borde del tablero.
    if not (0 <= ind_nueva_col < COLUMNAS and 0 <= ind_nueva_fila < FILAS):
        return "derrota", pos_jugador

    # Obtenemos el elemento que se encuentre en el tablero en la nueva posición del jugador.
    pos_elem = tablero[ind_nueva_fila][ind_nueva_col]

    if pos_elem == OBSTACULO:
        # Si el jugador choca con un obstáculo, pierde.
        return "derrota", pos_jugador

    if pos_elem == MANZANA:
        # Si el jugador toca la manzana, verifica si ya consiguió los 3 objetos de agrandar. (Generado con ayuda de IA (Claude))
        if objetos_conseguidos >= CANT_AGRANDAR:
            return "victoria", (ind_nueva_col, ind_nueva_fila)
        else:
            # Aún no consigue los 3 objetos, no puede pasar por la manzana
            return "ok", pos_jugador
    
    if pos_elem == AGRANDAR:
        # Si el jugador encuentra un objeto de agrandar, lo recoge y se agranda. (Generado con ayuda de IA (Claude))
        tablero[ind_actual_fila][ind_actual_col] = VACIO
        tablero[ind_nueva_fila][ind_nueva_col] = JUGADOR
        return "agrandar", (ind_nueva_col, ind_nueva_fila)

    # Movimiento normal, si es que no encontramos manzana ni obstáculo.
    tablero[ind_actual_fila][ind_actual_col] = VACIO
    tablero[ind_nueva_fila][ind_nueva_col] = JUGADOR

    return "ok", (ind_nueva_col, ind_nueva_fila)


def reiniciar():
    """
    Crea un nuevo tablero y estado para una nueva partida.

    Retorna:
        - (tablero, pos_jugador): Tablero nuevo y la nueva posición aleatoria del jugador.
            pos_jugador corresponda a una tupla (columna, fila) donde columna y fila son índices
            de matriz tablero.
    """

    # Si se modifica constante FILAS o COLUMNAS al inicio, también
    # se debe modificar este arreglo de tablero con los valores correspondientes.
    # Esto puede ser mejorado usando dos bucles "for" anidados o comprensión de listas.
    tablero = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]

    # Usando dos bucles "for" anidados se haría de la siguiente manera:
    # tablero = []
    # for _ in range(FILAS):
    #     fila_tablero = []
    #
    #     for _ in range(COLUMNAS):
    #         fila_tablero.append(VACIO)
    #
    #     tablero.append(fila_tablero)
    # Otra manera usando comprensión de listas:
    # tablero = [[VACIO] * COLUMNAS for _ in range(FILAS)]
    # El _ en el "for" indica que no usamos la variable con la que iteramos.
    
    # Colocamos al jugador en la posición (1, 10) del tablero.
    tablero[10][1] = JUGADOR 
    pos_jugador = (1, 10)

    # Colocamos los enemigos en posiciones aleatorias del tablero.
    pos_enemigos = []

    for _ in range(CANT_ENEMIGOS):
        pos_enemigos.append(aparecer_aleatorio(tablero, OBSTACULO))

    for _ in range(CANT_AGRANDAR):
        # Colocamos los objetos que agrandan al jugador en posiciones aleatorias.
        aparecer_aleatorio(tablero, AGRANDAR)
    
    # Colocamos la manzana en una posición aleatoria del tablero.
    aparecer_aleatorio(tablero, MANZANA)

    return tablero, pos_jugador, pos_enemigos


def mostrar_pantalla(screen, nombre_archivo):
    """
    Carga una imagen y la muestra escalada a la ventana.

    Parámetros:
        - screen: La pantalla donde colocaremos la imagen.
        - nombre_archivo: El nombre del archivo de la imagen.
    """

    ruta = os.path.join(DIR_PANTALLAS, nombre_archivo)

    try:
        imagen = pygame.image.load(ruta)
        imagen = pygame.transform.scale(imagen, screen.get_size())

        # Dibujamos la imagen en la pantalla en la coordenada (0, 0).
        screen.blit(imagen, (0, 0))

        # Refrescamos pantalla.
        pygame.display.flip()
    except FileNotFoundError:
        # Fallback de seguridad en caso de que las imágenes no existan aún
        screen.fill("black")
        pygame.display.flip()
        print(f"Advertencia: No se encontró la imagen {ruta}")


def main():
    pygame.init()
    fuente = pygame.font.Font(None, 36)

    # Establecemos la resolución de la pantalla.
    screen = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))

    # Establecemos el título de la ventana.
    pygame.display.set_caption("Juego Básico")

    running = True

    pygame.mixer.music.load("assets/Musica/musica_1.mp3")
    pygame.mixer.music.play(-1)
    cancion_actual = "assets/Musica/musica_1.mp3"

    estado = ESTADO_INICIO
    tablero = []
    pos_jugador = (0, 0)
    direccion = (0, 0)
    escala_jugador = 1.0
    objetos_conseguidos = 0
    tiempo_ultimo_mov = 0
    tiempo_enemigos = 0
    mostrar_pantalla(screen, PANTALLA_INICIO)
    pos_enemigos= [(100, 100), (200, 200)]

    img_arriba = pygame.image.load("assets/personaje/personaje_frontal.png").convert_alpha()
    img_abajo = pygame.image.load("assets/personaje/personaje_frontal.png").convert_alpha()
    img_izq = pygame.image.load("assets/personaje/personaje_retroceso.png").convert_alpha()
    img_der = pygame.image.load("assets/personaje/personaje_avanzando.png").convert_alpha()

    img_actual = img_abajo

    # Este es el bucle principal del juego, todo lo que sucede en el juego
    # está aquí.
    while running:
        # Se analizan los eventos del bucle actual.
        for evento in pygame.event.get():
            # Si es que se quiere cerrar la ventana.
            if evento.type == pygame.QUIT:
                running = False

            # Si es que se presiona alguna tecla.
            if evento.type == pygame.KEYDOWN:
                if estado == ESTADO_INICIO:

                    if evento.key == pygame.K_RETURN:
                        if cancion_actual != "assets/Musica/musica_2.mp3":
                            pygame.mixer.music.load("assets/Musica/musica_2.mp3")
                            pygame.mixer.music.play(-1)
                            cancion_actual = "assets/Musica/musica_2.mp3"

                        tablero, pos_jugador, pos_enemigos = reiniciar()
                        direccion = (0, 0)
                        escala_jugador = 1.0
                        objetos_conseguidos = 0 
                        # Obtiene tiempo en milisegundos
                        tiempo_ultimo_mov = pygame.time.get_ticks()
                        estado = ESTADO_JUGANDO
                        refrescar_tablero(screen, tablero, img_actual, fuente, objetos_conseguidos, escala_jugador)
                    elif evento.key == pygame.K_i:
                        estado = ESTADO_INSTRUCCIONES
                        mostrar_pantalla(screen, PANTALLA_INSTRUCCIONES)

                elif estado == ESTADO_INSTRUCCIONES:
                    estado = ESTADO_INICIO
                    mostrar_pantalla(screen, PANTALLA_INICIO)

                elif estado in (ESTADO_DERROTA, ESTADO_VICTORIA):

                    if evento.key == pygame.K_r:
                        if cancion_actual != "assets/Musica/musica_2.mp3":
                            pygame.mixer.music.load("assets/Musica/musica_2.mp3")
                            pygame.mixer.music.play(-1)
                            cancion_actual = "assets/Musica/musica_2.mp3"

                        tablero, pos_jugador, pos_enemigos = reiniciar()
                        pasos = 0
                        direccion = (0, 0)
                        escala_jugador = 1.0
                        objetos_conseguidos = 0
                        tiempo_ultimo_mov = pygame.time.get_ticks()
                        estado = ESTADO_JUGANDO
                        refrescar_tablero(screen, tablero, img_actual, fuente, objetos_conseguidos, escala_jugador)

                    if evento.key == pygame.K_ESCAPE:
                        if cancion_actual != "assets/Musica/musica_1.mp3":
                            pygame.mixer.music.load("assets/Musica/musica_1.mp3")
                            pygame.mixer.music.play(-1)
                            cancion_actual = "assets/Musica/musica_1.mp3"

                        escala_jugador = 1.0
                        objetos_conseguidos = 0
                        estado = ESTADO_INICIO
                        mostrar_pantalla(screen, PANTALLA_INICIO)

                if estado == ESTADO_JUGANDO:
                    if evento.key in (pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d):
                        direccion = cambiar_direccion(pygame.key.get_pressed(), direccion)

                        tiempo_actual = pygame.time.get_ticks()

                        if tiempo_actual - tiempo_ultimo_mov >= RETRASO:
                            resultado, pos_jugador = avanzar(tablero, pos_jugador, direccion, objetos_conseguidos)
            
                            tiempo_ultimo_mov = tiempo_actual
                        
                            # cambio de imagen segun direccion actual
                            if direccion == (0 , -1) :
                                img_actual = img_arriba
                            elif direccion == (0 , 1) :
                                img_actual = img_abajo
                            elif direccion == ( -1 , 0) :
                                img_actual = img_izq
                            elif direccion == (1 , 0) :
                                img_actual = img_der

                            if resultado == "derrota":
                                if cancion_actual != "assets/Musica/musica_derrota.mp3":
                                    pygame.mixer.music.load("assets/Musica/musica_derrota.mp3")
                                    pygame.mixer.music.play(0)
                                    cancion_actual = "assets/Musica/musica_derrota.mp3"
                                estado = ESTADO_DERROTA
                                mostrar_pantalla(screen, PANTALLA_DERROTA)
                            elif resultado == "victoria":
                                if cancion_actual != "assets/Musica/musica_victoria.mp3":
                                    pygame.mixer.music.load("assets/Musica/musica_victoria.mp3")
                                    pygame.mixer.music.play(0)
                                    cancion_actual = "assets/Musica/musica_victoria.mp3"
                                estado = ESTADO_VICTORIA
                                mostrar_pantalla(screen, PANTALLA_VICTORIA)
                            elif resultado == "agrandar":
                                objetos_conseguidos += 1
                                escala_jugador += 0.3
                            else:
                                tiempo_ultimo_mov = tiempo_actual
                            
            
        if estado == ESTADO_JUGANDO:
            tiempo_actual_enemigos = pygame.time.get_ticks()

            if tiempo_actual_enemigos - tiempo_enemigos >= RETRASO_ENEMIGOS_PRIMER:
                pos_enemigos = avanzar_enemigos(tablero, pos_enemigos)
                refrescar_tablero(screen, tablero, img_actual, fuente, objetos_conseguidos, escala_jugador)
                tiempo_enemigos = tiempo_actual_enemigos
                
    pygame.quit()


if __name__ == "__main__":
    main()

