import json
import os


class GestorJSON:
    """Lee y guarda una lista de diccionarios en un archivo JSON."""

    def __init__(self, ruta):
        self.ruta = ruta
        carpeta = os.path.dirname(ruta)
        if carpeta and not os.path.exists(carpeta):
            os.makedirs(carpeta)

    def leer(self):
        # Devuelve SIEMPRE una lista: vacía si el archivo no existe o está dañado
        if not os.path.exists(self.ruta):
            return []
        try:
            with open(self.ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
            return datos if isinstance(datos, list) else []
        except (json.JSONDecodeError, OSError):
            # Capturamos errores concretos, nunca un "except:" pelado
            return []

    def guardar(self, datos):
        try:
            with open(self.ruta, "w", encoding="utf-8") as archivo:
                json.dump(
                    datos, 
                    archivo, 
                    ensure_ascii=False, 
                    indent=2)
            return True
        except (TypeError, OSError):
            # TypeError aparece si intentas guardar un set: JSON no lo conoce
            return False
        
    def añadir(self, registro):
        datos =self.leer()
        datos.append(registro)
        return self.guardar(datos)
    
    def actualizar(self, id_registro, cambios):
        datos =self.leer()
        
        for registro in datos:
            if registro["id"] == id_registro:
                registro.update(cambios)
                
            return self.guardar(datos)
        return False
    
    def eliminar(self, id_registro):
        datos = self.leer()
        
        nuevos_datos = [registro for registro in datos if registro["id"] != id_registro]
        if len(nuevos_datos) == len(datos):
            return False

        return self.guardar(nuevos_datos)