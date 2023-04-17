class Compressor:
    def compress(self, _bytes, **kwargs):
        raise NotImplementedError

    def decompress(self, _bytes, **kwargs):
        raise NotImplementedError
