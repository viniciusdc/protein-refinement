import os
import logging
import pathlib
import json
import argparse

from datetime import datetime
from Scripts.utils import get_proteins, launch_sdp
from Scripts.distance_file_gen import gen_distance_file

parser = argparse.ArgumentParser(description="A protein refinement method...")
parser.add_argument("--filename", type=str, help="Input protein name")
# parser.add_argument(
#    "--input_format", type=str, help="Enable use of .pdb or dist.txt files as input"
# )
args_ops = parser.parse_args()


def check_config():
    logger = logging.getLogger("root.config_check")
    """This verifies if the config.json file is available (if not, runs main.py)"""
    if os.path.isfile("config.json"):
        logger.debug(
            ":: System Report: config.json file available, progressing to next phase."
        )
        with open("config.json") as file:
            config = json.load(file)
        return config
    else:
        logger.warning(
            ":: System Report: config.json file not found, possible first try run ?"
        )
        logger.warning(
            ":: System Report: as an attempt to solve the problem a new config.json will be created."
        )
        try:
            os.system("python Scripts/gen_config_file.py --silent=True")
            logger.debug(
                ":: System Report: A new config.json [standard] file was created."
            )
            # load config.json
            with open("config.json") as file:
                config = json.load(file)
            return config

        except Exception as ee:
            logger.warning(
                f"System Report: During the creation of config.json an error occurred {ee}."
            )
            return exit(
                ":: System Report: An error occurred loading the config.json file!"
            )


def main(args):
    # ###################### Pre initialization #######################
    # Get the current working dir. path;
    current_dir = str(pathlib.Path().absolute())

    # Get current time
    now = datetime.now()
    current_time = now.strftime("%d-%m-%Y") + "_" + now.strftime("%H_%M_%S")

    # ###################### Set LOG environment #######################
    # set up logging to file - see previous section for more details
    logger_path = f"{current_dir}/LOGs/{current_time}.log"
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)-20s: %(levelname)-8s %(message)s",
        filename=logger_path,
        filemode="w",
    )
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    # set a format which is simpler for console use
    formatter = logging.Formatter("[%(name)-20s]: [%(levelname)s] %(message)s")
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger("").addHandler(console)

    # Now, we can log to the root logger, or any other logger. First the root...
    logging.info(f":: System Report: The process has started on {now}.")

    # ###################### Load configurations #######################
    # Check for config.json
    config = check_config()
    proteins_path = config["paths"]["proteins_path"]

    # ###################### Start Tests Config #######################
    logging.debug(":: System Report: Creating the test directory.")

    directory = f"\\Tests\\{current_time}"
    test_path = current_dir + directory
    # Create the current test directory
    os.mkdir(test_path)

    # check for load mode, the proteins dict contains the protein(s) name (aka, node) and it's directory path.
    logging.debug(
        ":: System Report: Checking operation mode and generating test node(s) path(s)."
    )

    if args.filename:
        # run in single mode (only one protein will be loaded)
        proteins, test_proteins = get_proteins(
            proteins_path, test_path, single_mode=args.filename
        )
    else:
        # run file test-set (a list of proteins will be loaded)
        proteins, test_proteins = get_proteins(proteins_path, test_path)

    # Create the Node(s) test(s) directory(s) for the current test section
    logging.debug(":: System Report: Write Matlab protein input data")

    with open(current_dir + f"\\Matlab\\proteins.txt", "w+") as file:
        # Writes this information to Matlab usage
        for node in test_proteins:
            # Scheme: Node -- node_path -- test_path
            file.write(f"{node},{proteins.get(node)},{test_proteins.get(node)}\n")

    # Create the distance files for every available proteins
    distance = logging.getLogger("root.distance_file")
    for node in test_proteins.keys():
        # distance file generator -- generates the distance file, if it doesn't exists, and returns it's directory:
        # if args.input_format == "dist_file":
        #     # the user passed a 'valid' dist file as an input
        #     pass
        try:
            # else, we should have access to the pdb file of node
            # TODO: Insert the overwrite=distance_overwrite option
            gen_distance_file(node, proteins[f"{node}"])
            distance.debug(
                ":: System Report: Process completed successfully, waiting for data to be read...\n"
            )

        except OSError as err:
            distance.warning(
                f":: System Error Report: Distance file generator found an error with node: {node} \n"
                f":: {err}."
            )
            distance.warning(":: System Error Report: The process was interrupted!")
            continue

    # ###################### Run Tests #######################
    # ------------ [SDP] Pre-conformation phase ------------
    # SDP launch and start phase:
    logging.info(':: System Report: Start of [SDP] phase.')
    # prepare a structure file for he matlab bash script (SDP Execution);
    launch_sdp(current_dir)
    logging.debug(":: System Report: [SDP] completed! [SPG] environment configuration set.\n")

    # ------------ [SPG] Refinement phase ------------
    logging.info(':: System Report: Loading [SPG] entries.')
    num_test_nodes = len(proteins.key())
    nd_counter = 1  # node counter
    for node in test_proteins.keys():
        logging.info(f":: #{nd_counter} Node: {node} of {num_test_nodes}")
        # --- Open PDB File
        node_path = proteins[f'{node}']
        pdb_path = node_path + f'\\{node}.txt'
        dist_path = node_path + "\\dist.txt"
        test_path = protein_tests[f'{node}']
        if os.path.isfile(pdb_path):
            pdb = open_pdb_file(pdb_path)
        else:
            # pdb file not available
            pdb = []

        logging.debug(':: Environmental properties successful loaded.')
        distancias, u, v, lb, ub, prop_dist = env_set(dist_path, node)

        # Now begins the refinement process of each protein
        # SPG launch and start phase
        logging.info(":: System Report: Start [SPG] program phase.")
        options = (prop_dist, is_convex_relax, global_debug_value)

        if args.multistart:
            launch_spg(node, pdb, test_path, distancias, lb, ub, u, v, options, multi_start=True)
        else:
            launch_spg(node, pdb, test_path, distancias, lb, ub, u, v, options)
        # -----
        nd_counter += 1

    # General Statistics


if __name__ == "__main__":
    main(args_ops)
