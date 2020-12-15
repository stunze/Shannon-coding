from bitarray import bitarray

Base = 2
Byte = 8


def read_input_from_file(filename: str) -> str:
    try:
        with open(filename, mode='r') as file:  # reading characters from file
            word = file.read()
        return word
    except OSError:
        print("Failas nerastas.")


def frequency_table(word: list) -> dict:
    differentValues = (word)
    probTable = {}
    length = len(word)

    for letter in differentValues:
        p = word.count(letter)
        probTable.update({letter: p})  # e.g. {'a':0.25}

    # PATAISYTA DALIS. Buvo klaida nes grazindavo sarasa, o ne zodyna
    sorted_tuples = sorted(probTable.items(), key=lambda x: x[1], reverse=True)  # grazina surikiuota poru SARASA
    sorted_probTable = {k: v for k, v in sorted_tuples}  # is poru SARASO i zodyna

    return sorted_probTable


def length_of_bin_from_freq(frequency: int, data_len: int) -> int:
    total_sum = frequency
    counter = 0
    while total_sum < data_len:
        total_sum *= Base
        counter += 1
    return counter


def int_to_bin(value: float, length: int, dataSize: int) -> bitarray:
    bits = bitarray()
    newNum = value
    for i in range(0, length):
        newNum *= 2
        if newNum > dataSize:
            bits.append(True)
            newNum -= dataSize
        else:
            bits.append(False)
    return bits


def to_binary_table(probTable: dict, dataSize: int) -> dict:
    sum = 0
    binaryTable = {}
    for key, value in probTable.items():
        bit_len = length_of_bin_from_freq(value, dataSize)
        bits = int_to_bin(sum, bit_len, dataSize)
        binaryTable.update({key: bits})  # format(<the_integer>, "<0><width_of_string><format_specifier>")
        sum += value
    return binaryTable


def word_to_bin(word: str, binDict: dict) -> bitarray:
    bits = bitarray()
    for c in word:
        c_bits = binDict.get(c)
        bits += c_bits

    return bits


def write_output_to_file(table: dict, text: bitarray, filename: str) -> bool:
    try:
        with open(filename, mode='wb') as file:  # reading characters from file
            list_of_entries = list(table.values())
            total_bits = 0
            tableDataToBitArray = bitarray()

            for k, v in table.items():
                total_bits += 2 * Byte + len(v)
                tableDataToBitArray += bitarray(format(ord(k), 'b'))
                tableDataToBitArray += v



            diff = 0 + total_bits % 8
            print(int((total_bits - diff) / Byte))
            tableSize = bitarray(f'{int((total_bits - diff) / Byte):016b}')
            tableSizepadding = bitarray(f'{diff:08b}')
            extraZeros = bitarray(diff * '0')


            tableSize.tofile(file)
            tableSizepadding.tofile(file)
            extraZeros.tofile(file)
            tableDataToBitArray.tofile(file)

            text.tofile(file)


            return True

    except OSError:
        print("Failas nerastas.")
    return False


def prepare_to_write(table: dict, text: str) -> list:
    toWrite = ""


def shannon_encoder(inputFile: str, outputFile: str):
    word = read_input_from_file(inputFile)
    table_of_probabilities = frequency_table(word)

    table_of_binary_values = to_binary_table(table_of_probabilities, len(word))
    text_in_binary = word_to_bin(word, table_of_binary_values)
    # print(word)
    print(table_of_binary_values)
    # print(text_in_binary)
    prepare_to_write(table_of_binary_values, text_in_binary)
    write_output_to_file(table_of_binary_values, text_in_binary, outputFile)


if __name__ == '__main__':
    shannon_encoder("test.txt", "answer.bin")
