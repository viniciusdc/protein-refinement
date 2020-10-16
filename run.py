import os
import logging
import pathlib
import json
import argparse

from datetime import datetime
from Scripts.utils import get_proteins

parser = argparse.ArgumentParser(description="A protein refinement method...")
parser.add_argument("--filename", type=str, help="Input protein name")
args_ops = parser.parse_args()


def check_config():
    logger = logging.getLogger('root.config_check')
    """This verifies if the config.json file is available (if not, runs main.py)"""
    if os.path.isfile('config.json'):
        logger.info(':: System Report: config.json file available, progressing to next phase.')
        with open('config.json') as file:
            config = json.load(file)
        return config
    else:
        logger.warning(':: System Report: config.json file not found, possible first try run ?')
        logger.warning(':: System Report: as an attempt to solve the problem a new config.json will be created.')
        try:
            os.system('python Scripts/gen_config_file.py --silent=True')
            logger.info(':: System Report: A new config.json [standard] file was created.')
            # load config.json
            with open('config.json') as file:
                config = json.load(file)
            return config

        except Exception as ee:
            logger.warning(f'System Report: During the creation of config.json an error occurred {ee}.')
            return exit(':: System Report: An error occurred loading the config.json file!')


def main(args):
    # ###################### Pre initialization #######################
    # Get the current working dir. path;
    current_dir = str(pathlib.Path().absolute())

    # Get current time
    now = datetime.now()
    current_time = now.strftime("%d-%m-%Y") + '_' + now.strftime("%H_%M_%S")

    # ###################### Set LOG environment #######################
    # set up logging to file - see previous section for more details
    logger_path = f'{current_dir}/LOGs/{current_time}.log'
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-20s: %(levelname)-8s %(message)s',
                        filename=logger_path,
                        filemode='w')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    # set a format which is simpler for console use
    formatter = logging.Formatter('[%(name)-20s]: [%(levelname)s] %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    # Now, we can log to the root logger, or any other logger. First the root...
    logging.info(f':: System Report: The process has started on {now}.')

    # ###################### Load configurations #######################
    # Check for config.json
    config = check_config()
    proteins_path = config['paths']['proteins_path']

    # ###################### Start Tests Config #######################
    logging.info(':: System Report: Creating the test directory.')

    directory = f'\\Tests\\{current_time}'
    test_path = current_dir + directory
    # Create the directory
    os.mkdir(test_path)

    # check for load mode, the proteins dict contains the protein(s) name (aka, node) and it's directory path.
    logging.info(':: System Report: Checking operation mode and generating test node(s) path(s).')

    if args.filename:
        # run in single mode (only one protein will be loaded)
        proteins, test_proteins = get_proteins(proteins_path, test_path, single_mode=args.filename)
    else:
        # run file test-set (a list of proteins will be loaded)
        proteins, test_proteins = get_proteins(proteins_path, test_path)

    return


if __name__ == '__main__':
    main(args_ops)
