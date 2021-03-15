from Scripts.utils import rmsd, mde
import logging
import json
import numpy as np


def os_display_call(test_path, main, data):
    (
        filename,
        num_atom_init,
        m,
        prop_dist,
        fo_scaled,
        ops,
    ) = main
    xi, u, v, lb, ub = ops
    # Get logger
    logger = logging.getLogger('root.spgLOG')
    logger.info(
        "##########################################  INFO  ##########################################"
    )
    logger.info(
        f":: Protein: {filename}, Initial atoms number: {num_atom_init}, after re-ordination."
    )
    logger.info(f":: Assessed distances: {m} and known distances: {prop_dist}.")

    logger.info(
        f":: Initial objective value for the relaxed problem --scaled {fo_scaled:.4e}"
    )
    mde_i = mde(xi, u, v, lb, ub)
    logger.info(f":: MDEi = {mde_i:.2e}")

    # -----------------------------------------------------------------------------------
    # Multi-start --Disable  Standard
    # -----------------------------------------------------------------------------------
    out, elapsed_time, fo = data
    x_spg, backtracking, iterations, fun_o, gtd, norm_d = out
    # Statistics:
    mde_f = mde(x_spg, u, v, lb, ub)
    logger.info(":: spg results --multi start: False")
    logger.info(
        ":: Iter - bck ----- MDEf"
        " ----- i_val ----- f_val ----- gtd ----- |d| ----- time(s)"
    )
    prompt_string = (
        f"   {iterations:<5}: {backtracking:<6} {mde_f:<10.2e} {fo / 2:<11.2e} "
        f"{fun_o / 2:<10.2e} {gtd:<10.2e} {norm_d:<10.2e} {elapsed_time:.3f}"
    )

    logger.info(prompt_string)
    logger.info(
        "############################################################################################"
    )

    # -----------------------------------------------------------------------------
    # Generating output file with statistics:
    # -----------------------------------------------------------------------------
    static_log = test_path + f"\\spg_static_standard_LOG.txt"

    static_dict = {"node": f'{filename}', "init_atom_#": f"{num_atom_init}", "assessed_dist": f'{m}',
                   "Know_dist": f'{prop_dist}', "convex": True,
                   "init_fun_val_relax_k": f'{fo_scaled:.4e}', "MDEi": f'{mde_i:.2e}',
                   "multi-start": False, "standard": {"iter": f'{iterations:<7}', "back": f'{backtracking:<6}',
                                                      "MDEf": f'{mde_f:<10.2e}', "fun_i": f'{fo / 2:<11.2e}',
                                                      "fun_f": f'{fun_o / 2:<10.2e}',
                                                      "gtd": f'{gtd:<10.2e}', "norm_d": f'{norm_d:<10.2e}',
                                                      "time": f'{elapsed_time:.3f}'}}

    with open(static_log, "w") as file:
        json.dump(static_dict, file)
