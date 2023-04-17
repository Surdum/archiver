from compression.base import Compressor
from collections import defaultdict
from queue import PriorityQueue
import io


class Node:
    left: "Node" = None
    right: "Node" = None
    value: bytes
    count: int
    bit: bool

    def __init__(self, count: int, value: bytes):
        self.count = count
        self.value = value

    def __str__(self):
        return f"({self.count} {self.value})"

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        return Node(self.count + other.count, self.value + other.value)


class Huffman(Compressor):
    def compress(self, _bytes, **kwargs):
        from utils import int_to_byte

        b = _bytes.read(1)
        freq_dict = defaultdict(int)
        while b:
            freq_dict[b] += 1
            b = _bytes.read(1)
        _bytes.seek(0)
        alph_flag = [0 for _ in range(32)]  # по биту на букву
        for i in range(256):
            if int_to_byte(i) in freq_dict:
                alph_flag[31 - ((255 - i) // 8)] |= 1 << (7 - i % 8)

        while alph_flag:  # выгружаем в файл битовую маску, показывающую алфавит
            yield int_to_byte(alph_flag.pop(0))
        q = PriorityQueue()
        signs = set()
        for i in range(256):
            count = freq_dict.get(int_to_byte(i), 0)
            if count:
                signs.add(int_to_byte(i))
                q.put([count, int_to_byte(i)])
        values = []
        while not q.empty():
            elem = q.get()
            values.append(Node(*elem))
        while len(values) > 1:
            start_ids = []
            count = 0
            el = values[0]
            for i, elem in enumerate(values):
                if elem.count != el.count:
                    start_ids.append((i - 1, count))
                    el = elem
                    count = 1
                else:
                    count += 1
            if start_ids:
                start_ids.append((len(values) - 1, len(values) - 1 - start_ids[-1][0]))
            else:
                start_ids.append((len(values) - 1, len(values)))
            if start_ids[0][1] > 1:
                left = values[start_ids[0][0] - 1]
                right = values[start_ids[0][0]]
            else:
                left = values[start_ids[0][0]]
                right = values[start_ids[1][0]]
            new_node = left + right
            new_node.left = left
            new_node.right = right
            values.insert(0, new_node)
            values.remove(left)
            values.remove(right)
            values = sorted(values, key=lambda x: x.count)
        parent = values[0]
        for i in range(256):
            b = int_to_byte(i)
            if b in freq_dict:
                yield int_to_byte(len(self.get_code(parent, b)))
        buffer = ''
        for i in range(256):
            b = int_to_byte(i)
            if b in freq_dict:
                buffer += self.get_code(parent, b)
            while len(buffer) >= 8:
                yield int_to_byte(self.str_to_int(buffer[:8]))
                buffer = buffer[8:]
        if buffer:
            yield int_to_byte(self.str_to_int(buffer.ljust(8, '0')))

        b = _bytes.read(1)
        buffer = ''
        while b:
            buffer += self.get_code(parent, b)
            while len(buffer) >= 8:
                yield int_to_byte(self.str_to_int(buffer[:8]))
                buffer = buffer[8:]
            b = _bytes.read(1)
        if buffer:
            yield int_to_byte(self.str_to_int(buffer.ljust(8, '0')))

    def get_code(self, node, code, bit=''):
        if node.value == code:
            return bit or '0'
        if node.left and code in node.left.value:
            return bit + self.get_code(node.left, code, '0')
        if node.right and code in node.right.value:
            return bit + self.get_code(node.right, code, '1')

    @staticmethod
    def str_to_int(bits_str):
        eta = 0b0000000
        for i in range(len(bits_str) - 1, -1, -1):
            if bits_str[len(bits_str) - 1 - i] == '1':
                eta |= 0b1 << i
        return eta

    def decompress(self, _bytes, **kwargs):
        from utils import int_to_byte, int_from_bytes

        def read_bits(stream):
            b = stream.read(1)
            while b:
                n = int_from_bytes(b)
                for bit_index in range(7, -1, -1):
                    yield str(int(bool(n & (1 << bit_index))))
                b = stream.read(1)

        bit_reader = read_bits(io.BytesIO(_bytes.read(32)))
        alph = []
        for i in range(256):
            if next(bit_reader) == '1':
                alph.append(int_to_byte(i))
        bit_length = {}
        for let in alph:
            bit_length[let] = int_from_bytes(_bytes.read(1))
        codes = defaultdict(str)
        bit_reader = read_bits(_bytes)

        for let in alph:
            for i in range(bit_length[let]):
                codes[let] += next(bit_reader)

        parent = Node(0, b'')
        for let, code in codes.items():
            current = parent
            new_node = None
            for bit in code:
                new_node = Node(0, b'')
                if bit == '0':
                    if not current.left:
                        current.left = new_node
                    current = current.left
                else:
                    if not current.right:
                        current.right = new_node
                    current = current.right
            new_node.value = let
        bit_reader = read_bits(_bytes)
        eof = False
        while not eof:
            current = parent
            while current.left or current.right:
                try:
                    bit = next(bit_reader)
                except StopIteration:
                    eof = True
                    break
                if bit == '1':
                    current = current.right
                else:
                    current = current.left
            yield current.value
