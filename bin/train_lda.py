import sys
import gzip
from argparse import ArgumentParser

from path import path
from amazon import LDA

def main():
    argparser = ArgumentParser()
    argparser.add_argument('input_file')

    args = argparser.parse_args()

    input_file = path(args.input_file)
    if not input_file.exists():
        print "Input file does not exist"
        sys.exit(1)

    with gzip.open(input_file) as fp:
        lda = LDA(fp,
                  num_topics=30,
                  D=950000,
                  bit_precision=20)
        lda.run(True)

