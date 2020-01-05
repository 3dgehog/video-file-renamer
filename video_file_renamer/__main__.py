import os
import logging
import argparse

from .app import App


def main():
    # Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose",
                        help="Displays debug messages",
                        action="store_true")
    parser.add_argument('-d', '--directory',
                        help="Directory to scan",
                        action='store',
                        required=True)
    args = parser.parse_args()

    # Setup Logger
    logger = logging.getLogger('vfr')
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler('vfr.log')
    fh.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)

    # Set log level based on input arguments
    if args.verbose:
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)

    file_format = logging.Formatter(
        '%(asctime)s - %(levelname)s:%(message)s')
    console_format = logging.Formatter(
        '%(message)s')

    ch.setFormatter(console_format)
    fh.setFormatter(file_format)

    logger.addHandler(ch)
    logger.addHandler(fh)

    if args.verbose:
        logger.info("Running in verbose mode")

    # App
    app = App(os.environ["API_KEY"])

    app.scan_folder(args.directory)


if __name__ == "__main__":
    main()
