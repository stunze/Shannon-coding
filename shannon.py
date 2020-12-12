
#viskas bus gerai Zivile, susigaudysi

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
        p = word.count(letter)/length
        probTable.update({letter: p})   # e.g. {'a':0.25}

    sorted_probTable = sorted(probTable.items(), key=lambda x: x[1], reverse=True)

    return sorted_probTable


if __name__ == '__main__':
    word = read_input_from_file("test.txt")
    table = probability_table(word)
    print(table)
