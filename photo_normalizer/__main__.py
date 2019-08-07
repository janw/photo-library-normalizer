import sys
import logging

from photo_normalizer import Normalizer


def main(argv):
    logging.basicConfig(level=logging.DEBUG, format="%(msg)s")
    n = Normalizer(*argv)
    n.run()


main(sys.argv[1:])
