import functools
import time

def seguimiento_funciones(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"DEBUG: Ejecutando {func.__name__}")
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"DEBUG: Terminó {func.__name__} en {end_time - start_time:.4f}s")
        return result
    return wrapper

def msg_succ(msg):
    print(f"SUCCESS: {msg}")

def msg_warn(msg):
    print(f"WARNING: {msg}")

def msg_error(msg):
    print(f"ERROR: {msg}")

def msg_info(msg):
    print(f"INFO: {msg}")
