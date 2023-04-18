from compression.base import Compressor
import io


class Rule:
    def __init__(self, count, values):
        self.count = count
        self.values = values

    def __str__(self):
        return f'({self.count}, {self.values})'

    def __repr__(self):
        return f'({self.count}, {self.values})'


class BRRLE(Compressor):  # Bit-Rules RLE
    def compress(self, _bytes, **kwargs):
        from utils import int_to_byte, int_from_bytes, int_to_bytes
        bit_rules = [[] for _ in range(8)]
        b = _bytes.read(1)
        while b:
            bits = bin(int_from_bytes(b))[2:].rjust(8, '0')
            for i, bit in enumerate(bits):
                if bit_rules[i] and bit_rules[i][-1].values[-1] == int(bit):
                    bit_rules[i][-1].count += 1
                else:
                    bit_rules[i].append(Rule(1, [int(bit)]))
            b = _bytes.read(1)
        optimized_rules = [[] for _ in range(8)]
        right_p = 127  # можно поиграть, значение должно быть n байт в степени m - 1
        for i in range(8):  # оптимизация путём группировки
            temp_rule = Rule(0, [])
            for bit_rule in bit_rules[i]:
                if bit_rule.count < 17 and (temp_rule.count + bit_rule.count) < right_p + 1:
                    temp_rule.count += bit_rule.count
                    for _ in range(bit_rule.count):
                        temp_rule.values.append(bit_rule.values[0])
                    continue
                if temp_rule.count != 0:
                    optimized_rules[i].append(temp_rule)
                    temp_rule = Rule(0, [])

                if bit_rule.count > right_p:
                    p = bit_rule.count
                    while p > right_p:
                        optimized_rules[i].append(Rule(right_p, bit_rule.values))
                        p -= right_p
                    if p:
                        optimized_rules[i].append(Rule(p, bit_rule.values))
                else:
                    optimized_rules[i].append(bit_rule)
            if temp_rule.count != 0:
                optimized_rules[i].append(temp_rule)
        rule_len = []
        for rules in optimized_rules:
            rule_len.append(len(rules))

        max_len = max([len(int_to_bytes(r)) for r in rule_len])
        yield int_to_byte(max_len)
        for rules in optimized_rules:  # пишем правила записи
            yield int_to_bytes(len(rules), length=max_len)  # количество правил в последовательности
            for rule in rules:
                if len(rule.values) > 1:
                    yield int_to_bytes(-rule.count, signed=True, length=1)
                else:
                    yield int_to_bytes(rule.count, signed=True, length=1)
        buffer = ''
        for rules in optimized_rules:  # пишем последовательности битов для записи
            for rule in rules:
                for bit in rule.values:
                    buffer += str(bit)
                while len(buffer) >= 8:
                    yield int_to_byte(self.bits_to_int(buffer[:8]))
                    buffer = buffer[8:]

        if buffer:
            yield int_to_byte(self.bits_to_int(buffer.ljust(8, '0')))

    @staticmethod
    def bits_to_int(bits_str):
        eta = 0b0000000
        for i in range(len(bits_str) - 1, -1, -1):
            if bits_str[len(bits_str) - 1 - i] == '1':
                eta |= 0b1 << i
        return eta

    def decompress(self, _bytes: io.BytesIO, **kwargs):
        from utils import int_to_byte, int_from_bytes

        def read_bits(stream):
            _b = stream.read(1)
            while _b:
                n = int_from_bytes(_b)
                for bit_index in range(7, -1, -1):
                    yield str(int(bool(n & (1 << bit_index))))
                _b = stream.read(1)

        counter_len = int_from_bytes(_bytes.read(1))
        bit_rules = [[] for _ in range(8)]
        for i in range(8):  # читаем правила для каждого бита
            rule_count = int_from_bytes(_bytes.read(counter_len))
            for j in range(rule_count):
                b = _bytes.read(1)
                bit_rules[i].append(int_from_bytes(b, signed=True))
        bit_reader = read_bits(_bytes)
        parts = ['' for _ in range(8)]
        for i, rules in enumerate(bit_rules):
            for bit_count in rules:
                if bit_count > 0:
                    bit = next(bit_reader)
                    for _ in range(bit_count):
                        parts[i] += bit
                else:
                    for _ in range(abs(bit_count)):
                        bit = next(bit_reader)
                        parts[i] += bit
        buffer = ''
        for k in range(sum([len(p) for p in parts]) // 8):
            for i in range(8):
                buffer += parts[i][k]
            yield int_to_byte(self.bits_to_int(buffer))
            buffer = ''
