import pathlib
import json
import logging

from Scripts.gen_config_file import gen_file as _gen_config_file
from Scripts.tests import *


def check_requirements() -> None:
    logger = logging.getLogger('main.check_requirements')
    # run in silent mode
    os.system('conda config --set always_yes True')
    # select conda-forge as strict channel
    os.system('conda config --prepend channels conda-forge')
    # run conda update at all the available packages
    os.system('conda update --all')
    # run conda install requirements
    os.system('conda install --quiet --yes --file Requirements/requirements')
    logger.info(":: System Report: Conda packages configuration complete.\n")


def main() -> None:
    """This code verifies the config file information and runs the tests for structural viability"""
    # Set Logging information
    formatter = '[%(name)-20s]: [%(levelname)s] %(message)s'
    logging.basicConfig(format=formatter)
    logging.getLogger().setLevel(logging.INFO)
    logger = logging.getLogger('main')

    # Now, we can log to the root logger, or any other logger. First the root...
    logger.info(':: System Announcement: Process started')

    # run environment tests
    try:
        logger.info(':: Check conda installation and required packages')
        check_requirements()
    except Exception as e:
        print('Could not install the required packages, please try again in a few minutes.')
        print(f'System Exception: {e}')

    # Get the current working dir./path;
    current_dir = str(pathlib.Path().absolute())

    # check for config.yaml file
    config_file_path = current_dir + "\\config.json"

    # if config file exists continue, else create a new one;
    if os.path.isfile(config_file_path):
        # Get the available configuration file;
        with open(config_file_path) as file:
            json.load(file)
        logger.info(":: System Report: Read configuration file complete.\n")
    else:
        logger.info(":: System Report: config.json file not found!")
        logger.info(":: System Report: Creating a new configuration...")
        logger.info(
            ":: Please check the Readme file for information regarding the settings configuration standards.\n")
        _gen_config_file(current_dir)

    # TODO: general tests
    routine_test()

    return


if __name__ == '__main__':
    pass  # main()
