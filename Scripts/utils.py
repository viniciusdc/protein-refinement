import logging
import numpy as np
from subprocess import Popen, PIPE, STDOUT
import random
import os
import glob
from numpy.linalg import svd
from time import time
from numpy.core.umath_tests import inner1d


def get_proteins(path: str, test_path: str, single_mode: str = None, black_list: dict = None) -> (dict, dict):
    # First we will save the proteins names and paths to be read by the SDP Matlab script;
    # And also, create the test paths for each one, saving it on a dictionary
    logger = logging.getLogger('root.utils.get_proteins')
    if type(single_mode) == str:
        logger.debug(':: System Report: Single mode enabled!')
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
        # os.makedirs(f'{test_path}\\{node}')

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
            # os.makedirs(f'{test_path}\\{node}')

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
    matlab_scripts = path + '\\Matlab\\sdpaux.m'

    if os.path.isfile(matlab_scripts):
        pass
    else:
        logger.warning(':: System Error Report: Matlab auxiliary file method not found!')
        return exit()

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


def env_set(raid: str, node: str, debug_mode: bool = False):
    """"Prepares all the necessary variables for the [SPG] phase"""
    # get current logger
    logger = logging.getLogger('root.utils.env_set')
    if debug_mode:
        logger.setLevel(10)

    # open distance file (as an np-array):
    dist = []
    try:
        if os.path.isfile(raid + r'\dist_wh.txt'):
            # Van der Waals
            dist = np.concatenate((np.genfromtxt(raid + r'\dist.txt', dtype="str"),
                                   np.genfromtxt(raid + r'\dist_wh.txt', dtype="str")))
        else:
            dist = np.genfromtxt(raid + r'\dist.txt', dtype="str")
    except Exception as error:
        logger.warning(f':: System Error Report: Could not load {node} distance file.')
        logger.error(f':: {error}')
    logger.debug(f":: System Report: Distance file read completed!")

    # parse distances (when Wander Wauss distances available)
    # index vectors (for atom pairs [u, v]):
    u, v = (
        np.array(dist[:, 0], dtype="int"),
        np.array(dist[:, 1], dtype="int"),
    )
    # it starts from zero on python
    u = u - np.ones(len(u), dtype="int")
    v = v - np.ones(len(v), dtype="int")

    # lower and upper bounds vectors:
    lb, ub = (
        np.array(dist[:, 8], dtype="float"),
        np.array(dist[:, 9], dtype="float"),
    )

    prop_dist = 0
    for k in range(len(u)):
        if int(dist[k][-1]) == 1:
            prop_dist += 1
    prop_dist = int(prop_dist)

    # Log archive
    logger.debug(":: Process completed successfully, waiting for data to be read...")
    comp = {'dist': dist, 'u': u, 'v': v, 'lb': lb, 'ub': ub, 'prop_dist': prop_dist}
    return comp


# funções auxiliares utilizadas:
# prod_interno :: produto interno entre pares (A,v) com A matriz (n, p) e v vetor m-dimensional;
# def :: <(A, v), (B, w)> = Tr(AB') + sum_{i = 1}^{m} (v_i * w_i)
def prod_interno(matrix_a, matrix_b, v, w):
    # n :: número de linhas de A;
    # p :: número de linhas de B;
    n, p = matrix_a.shape
    if matrix_a.shape != matrix_b.shape or len(v) != len(w):
        print('Report Error: Incompatible dimensions!')
        return
    prod_soma = sum(inner1d(matrix_a, matrix_b))
    prod_soma += np.dot(v, w)
    return prod_soma


# distância Euclidiana entre as linhas i e j da matriz X;
def distance(i, j, matrix_x):
    dist = np.linalg.norm(matrix_x[i, :] - matrix_x[j, :])
    return dist


# centralizar um conjunto de pontos x;
def centralizar(x):
    # caso a entrada não esteja no formato adequado;
    x = np.array(x, dtype=float)

    # k :: dimensão
    # n :: número de pontos
    n, k = x.shape

    ponto_medio = (1 / n) * np.dot(np.ones(n), x)
    # ponto transladado;
    x = x - (np.ones((n, 1)) * ponto_medio)

    return x


