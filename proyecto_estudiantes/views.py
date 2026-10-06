from models import Estudiante
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido

gestor = GestorJSON("data/estudiante.json")

# TUPLAS de configuración: fijas, nadie las modifica en tiempo de ejecución
CAMPOS_ESTUDIANTES = ("nombre", "apellido", "email", "carnet")
CAMPOS_OBLIGATORIOS = ("nombre", "apellido", "email", "carnet")
CAMPOS_BUSCABLES = ("nombre", "apellido", "email", "carnet")


# ===================== AYUDAS INTERNAS =====================

def emails_registrados(excepto_id=None):
    """CONJUNTO con los emails ya usados. Sirve para detectar duplicados al instante."""
    return {
        registro["email"].lower()
        for registro in gestor.leer()
        if registro["id"] != excepto_id
    }

def carnets_resgistrados(excepto_id=None):
    """CONJUNTO con los carnets ya usados. Sirve para detectar duplicados al instante."""
    return{
        registro["carnet"].lower()
        for registro in gestor.leer()
        if registro["id"] != excepto_id
    }

def siguiente_id():
    ids = [registro["id"] for registro in gestor.leer()]
    return max(ids) + 1 if ids else 1


# ===================== C · CREATE =====================

def crear_estudiantes(datos):
    try:
        valores ={
            campo: str(datos.get(campo,"")).strip()
            for campo in CAMPOS_ESTUDIANTES
        }
        
        faltantes = [
            campo
            for campo in CAMPOS_OBLIGATORIOS
            if not valores[campo]
        ]
        
        if faltantes:
            return False, f"Faltan campos obligatorios: {', '.join(faltantes)}"
        
        if not es_email_valido(valores["email"]):
            return False, f"El email '{valores['email']}' no tiene un formato válido"
        
        if valores["email"].lower() in emails_registrados():
            return False, "Ese email ya está registrado"
        
        if valores["carnet"].lower() in carnets_resgistrados():
            return False, "Ese carnet ya está registrado"
        
        estudiante = Estudiante(
            siguiente_id(),
            valores["nombre"],
            valores["apellido"],
            valores["email"],
            valores["carnet"],
            )
        
        if not gestor.añadir(estudiante.a_diccionario()):
            return False, "No se pudo escribir el archivo"
        
        return True, (
            f"estudiante {estudiante.obtener_nombre_completo()}"
            f"creado con id {estudiante.id}"
        )        
        
    except Exception as error:
        return False, f"Error inesperado: {error}"

# ===================== R · READ =====================

def obtener_todos():
    """LISTA de objetos Cliente."""
    return [Estudiante.desde_diccionario(registro) for registro in gestor.leer()]


def obtener_por_id(id_estudiante):
    for estudiante in obtener_todos():
        if estudiante.id == id_estudiante:
            return estudiante
    return None


# ===================== S · SEARCH =====================

def buscar_estudiantes(termino):
    """Búsqueda lineal: revisa registro por registro los campos de CAMPOS_BUSCABLES."""
    termino = termino.strip().lower()
    if not termino:
        return []

    encontrados = []
    for registro in gestor.leer():
        for campo in CAMPOS_BUSCABLES:                 # recorro la TUPLA de campos
            if termino in str(registro.get(campo, "")).lower():
                encontrados.append(
                    Estudiante.desde_diccionario(registro)
                )
                break                                   # ya coincidió: paso al siguiente Estudiante
    return encontrados


# ===================== U · UPDATE =====================

def actualizar_estudiantes(id_estudiante, cambios):
    """cambios: diccionario solo con los campos que se quieren modificar."""
    try:
        # DIFERENCIA DE CONJUNTOS: ¿mandaron algún campo que no existe?
        desconocidos = (set(cambios) - set(CAMPOS_ESTUDIANTES))
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        if not cambios:
            return False, "No se indicó ningún cambio"

        if "email" in cambios:
            
            if not es_email_valido(cambios["email"]):
                return False, "El email no tiene un formato válido"
            if cambios["email"].lower() in emails_registrados(excepto_id=id_estudiante):
                return False, "Ese email ya lo usa otro cliente"
        
        if "carnet" in cambios:
            cambios["carnet"] = cambios["carnet"].strip()
            if cambios["carnet"].lower() in carnets_resgistrados(excepto_id=id_estudiante):
                return False, "Ese carnet ya lo usa otro estudiante"
            
        if not gestor.actualizar(id_estudiante, cambios):
            return False, (f"No existe un estudiante con id {id_estudiante}")
        return True, (f"estudiante {id_estudiante} actualizado")

    except Exception as error:
        return False, f"Error inesperado: {error}"


# ===================== D · DELETE =====================

def eliminar_estudiantes(id_estudiante):
    
    if not gestor.eliminar(id_estudiante):
        return False, "No se pudo guardar la información"

    return True, (f"Estudiante {id_estudiante} eliminado")


# ===================== Extras ==========================

def agregar_nota(id_estudiante, materia, nota):
    try:
        nota = float(nota)

        if nota < 0 or nota > 20:
            return False, "La nota debe estar entre 0 y 20"

        materia = materia.strip()

        if not materia:
            return False, "La materia no puede estar vacía"

        estudiante = obtener_por_id(id_estudiante)

        if not estudiante:
            return False, f"No existe un estudiante con id {id_estudiante}"

        estudiante.agregar_nota(materia, nota)

        registros = gestor.leer()

        for indice, registro in enumerate(registros):
            if registro["id"] == id_estudiante:
                registros[indice] = estudiante.a_diccionario()
                break

        if not gestor.guardar(registros):
            return False, "No se pudo guardar la nota"

        return True, f"Nota {nota} agregada en {materia}"

    except (ValueError, TypeError):
        return False, "La nota debe ser un número"
    
def materias_ofertadas():
    materias = set()

    for estudiante in obtener_todos():
        materias.update(estudiante.materias)

    return materias

def estudiantes_en_comun(id_a, id_b):
    estudiante_a = obtener_por_id(id_a)
    estudiante_b = obtener_por_id(id_b)

    if not estudiante_a:
        return False, f"No existe un estudiante con id {id_a}"

    if not estudiante_b:
        return False, f"No existe un estudiante con id {id_b}"

    materias = estudiante_a.materias_en_comun(estudiante_b)

    return True, materias