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


def read_gds(path: str) -> bytes:
    """
    Чтение бинарного файла с расширением *.gds.
    """
    if not os.path.exists(path):
        raise ValueError("ERROR: Указан невалидный путь к *.gds")

    with open(path, mode="rb") as f:
        binary_data = f.read()

    # Препроцессинг бинарных данных
    binary_data = binary_data.replace(b"\r", b"")
    # binary_data = binary_data.replace(b"\x00\x04\x0c\x00\x00\x06\x02\x00\x03\x00\x06\x16\x024\xa4"
    #                                   b"\x00\x06\x17\x01\x00\x00\x00\x08\x0f\x03\xff\xff\xff\xf0"
    #                                   b"\x00\x06\x1a\x01\x00\x00\x00\x0c\x10\x03\xff\xff\xfb\x82"
    #                                   b"\x00\x00;.\x00p\x19\x06Generated with the LayoutEditor "
    #                                   b"(This message will NOT added in any commercial version of"
    #                                   b" the LayoutEditor.)\x00\x04\x11\x00",
    #                                   b"")
    return binary_data


def _get_length(two_bytes: bytes) -> int:
    """
    Получение длины полезной нагрузки.
    """
    return int.from_bytes(two_bytes, "big")


def _get_type(two_bytes: bytes):
    """
    Получение типа объекта структуры.
    """
    try:
        return StructObjectType(two_bytes)
    except Exception:
        return None
        # return str(hex(_get_length(two_bytes)))


def _analyze(data: bytes, obj_type: StructObjectType) -> None:
    """
    Анализ полезной нагрузки пакета.
    """
    write_string = ""

    data_type = obj_type
    if isinstance(obj_type, StructObjectType):
        data_type = str(obj_type.value[1])

    # Обработка HEADER
    if obj_type == StructObjectType.HEADER:
        write_string += "Header (" + data_type + ")  " + str(_get_length(data))
    # Обработка BGNLIB / BGNSTR
    elif obj_type == StructObjectType.BGNLIB or obj_type == StructObjectType.BGNSTR:
        # В зависимости от типа пакета - разный заголовок
        if obj_type == StructObjectType.BGNLIB:
            write_string += "BgnLib (" + data_type + ")  "
        else:
            write_string += "\tBgnStr (" + data_type + ")  "

        while data:
            # Получение слова
            write_string += str(_get_length(data[0:2])) + ", "
            # Удаление обработанных данных
            data = data[2:]
        # Удаление последней запятой
        write_string = write_string[:len(write_string)-2]
    # Обработка LIBNAME
    elif obj_type == StructObjectType.LIBNAME:
        # Удаление нулевых символов
        data = data.replace(b'\x00', b'')
        write_string += "\tLibName (" + data_type + ")  \'" + data.decode("ascii") + "\'"
    # Обработка STRNAME
    elif obj_type == StructObjectType.STRNAME:
        # Удаление нулевых символов
        data = data.replace(b'\x00', b'')
        write_string += "\t\tStrName (" + data_type + ")  \'" + data.decode("ascii") + "\'"
    # TODO: Обработка UNITS
    elif obj_type == StructObjectType.UNITS:
        data = b"\x39\x44\xb8\x2f\xa0\x9b\x5a\x51"
        write_string += "\tUnits (" + data_type + ")  "
    # Обработка BOUNDARY
    elif obj_type == StructObjectType.BOUNDARY:
        write_string += "\t\tBoundary (" + data_type + ")  "
    # Обработка LAYER
    elif obj_type == StructObjectType.LAYER:
        write_string += "\t\t\tLayer (" + data_type + ")  " + str(_get_length(data))
    # Обработка ENDEL
    elif obj_type == StructObjectType.ENDEL:
        write_string += "\t\tEndEl (" + data_type + ")  "
    # Обработка ENDSTR
    elif obj_type == StructObjectType.ENDSTR:
        write_string += "\tEndStr (" + data_type + ")  "
    # Обработка неопознанного пакета
    else:
        write_string += "\t\t\tUnknown (" + data_type + ") (" + data_type[-2] + ")  " + str(_get_length(data))

    print(write_string)


def parse_gds(bin_data: bytes) -> None:
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
            print(bin_data)
            raise ValueError("Не удалось обработать пакет")

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
    print(binary)

    try:
        # Парсинг бинарных данных
        parse_gds(binary)
    except ValueError as e:
        print("ERROR: " + str(e))
        exit(-1)