# rmsd :: calcula a raiz quadrada da média dos desvios entre duas estruturas A e B (centralizadas);
def rmsd(matrix_a, matrix_b):
    # Get logger
    logger = logging.getLogger('root.utils.rmsd')
    # n :: número de pontos;
    n, k = matrix_a.shape
    if matrix_a.shape != matrix_b.shape:
        logger.warning('Dimensões incompativeis entre as matrizes')
        logger.warning('Dimensões da matriz A : {}'.format(matrix_a.shape))
        logger.warning('Dimensões da matriz B : {}'.format(matrix_b.shape))
        return 'NaN'
    # Procrustes:
    # Given two matrices A and B it is asked to find an orthogonal matrix Q which most closely maps A to B.
    matrix_a = centralizar(matrix_a)
    matrix_b = centralizar(matrix_b)
    singular_value_dec = svd(np.dot(matrix_b, matrix_a.T))
    matri_q = np.dot(singular_value_dec[0], singular_value_dec[2])

    correlation = np.linalg.norm(np.dot(matri_q, matrix_a) - matrix_b, ord='fro')

    return np.sqrt(1 / n) * correlation


# mde :: erro médio dos desvios;
# lb :: limitantes inferiores;
# ub :: limitantes superiores;
def mde(ponto, vec_u, vec_v, lb, ub):
    # dim :: tamanho/ dimensão do vetor u;
    # m :: número de limitantes/distâncias conhecidos/das;
    dim = len(vec_u)
    m = len(lb)

    soma = 0
    for s in range(dim):
        dist_ponto = distance(vec_u[s], vec_v[s], ponto)
        soma += max((lb[s] - dist_ponto) / lb[s], 0) + max((dist_ponto - ub[s]) / ub[s], 0)

    return soma / m


# apenas uma checagem para verificar se o problema de dimensionamento foi resolvido.
def check_solution_dimension(matrix_a, matrix_b):
    if matrix_a.shape[0] != matrix_b.shape[0]:
        return True
    else:
        return False


# dado um conjunto de pontos, projeta-se suas distâncias sobre os limitantes lb e ub;
# saída :: vetor armazenando as distâncias projetadas.
def dist_matrix_projection(dim, vec_u, vec_v, lower_bound, upper_bound, point_set, multistart=False):
    y = np.zeros(dim)
    if multistart:
        for s in range(dim):
            # d = distance(vec_u[s], vec_v[s], point_set)
            # if lower_bound[s] <= d <= upper_bound[s]:
            #     y[s] = d
            # elif d < lower_bound[s]:
            #     y[s] = random.uniform(lower_bound[s], upper_bound[s])
            # elif d > upper_bound[s]:
            #     y[s] = random.uniform(lower_bound[s], upper_bound[s])
            y[s] = random.uniform(lower_bound[s], upper_bound[s])
    else:
        for s in range(dim):
            d = distance(vec_u[s], vec_v[s], point_set)
            y[s] = np.clip(d, lower_bound[s], upper_bound[s])
    return y


def atoms_re_ordination(dist_file):
    """sorting atoms according to its distance file. To create the expected/correct solution"""
    # Get current logger
    logger = logging.getLogger()

    # total number of atoms (in accordance with the distance data file)
    total_atoms_ord = max(
        max(np.array(dist_file[:, 0], dtype="int")),
        max(np.array(dist_file[:, 1], dtype="int")),
    )

    to = time()
    atoms_names_list = []
    for item in dist_file:
        line = [item[0]] + list(item[2:5])
        atoms_names_list.append(line)
        line = [item[1]] + list(item[5:8])
        atoms_names_list.append(line)
    # create a dict containing the dist list index
    dist_atoms = {}
    for item in atoms_names_list:
        if int(item[0]) in dist_atoms:
            continue
        else:
            dist_atoms[int(item[0])] = item[1:]

    elapsed_time = time() - to
    logger.debug(f":: The process of reformatting/re-ordination was successfully completed in {elapsed_time:.4f}s")

    return total_atoms_ord, dist_atoms
