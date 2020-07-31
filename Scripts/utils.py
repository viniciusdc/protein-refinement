import logging
import os
import glob


def get_proteins(path: str, single_mode: str = None) -> dict:
    logger = logging.getLogger('root.get_proteins')
    if type(single_mode) == str:
        logger.info(':: System Report: Single mode enabled!')
        node = single_mode
        # check if the given protein belongs to the specified 'path'
        if os.path.isdir(f'{path}\\{node}'):
            # get the directory of the chosen protein; dict(protein_name: its_dir);
            proteins = {f'{node}': f'{path}\\{node}'}  # dict
        else:
            # the chosen protein don't belong to this 'path'
            logger.warning(f':: System Report : specified protein [{node}] could not be found at: {path}!')
            return exit(f':: System Exit Report: {__name__}.get_proteins failed to recognize the given node: {node}')
    else:
        # get the names and directories for all the available proteins; dict(protein_name: its_dir);
        proteins = dict(zip(os.listdir(path), glob.glob(f"{path}\\*")))  # dict
        logger.info(f':: System Report: All available nodes at {path} were successfully loaded.')

    return proteins
