from encoder import *
from decoder import *
import sys

if __name__ == '__main__':
    shannon_encoder("flowers.bmp", "vo.shn", 10)
    shannon_decoder("vo.shn", "flo.bmp")

    # if sys.argv[1] == 'c' and len(sys.argv) == 5 and 16 >= int(sys.argv[4]) >= 2:
    #     shannon_encoder(sys.argv[2], sys.argv[3], int(sys.argv[4]))
    # elif sys.argv[1] == 'd' and len(sys.argv) == 4:
    #     shannon_decoder(sys.argv[2], sys.argv[3])
    # else:
    #     sys.exit("Invalid arguments. Format [c|d] [inputFile.*] [outputFile.*] [k| ]")
