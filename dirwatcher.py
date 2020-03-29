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
""".format(str(startTime)))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ch.setFormatter(formatter)
logger.addHandler(ch)

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
        '-i', '--interval', help='set the polling interval')
    parser.add_argument(
        '-e', '--extension', help='file extensions to search for')
    parser.add_argument('magic', help='The magic sauce to look for')

    return parser

def no_dir(directory):
    makedir = input(f"Would you like to create a directory named: {directory} ? Y/n: ")
    if (makedir[0].lower() == "y"):
        logger.info(f"Makeing new directory: {directory}")
        os.mkdir(directory)
    else:
        logger.warning("Continuing without making a new dir")

all_files = {}

def dirwatch(magic = "magic text", directory = "./", extension="txt"):
    logger.info("checking...")
    for root, _, files in os.walk(directory, topdown=True):
        for _file in files:
            if _file.split(".")[-1] == extension.split(".")[-1]:
                if _file not in all_files.keys():
                    logger.info(f"New file {os.path.join(root, _file)} found")
                    with open(os.path.join(root, _file), "r") as f:
                        counter = 0
                        for line in f.readlines():
                            if magic.lower() in line.lower():
                                logger.info(f"!! MAGIC FOUND !! file: {os.path.join(root, _file)} line: {counter+1}")
                            counter += 1
                        all_files.update({_file:counter})
                else:
                    with open(os.path.join(root, _file), "r") as f:
                        for i, line in enumerate(f.readlines(), start=1):
                            if(i > all_files[_file]):
                                logger.info(f"New line found in file: {os.path.join(root, _file)}")
                                if magic.lower() in line.lower():
                                    logger.info(f"!! MAGIC FOUND !! file: {os.path.join(root, _file)} line: {i}")
                                all_files.update({_file:i})
        if len(files) < len(all_files.keys()):
            keys = all_files.keys()
            for removed_file in keys:
                if removed_file not in files:
                    logger.info(f"File {os.path.join(root, removed_file)} was removed from the directory")
                    all_files.pop(removed_file)


def main(args):
    # Hook these two signals from the OS .. 
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called if OS sends either of these to my process.
    
    parser = create_parser()

    if not args:
        parser.print_usage()
        sys.exit(1)

    parsed_args = parser.parse_args(args)
    
    magic = parsed_args.magic
    directory = "./" if not parsed_args.dir else parsed_args.dir
    polling_int = 3 if not parsed_args.interval else parsed_args.interval
    extension = ".txt" if not parsed_args.extension else parsed_args.extension
    
    logger.info(f"Searching '{directory}' checking '{extension}' files for '{magic}'.")

    while not exit_flag:
        if not os.path.isdir(directory):
            logger.error("No direcotry found with path: " + directory)
            no_dir(directory)
        
        dirwatch(magic=magic, directory=directory, extension=extension)
        # put a sleep inside my while loop so I don't peg the cpu usage at 100%
        time.sleep(polling_int)

if __name__ == '__main__':
    main(sys.argv[1:])