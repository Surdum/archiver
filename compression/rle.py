from compression.base import Compressor


class RLE(Compressor):
    def compress(self, _bytes, **kwargs):
        from utils import int_to_byte

        sign = _bytes.read(1)
        number = 1
        alone_stack = []
        while True:
            b = _bytes.read(1)
            if not b:
                break
            if b == sign:
                number += 1
                if number > 1 and alone_stack:
                    yield int_to_byte(-len(alone_stack), signed=True)
                    while alone_stack:
                        yield alone_stack.pop(0)
            elif b != sign and number == 1:
                alone_stack.append(sign)
                sign = b
                number = 1
            else:
                yield int_to_byte(number, signed=True) + sign
                number = 1
                sign = b
            if number == 127:
                yield int_to_byte(number, signed=True) + sign
                number = 0
            if len(alone_stack) == 127:
                yield int_to_byte(-len(alone_stack), signed=True)
                while alone_stack:
                    yield alone_stack.pop(0)
        if alone_stack:
            yield int_to_byte(-len(alone_stack), signed=True)
            while alone_stack:
                yield alone_stack.pop(0)
        yield int_to_byte(number, signed=True) + sign
        return b''

    def decompress(self, _bytes, **kwargs):
        from utils import int_from_bytes
        # init settings here
        while True:
            number = int_from_bytes(_bytes.read(1), signed=True)
            if not number:
                break
            if number < 0:
                for _ in range(abs(number)):
                    yield _bytes.read(1)
            else:
                b = _bytes.read(1)
                for _ in range(number):
                    yield b
        return b''
