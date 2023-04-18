from .base import Compressor
from .mock import Mock
from .rle import RLE
from .huffman import Huffman
from .brrle import BRRLE

COMPRESSION_ALGORITHMS = [(Mock, 0x0), (RLE, 0x1), (Huffman, 0x2), (BRRLE, 0x3)]
