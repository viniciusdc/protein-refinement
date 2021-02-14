from Scripts.utils import open_pdb_file
import numpy as np
import logging
import os


def gen_distance_file(protein_node, protein_path: str, overwrite: bool = False) -> str:
    """"Generates the dist.txt file of a given protein (.pdb as a basis)"""
    raid = protein_path + f'\\dist.txt'
    pdb_path = protein_path + f"\\{protein_node}.txt"
    logger = logging.getLogger('root.distance_file')
    logger.debug(f'>> System Report: Looking for dist.txt file of node: {protein_node}...')

    try:
        if os.path.isfile(raid):
            # if dist.txt already exists, pass
            logger.debug(">> System Report: One correspondence found... Loading dist.txt file.")
            if overwrite:
                # overwrite the existing one and create a new dist file:
                pass
            else:
                return str(raid)  # return the dist file path
        # if there isn't any dist.txt at the given path, create a new one:
        else:
            logger.debug(">> System Report: File not found. Generating a new file...")
    except OSError as ee:
        logger.warning(":: System Error Report: Something odd happened !\n"
                       f":: {ee}")

    # open the pdb file
    pdb = open_pdb_file(pdb_path)

    # Just to confirm that the equality constraints will not behave oddly (linear dependence-LD)
    delta = np.random.rand(1)[0] / 10000
    distance_accept_control = 6.0

    logger.debug(f':: System Report: Acceptable maximum distance between atoms: {distance_accept_control} Angstroms')

    # start
    acceptable_atoms = ['H', 'C', 'CA', 'N', 'O', 'S', 'P', 'M']
    backbone_main_chain = ['C', 'CA', 'N']

    logger.debug('>> System Report: Starting distance file generation.')

    data_file = []
    for atom1 in pdb[1:]:
        for atom2 in pdb:
            # for each pair of atoms (atm1, atm2) we check if they are acceptable atoms;
            if atom1[2] in acceptable_atoms and atom2[2] in acceptable_atoms:
                # only calculating distances between different atoms...
                # to avoid adding the same distance, we will consider a crescent order;
                if int(atom2[1]) < int(atom1[1]):
                    coord1 = np.array(atom1[6:9], dtype=float)
                    coord2 = np.array(atom2[6:9], dtype=float)
                    # dist :: initial distance (Euclidean) between the atoms;
                    dist = np.linalg.norm(coord1 - coord2)

                    # are they backbone atoms?
                    if atom1[2] in backbone_main_chain and atom2[2] in backbone_main_chain:
                        # Same chain/amino-acid
                        if atom1[5] == atom2[5]:
                            # avoid LD;
                            dist_lb = np.copy(dist) - delta
                            dist_ub = np.copy(dist) + delta
                            # write as : ['1', '6', 'N', 'LYS', '2', 'N', 'LEU', '3', 'dist_l', 'dist_u', '1'];
                            data_file.append([atom2[1], atom1[1], atom2[2], atom2[3],
                                              atom2[5], atom1[2], atom1[3], atom1[5],
                                              f'{dist_lb:.12f}', f'{dist_ub:.12f}', '1'])
                        # Else, we only add the distacence d, if d >= acceptable distance:
                        elif dist <= distance_accept_control:
                            dist_lb = np.copy(dist) - 1 / 3
                            dist_ub = np.copy(dist) + 1 / 3
                            # write as : ['1', '6', 'N', 'LYS', '2', 'N', 'LEU', '3', 'dist_l', 'dist_u', '0'];
                            data_file.append([atom2[1], atom1[1], atom2[2], atom2[3],
                                              atom2[5], atom1[2], atom1[3], atom1[5],
                                              f'{dist_lb:.12f}', f'{dist_ub:.12f}', '0'])

                    elif dist <= distance_accept_control:
                        dist_lb = np.copy(dist) - 1 / 3
                        dist_ub = np.copy(dist) + 1 / 3
                        # write as : ['1', '6', 'N', 'LYS', '2', 'N', 'LEU', '3', 'dist_l', 'dist_u', '0'];
                        data_file.append([atom2[1], atom1[1], atom2[2], atom2[3],
                                          atom2[5], atom1[2], atom1[3], atom1[5],
                                          f'{dist_lb:.12f}', f'{dist_ub:.12f}', '0'])

    logger.debug(">> System Report: Sorting the chosen atoms numbers with a new map.")

    index_set = np.array(data_file)
    index_set = np.array(list(set(list(index_set[:, 0]) + list(index_set[:, 1]))), dtype='int')
    index_set.sort()
    index = dict(zip(index_set, [i for i in range(1, len(index_set) + 1)]))

    logger.debug(">> System Report: Writing output file;")
    dist_data = []
    for item in data_file:
        item[0] = index[int(item[0])]
        item[1] = index[int(item[1])]
        line = '  '
        for i in range(len(item)):
            if i in [8, 9]:
                line += format(item[i]).ljust(23, ' ')
            else:
                line += format(item[i]).ljust(5, ' ')
        dist_data.append(line)

    with open(raid, 'w') as dist_file:
        for item in dist_data:
            dist_file.write("%s\n" % item)

    # End
