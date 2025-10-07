from functools import wraps
import time
import yaml
import os


def msg_warn(msg):
    return '\33[33m%s\033[0m' % msg   # Amarillo

def msg_succ(msg):
    return '\33[32m%s\033[0m' % msg   # Verde

def msg_error(msg):
    return '\33[31m%s\033[0m' % msg   # Rojo

def seguimiento_funciones(func):
    @wraps(func)
    def wrapper(*args,  **kwargs):
        print(msg_succ("%s[INFO] Inicia la Funcion %s" % (time.strftime('%H:%M:%S'), func.__name__)))
        f = func(*args, **kwargs)
        print(msg_succ("%s[INFO] Finaliza la Funcion %s" % (time.strftime('%H:%M:%S'), func.__name__)))
        return f
    return wrapper

def load_config(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Archivo de configuración no encontrado: {path}")
    with open(path, "r") as f:
        return yaml.safe_load(f)
    
def calcular_tiempo_ejecucion(val_inicio_ejecucion, val_fin_ejecucion):
    duracion_total_segundos = int((val_fin_ejecucion - val_inicio_ejecucion).total_seconds())
    horas = duracion_total_segundos // 3600
    minutos = (duracion_total_segundos % 3600) // 60
    segundos = duracion_total_segundos % 60
    print(f"{val_fin_ejecucion.strftime('%Y-%m-%d %H:%M:%S')}: Tiempo de ejecución es: {horas}h {minutos}min {segundos}s")
    tiempo_str = f"{horas}:{minutos}:{segundos}"
    return tiempo_str