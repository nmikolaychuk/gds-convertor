import os
import sys
import struct

from enums import *

# Путь до корневой директории проекта.
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Длина блока, содержащего значение длины данных.
SIZE_LENGTH = 2
# Путь для сохранения результата по умолчанию.
DEFAULT_SAVE_PATH = os.path.join(ROOT_DIR, "../etc/result.txt")
# Путь для конвертируемого файла.
GDS_PATH = os.path.join(ROOT_DIR, "../etc/LR1.GDS_example_flat.gds")


def read_gds(path: str) -> str:
    """
    Чтение бинарного файла с расширением *.gds.
    """
    if not os.path.exists(path):
        return

    with open(path, mode="rb") as f:
        binary_data = f.read()
    return binary_data


def _get_length(two_bytes: str) -> int:
    """
    Получение длины полезной нагрузки.
    """
    return int.from_bytes(two_bytes, "big")


def _get_type(two_bytes: str) -> StructObjectType:
    """
    Получение типа объекта структуры.
    """
    try:
        return StructObjectType(two_bytes)
    except Exception:
        return None

def _analyze(data: str, obj_type: StructObjectType) -> None:
    """
    Анализ полезной нагрузки пакета.
    """
    write_string = ""
    if obj_type == StructObjectType.BGNLIB:
        # Ожидается 12 слов каждый по 2 байта
        write_string += "BgnLib  "
        while data:
            # Получение слова
            write_string += str(_get_length(data[0:2])) + ", "
            # Удаление обработанных данных
            data = data[2:]
        # Удаление последней запятой
        write_string = write_string[:len(write_string)-2] + "\n"
    
    elif obj_type == StructObjectType.LIBNAME:
        write_string += "LibName  \'" + data.decode("ascii") + "\'\n"

    elif obj_type == StructObjectType.UNITS:
        data = b"\x3E\x41\x89\x37\x4B\xC6\xA7\xEF\x39\x44\xB8\x2F\xA0\x9B\x5A\x51"
        write_string += "Units  "
        print(struct.unpack('!d', data[0:8]))
        

def parse_gds(bin_data: str) -> str:
    """
    Парсинг бинарных данных.
    """
    # Пока не пустой - парсинг
    while bin_data:
        # Получение длины данных
        length = _get_length(bin_data[0:SIZE_LENGTH])
        # Получение типа объекта структуры
        obj_type = _get_type(bin_data[SIZE_LENGTH:2*SIZE_LENGTH])
        if obj_type is None:
            print("Обнаружен некорректный пакет")
            break

        # Получение данных
        data = bin_data[2*SIZE_LENGTH:length]
        # Обработка данных
        _analyze(data, obj_type)
        # Удаление обработанных данных
        bin_data = bin_data[length:]


if __name__ == "__main__":
    # Если не указан путь для сохранения - использовать по умолчанию
    if len(sys.argv) < 2:
        save_path = DEFAULT_SAVE_PATH
    else:
        # Считывание аргументов
        save_path = sys.argv[1]
    print("Путь для сохранения:", save_path)

    # Чтение gds файла
    binary = read_gds(GDS_PATH)
    # Парсинг бинарных данных
    parse_gds(binary)
