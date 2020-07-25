import pathlib
import os
import json
import logging

from Scripts.gen_config_file import gen_file as _gen_config_file


def main() -> None:
    """This code verifies the config file information and runs the tests for structural viability"""
    # Set Logging information
    _style = '%(asctime)s %(levelname)-8s :: %(message)s'
    logging.basicConfig(format=_style)

    # Get the current working dir./path;
    current_dir = str(pathlib.Path().absolute())

    # check for config.yaml file
    config_file_path = current_dir + "\\general_config.json"

    # if config file exists continue, else create a new one;
    if os.path.isfile(config_file_path):
        # Get the available configuration file;
        with open(config_file_path) as file:
            config = json.load(file)
        logging.info(":: System Report: Read configuration file complete.\n")
    else:
        logging.info(":: System Report: File not found!")
        logging.info(":: System Report: Creating a new configuration...")
        logging.info(
            ":: Please check the Readme file for information regarding the settings configuration standards.\n")
        config = _gen_config_file(current_dir)

    # run environment tests
    # run structure tests
    # run solvers tests: both phases
    # if all done execute run.py; else check missing information and reload
    return


if __name__ == '__main__':
    main()
