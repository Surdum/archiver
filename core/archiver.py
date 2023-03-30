from settings import *
from utils import get_algorithm, get_algorithm_header, int_to_bytes, int_from_bytes, split_path
import os


def pack(input_paths, output_path, compress_algo=None):
    for path in input_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        if len(path) > 255:
            raise ValueError(f'{path} is too len: {len(path)}')
    if os.path.exists(output_path):
        print('out file exists')

    if compress_algo is None:
        compress_algo = DEFAULT_ALGORITHM
    compressor = compress_algo()

    with open(output_path, 'wb') as out_file:
        out_file.write(HEADER)
        out_file.write(get_algorithm_header(compress_algo))
        for inp_path in input_paths:
            out_file.write(int_to_bytes(len(inp_path.encode())))  # file name byte length
            out_file.write(inp_path.encode())  # file name bytes
            out_file.write(int_to_bytes(os.path.getsize(inp_path)).rjust(4, b'\x00'))
            with open(inp_path, 'rb') as inp_file:
                byte_stream = compressor.compress(inp_file)
                for elem in byte_stream:
                    out_file.write(elem)
    return True


def unpack(input_path, output_path):
    if not os.path.exists(input_path):
        raise FileNotFoundError(input_path)

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    with open(input_path, 'rb') as input_file:
        if HEADER != input_file.read(len(HEADER)):
            raise Exception('Input file has invalid header')
        alg = get_algorithm(input_file.read(1))
        compressor = alg()
        byte_stream = compressor.decompress(input_file)
        eof = not bool(next(byte_stream))

        while not eof:
            b = input_file.read(1)
            if not b:
                break
            filename_len = int_from_bytes(b)
            print(f'filename_len: {filename_len}')
            if not filename_len:
                break
            file_path = os.path.join(output_path, input_file.read(filename_len).decode())
            print(f'file_path: {file_path}')
            dirs = split_path(file_path)[:-1]
            print(dirs)
            for i in range(1, len(dirs) + 1):
                p = os.path.join(*dirs[:i])
                if not os.path.exists(p):
                    os.mkdir(p)
            content_len = int_from_bytes(input_file.read(4))
            print(f'content_len: {content_len}')
            with open(os.path.join(file_path), 'wb') as out_file:
                while content_len > 0:
                    _decoded_bytes = next(byte_stream)
                    out_file.write(_decoded_bytes)
                    content_len -= len(_decoded_bytes)
    return True






