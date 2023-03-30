import argparse
from utils import file_info
from core.archiver import pack, unpack


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Archiver with compression")
    parser.add_argument('mode', type=str, choices=['pack', 'unpack'])
    parser.add_argument(dest='inp_paths', metavar='PATH', action='extend', type=str, nargs='+', help='Input file(s)')
    parser.add_argument('-o', dest='out_path', metavar='OUTPUT_PATH', help='Output file')
    # parser.add_argument('-alg', dest='algorithm', metavar='ALGORITHM', help='Compression algorithm')

    args = parser.parse_args()

    if args.mode == 'pack':
        success = pack(args.inp_paths, args.out_path)
        if success:
            print(file_info(args.out_path))
    elif args.mode == 'unpack':
        unpack(args.inp_paths[0], args.out_path)






