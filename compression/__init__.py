from .base import Compressor
from .mock import Mock
from .rle import RLE

COMPRESSION_ALGORITHMS = [(Mock, 0x0), (RLE, 0x1)]
