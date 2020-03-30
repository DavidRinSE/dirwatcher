__author__ = "DavidRinSE"  # David Richardson

import signal
import time
import logging
import argparse
import sys
import os
exit_flag = False

startTime = time.time()

print("""
-------------------------------------------------------------------
   Started dirwatcher.py
   Start time was {}
-------------------------------------------------------------------
""".format(time.ctime()))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ch.setFormatter(formatter)
logger.addHandler(ch)

all_files = {}


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT. Other signals can be mapped here as well (SIGHUP?)
    Basically it just sets a global flag, and main() will exit it's loop if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    # log the associated signal name (the python3 way)
    logger.warning('Received ' + signal.Signals(sig_num).name)
    global exit_flag
    exit_flag = True


def create_parser():
    """Create an argument parser object"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--dir', help='destination directory to search')
    parser.add_argument(
        '-i', '--int', help='set the polling interval')
    parser.add_argument(
        '-e', '--ext', help='file extensions to search for')
    parser.add_argument('magic', help='The magic sauce to look for')

    return parser


def new_file(root, _file, magic):
    """
    Search entire new file for magic text
    Log if found, and update the dict with the latest line checked
    """
    logger.info(f"New file {os.path.join(root, _file)} found")
    with open(os.path.join(root, _file), "r") as f:
        counter = 0
        for line in f.readlines():
            if magic.lower() in line.lower():
                logger.info(
                    f"!! MAGIC FOUND !! file: {os.path.join(root, _file)}" +
                    "line: {counter+1}")
            counter += 1
        all_files.update({_file: counter})


def old_file(root, _file, magic):
    """
    Search a file that has already been detected
    Only check lines that have not been tested
    Log if magic is found, and update the dict with latest line tested
    """
    with open(os.path.join(root, _file), "r") as f:
        for i, line in enumerate(f.readlines(), start=1):
            if(i > all_files[_file]):
                logger.info(
                    f"New line found in file: {os.path.join(root, _file)}")
                if magic.lower() in line.lower():
                    logger.info(
                        "!! MAGIC FOUND !! file: " +
                        f"{os.path.join(root, _file)} line: {i}")
                all_files.update({_file: i})


def check_deleted(root, files):
    """
    Loop through known files and the current list of files
    If a known file is missing, log the removal and update dict
    """
    if len(files) < len(all_files.keys()):
        keys = [i for i in all_files.keys()]
        for removed_file in keys:
            if removed_file not in files:
                logger.info(
                    f"File {os.path.join(root, removed_file)}" +
                    " was removed from the directory")
                all_files.pop(removed_file)


def dirwatch(magic="magic text", directory="./", ext="txt"):
    """
    Ran once every polling interval
    Walk the directory
    Loop through the files
    Check new file if it is not in all_files dict
    Check old file otherwise
    """
    logger.info("checking...")
    # Using sacndir over walk becasue it throws an except
    # if dir is missing
    try:
        with os.scandir(directory) as obj:
            files = [entry.name for entry in obj if entry.is_file()]
            for _file in files:
                if _file.split(".")[-1] == ext.split(".")[-1]:
                    if _file not in all_files.keys():
                        new_file(directory, _file, magic)
                    else:
                        old_file(directory, _file, magic)
            check_deleted(directory, files)
    except FileNotFoundError:
        logger.error("No direcotry found with path: " + directory)


def main(args):
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    parser = create_parser()

    if not args:
        parser.print_usage()
        sys.exit(1)

    parsed_args = parser.parse_args(args)

    magic = parsed_args.magic
    directory = "./" if not parsed_args.dir else parsed_args.dir
    polling_int = 3 if not parsed_args.int else parsed_args.int
    ext = ".txt" if not parsed_args.ext else parsed_args.ext

    logger.info(
        f"Searching '{directory}' checking '{ext}' files for '{magic}'.")

    while not exit_flag:
        dirwatch(magic=magic, directory=directory, ext=ext)
        # put a sleep inside my while loop so I don't peg the cpu usage at 100%
        time.sleep(polling_int)

    print("""
        -------------------------------------------------------------------
        Started dirwatcher.py
        Uptime was {}
        -------------------------------------------------------------------
        """.format(str(time.time() - startTime)))


if __name__ == '__main__':
    main(sys.argv[1:])
