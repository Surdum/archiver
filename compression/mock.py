from compression.base import Compressor


class Mock(Compressor):
    def compress(self, _bytes):
        b = _bytes.read(1)
        while b:
            yield b
            b = _bytes.read(1)
        return b''

    def decompress(self, _bytes):
        # init settings here
        yield 'not eof'
        b = 'wow'
        while b:
            b = _bytes.read(1)
            yield b
        return b''
