import numpy as np
import logging
from Scripts.utils import centralizar, dist_matrix_projection, atoms_re_ordination
from Scripts.obj import *
from time import time
from Scripts.spectral_projected_gradient import protein_spg
from Scripts.LOG import os_display_call
from Scripts.pdf_file_gen import write_pdb_file


def launch_spg(node, pdb, test_path, comp: dict):
    """This method aims to create all the environment variables to execute the spectral gradient method."""
    # Get run options
    prop_dist = comp.get('prop_dist')
    u, v = comp.get('u'), comp.get('v')
    lb, ub = comp.get('lb'), comp.get('ub')
    dist = comp.get('dist')
    # Get logger
    logger = logging.getLogger('root.run_spg.launch_spg')
    # if debug_mode:
    #     logger.setLevel('DEBUG')

    # Adjust variables:
    noise, tol, big_n, big_m, w = 1e1, 1e-6, 2000, 15, np.ones(len(lb))

    num_atom_init = max(int(len(dist[:, 1])), int(len(dist[:, 2])))
    # Noise :: Degree of disturbance of the expected solution;
    # TOL :: tolerance for the SPG;
    # N :: maximum accepted number of iterations;
    # M :: non monotone parameter of GLL line search;
    # w :: weight vector

    # Pre-initialization:
    # Choice/re-ordination of the available atoms in accordance with the distance data file
    # Todo: This part don't make sense anymore
    total_atoms_ord, atoms_dict = atoms_re_ordination(dist)
    # solution = centralizar(solution)

    # Initial point origin:
    # TODO: rm is convex args, as its not supported anymore
    # TODO: Check statistics behavior and dual dist file compatibility
    try:
        # directory to initial point file (convex relax solution)
        raid = test_path + f"\\relax_k.txt"
        xi = np.genfromtxt(raid)
        xi = centralizar(xi)
        logger.debug(f":: relax_k file read complete.")

        # directory to initial point file (non scaled relax solution)
        raid = test_path + f"\\relax_np.txt"
        non_scaled = np.genfromtxt(raid)
        non_scaled = centralizar(non_scaled)
        logger.debug(f":: relax_np file read complete.")

        # Starting point from convex relaxation:
        # calculating the objective function value for the non scaled initial point (stress)
        dist_non_scaled = dist_matrix_projection(len(u), u, v, lb, ub, non_scaled)
        # fo_non_scaled = stress(non_scaled, dist_non_scaled, u, v, w)
        # calculating the objective function value for the scaled initial point (stress)
        dist_non_scaled = dist_matrix_projection(len(u), u, v, lb, ub, xi)
        fo_scaled = stress(xi, dist_non_scaled, u, v, w)

    except FileNotFoundError:
        logger.warning(f":: File relax_k or relax_np not found --convex_relax: False")
        is_convex_relax = False
        fo_scaled, fo_non_scaled, xi = 0, 0, []

    data = {}
    # Initiate solver:
    # multi start option not enable, initial distance vector will be the standard
    yi = dist_matrix_projection(int(len(u)), u, v, lb, ub, xi)
    try:
        logger.info(f":: maximum iterations: {big_n}, tol: {tol} and memory: {big_m}")
        to = time()
        out = protein_spg(
            stress,
            grad_stress,
            xi,
            yi,
            [u, v, w, lb, ub, tol, big_n, big_m],
        )
        elapsed_time = time() - to
        fo = stress(xi, yi, u, v, w)
        logger.info(":: Solution found!")

        data = (out, elapsed_time, fo)
        logger.info(f':: Standard phase of node: {node} complete.\n')

    except Exception as err:
        logger.warning(f":: Attempt for protein_spg failed with --bad error: {err}")
        logger.warning(":: The process was interrupted!")
        exit()
        out = []
        fo, elapsed_time = 0.0, 0.0
        data = (out, elapsed_time, fo)

    ops = (xi, u, v, lb, ub)
    main = (
        node,
        num_atom_init,
        len(u),
        prop_dist,
        fo_scaled,
        ops
    )
    os_display_call(test_path, main, data)

    # ----------------------------------------------------------
    #                 Output the data to a file
    # ----------------------------------------------------------
    atoms = np.array([[i] + item for i, item in atoms_dict.items()])

    def raid_gen(arch):
        return test_path + f"\\{arch}.pdb"

    # export solution pdb file:
    # output PDB file format -- ATOM i atom amino A res x1 x2 x3 0.00  0.00 atom[0]:
    write_pdb_file(raid_gen("Sol"), out[0], atoms[:, 1], atoms[:, 3], atoms[:, 2])
    # ----------------------------------------------------------

    return
