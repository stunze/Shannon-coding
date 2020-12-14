import math
from bitarray import bitarray

Base = 2


def read_input_from_file(filename: list) -> str:
    try:
        with open(filename, mode='r') as file:  # reading characters from file
            word = file.read()
        return word
    except OSError:
        print("Failas nerastas.")


def probability_table(word: list) -> dict:
    differentValues = (word)
    probTable = {}
    length = len(word)

    for letter in differentValues:
        p = word.count(letter) / length
        probTable.update({letter: p})  # e.g. {'a':0.25}

    # PATAISYTA DALIS. Buvo klaida nes grazindavo sarasa, o ne zodyna
    sorted_tuples = sorted(probTable.items(), key=lambda x: x[1], reverse=True)  # grazina surikiuota poru SARASA
    sorted_probTable = {k: v for k, v in sorted_tuples}  # is poru SARASO i zodyna

    return sorted_probTable


def length_of_bin_from_prob(probability: float) -> int:
    log_len = math.log(probability, Base)
    return math.ceil(-log_len)


def float_to_bin(value: float, length: int) -> bitarray:
    bits = bitarray()
    newNum = value
    for i in range(0, length):
        newNum *= 2
        if newNum > 1:
            bits.append(True)
            newNum -= 1
        else:
            bits.append(False)
    return bits


def to_binary_table(probTable: dict) -> dict:
    sum = 0
    binaryTable = {}
    for key, value in probTable.items():
        bit_len = length_of_bin_from_prob(value)
        bits =  float_to_bin(sum, bit_len)
        binaryTable.update({key: bits})  # format(<the_integer>, "<0><width_of_string><format_specifier>")
        sum += value
    return binaryTable


if __name__ == '__main__':
    word = read_input_from_file("test.txt")
    table = probability_table(word)
    bTable = to_binary_table(table)
    print(bTable)
