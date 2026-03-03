import os
from datetime import datetime

def save_file(content, file_name):
    with open(file_name, "w") as f:
        f.write(content)