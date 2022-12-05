from enum import Enum


class StructObjectType(Enum):
    """
    Тип объекта структуры.
    """
    HEADER = b"\x00\x02"
    BGNLIB = b"\x01\x02"
    LIBNAME = b"\x02\x06"
    UNITS = b"\x03\x05"
    BGNSTR = b"\x05\x02"
    STRNAME = b"\x06\x06"
    BOUNDARY = b"\x08\x00"
    BOX = b"\x2d\x00"
    LAYER = b"\x0d\x02"
    XY = b"\x10\x03"
    ENDEL = b"\x11\x00"
    ENDSTR = b"\x07\x00"
    ENDLIB = b"\x04\x00"
