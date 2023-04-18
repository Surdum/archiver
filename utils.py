from compression import COMPRESSION_ALGORITHMS, Compressor, Mock
import typing
import re
import os


PRECALCULATED_BYTE_RANGES = [256**i for i in range(1, 9)]


def get_algorithm_header(alg: typing.Type[Compressor]) -> bytes:
    return int_to_bytes([pare[1] for pare in COMPRESSION_ALGORITHMS if pare[0] == alg][0])


def get_algorithm(value: bytes) -> typing.Type[Compressor]:
    return [pare[0] for pare in COMPRESSION_ALGORITHMS if int_to_bytes(pare[1]) == value][0]


def int_to_bytes(number: int, signed=False, length=None) -> bytes:
    if not length:
        if not signed:
            length = number.bit_length() // 8 + 1
        else:
            length = (8 + (number + (number < 0)).bit_length()) // 8
    try:
        return number.to_bytes(length=length, byteorder='big', signed=signed)
    except Exception as e:
        print(number)
        raise e


def int_to_byte(number: int, signed=False) -> bytes:
    return number.to_bytes(length=1, byteorder='big', signed=signed)


def int_from_bytes(binary_data: bytes, signed=False) -> int:
    return int.from_bytes(binary_data, byteorder='big', signed=signed)


def get_name(cls: object) -> str:
    if not isinstance(cls, type):
        cls = cls.__class__
    words = re.findall('[A-Z][^A-Z]*', cls.__name__)
    for i in range(1, len(words)):
        words[i] = words[i].lower()
    return ' '.join(words)


def file_info(filename):
    size = os.path.getsize(filename)
    return f'Name: {filename}\nSize: {size}'


def split_path(s):
    rest, tail = os.path.split(s)
    if rest in ('', os.path.sep):
        return tail,
    return split_path(rest) + (tail,)

