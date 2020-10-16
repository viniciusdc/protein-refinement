import logging
import os
import glob


def get_proteins(path: str, test_path: str, single_mode: str = None) -> (dict, dict):
    logger = logging.getLogger('root.get_proteins')
    if type(single_mode) == str:
        logger.info(':: System Report: Single mode enabled!')
        node = single_mode
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
            # Create the node test directory
            os.makedirs(f'{test_path}\\{node}')

            # Saves the directory for further uses
            proteins_test_paths[f'{node}'] = f'{test_path}\\{node}'
            logger.info(f":: System Report: Directory {proteins_test_paths[f'{node}']} successfully created.")

    return proteins, proteins_test_paths
