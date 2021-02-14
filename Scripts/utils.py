import logging
import numpy as np
from subprocess import Popen, PIPE, STDOUT
import os
import glob


def get_proteins(path: str, test_path: str, single_mode: str = None, black_list: dict = None) -> (dict, dict):
    # First we will save the proteins names and paths to be read by the SDP Matlab script;
    # And also, create the test paths for each one, saving it on a dictionary
    logger = logging.getLogger('root.get_proteins')
    if type(single_mode) == str:
        logger.info(':: System Report: Single mode enabled!')
        node = single_mode
        # check if the given protein belongs to the black_list
        if (black_list is not None) and (node in black_list.items()):
            return exit(f':: System Exit Report: {__name__}.get_proteins received a black listed protein: {node}')
        # check if the given protein belongs to the specified 'path'
        if os.path.isdir(f'{path}\\{node}'):
            # get the directory of the chosen protein; dict(protein_name: its_dir);
            logger.info(f':: System Report: Protein {node} was successfully loaded.')
            proteins = {f'{node}': f'{path}\\{node}'}  # dict
        else:
            # the chosen protein don't belong to this 'path'
            logger.warning(f':: System Report: specified protein [{node}] could not be found at: {path}!')
            return exit(f':: System Exit Report: {__name__}.get_proteins failed to recognize the given node: {node}')

        # Create the node test directory
        os.makedirs(f'{test_path}\\{node}')

        # Saves the directory for further uses
        proteins_test_paths = {f"{node}": f'{test_path}\\{node}'}
        logger.info(f":: System Report: Directory {proteins_test_paths[f'{node}']} successfully created.")

    else:
        # get the names and directories for all the available proteins; dict(protein_name: its_dir);
        proteins = dict(zip(os.listdir(path), glob.glob(f"{path}\\*")))  # dict
        logger.info(f':: System Report: All available nodes at {path} were successfully loaded.')

        # Create the nodes test directories
        proteins_test_paths = {}
        for node in proteins.keys():
            # check if the given protein belongs to the black_list
            if (black_list is not None) and (node in black_list.items()):
                logger.debug(f':: System Exit Report: {__name__}.get_proteins received a black listed protein: {node}')
                pass
            # Create the node test directory
            os.makedirs(f'{test_path}\\{node}')

            # Saves the directory for further uses
            proteins_test_paths[f'{node}'] = f'{test_path}\\{node}'
            logger.info(f":: System Report: Directory {proteins_test_paths[f'{node}']} successfully created.")

    return proteins, proteins_test_paths


def open_pdb_file(dir_pdb: str, debug_mode: bool = False):
    """"This function aims to open the correspondent .pdb file for a given node."""
    # Get the current logger
    logger = logging.getLogger('root.utils.open_pdb')
    if debug_mode:
        logger.setLevel(10)
    try:
        # open PDB file (as an np-array):
        pdb = np.genfromtxt(dir_pdb, dtype="str")

    except FileNotFoundError as e:
        logger.warning(":: System Report: PDB file not found!")
        logger.error(f":: {e}")
        pdb = []
        logger.warning(":: System Report: The process was interrupted!")
        # If no pdb file was found we can't proceed with this node.
        return exit()
    logger.debug(":: System Report: PDB file read complete!")
    return pdb


def launch_sdp(path):
    """ This code creates de run bash line, to start the Matlab functions for the SDP program"""
    # Get Logger
    logger = logging.getLogger('root.utils.matlab_sdp')

    # Look for the Matlab current working directory, and set the environment code for SDP;
    # Get Matlab run bash line:
    matlab_scripts = path + '\\Matlab\\PDB_aux.m'

    # TODO: This code works for matlab R2019b and later. For earlier versions we should add an equivalent command.
    run_command = 'matlab -batch "addpath(' + f"'{matlab_scripts}'); try sdpaux; catch ME; end" + '"'

    # Run and wait for process finishes
    try:
        process = Popen(run_command, stdout=PIPE, stderr=STDOUT)
        while True:
            try:
                line = process.stdout.readline()
            except StopIteration:
                break
            if line != b'':
                if isinstance(line, bytes):
                    line = line.decode('utf-8')
                logger.info(line.rstrip())
            else:
                break

    except Exception as e:
        logger.warning(f":: System Error Report: Attempt to run Matlab script failed with error: \n {e}.")
