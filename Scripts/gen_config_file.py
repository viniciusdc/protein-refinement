import logging
import json
import os


def gen_file(working_dir: str) -> dict:
    """"This code generates the config.json file"""

    # defines the skeleton for the config dict
    config = {'paths': {}, 'global_settings': {}}

    # get logger
    logger = logging.getLogger('main.gen_config_file')

    # user choice:
    logger.info(':: System Request: Please choose between Standard and Custom configuration.')
    logger.info(':: Insert (0) for Standard or (1) for Custom configuration:')
    choice = input('>> Inform your choice: ')
    try:
        choice = int(choice)
    except Exception as e:
        choice = input('>> Inform your choice (only integers): ')
        choice = int(choice)

    if choice not in [0, 1]:
        logger.warning('>> System config: Invalid option!')
        choice = input('>> Inform your choice (0 or 1): ')

    elif choice == 0:
        # Standard mode
        config['paths'] = {'proteins_path': working_dir + '\\Nodes', 'tests_path': working_dir + '\\Tests'}
        config['global_settings'] = {'disable_SPD': False, 'multi_start': False, 'statistics': True}

    elif choice == 1:
        # Custom mode:
        # Proteins information location;
        proteins_path = input(
            ">> Please confirm the protein examples location (Insert the full path). \n"
            ">> An empty answer will set the protein location to the default '../Nodes' folder:\n"
            ">> Path: ")
        if proteins_path:
            # check if a valid directory was given;
            if os.path.isdir(proteins_path):
                config['paths']["proteins_path"] = proteins_path
                pass
            else:
                print(f">> System config: Given directory not found:\n {proteins_path}.")
                # set the default directory;
                proteins_path = working_dir + "\\Nodes"
                config['paths']["proteins_path"] = proteins_path
                print(f">> Directory set as default: {proteins_path}")
        else:
            # set the default directory;
            proteins_path = working_dir + "\\Nodes"
            config['paths']["proteins_path"] = proteins_path

        # Tests outputs location;
        tests_path = input(
            ">> Please confirm the tests outputs location (Insert the full path). \n"
            ">> An empty answer will set the protein location to the default '../Tests' folder:\n"
            ">> Path: ")
        if tests_path:
            # check if a valid directory was given;
            if os.path.isdir(tests_path):
                config['paths']["tests_path"] = tests_path
                pass
            else:
                print(f">> System config: Given directory not found:\n {tests_path}.")
                # set the default directory;
                tests_path = working_dir + "\\Tests"
                config['paths']["tests_path"] = tests_path
                print(f">> Directory set as default: {tests_path}")
        else:
            # set the default directory;
            tests_path = working_dir + "\\Tests"
            config['paths']["tests_path"] = tests_path
        print("\n")

        # global settings:
        is_convex_relax = bool(input(
            ">> Please confirm if the existing proteins will NOT pass the SDP phase: (Boolean)\n"
            ">> An empty answer will set the configuration to 'False'.\n"
            ">> "))
        config["global_settings"].update(dict(disable_SPD=is_convex_relax))
        print("\n")

        multi_start_phase = bool(input(
            ">> Please confirm if the Multi-start will be executed: (Boolean)\n"
            ">> An empty answer will set the configuration to 'False'.\n"
            ">> "))
        config["global_settings"].update(dict(multi_start=multi_start_phase))
        print("\n")

        gen_statistics = bool(input(
            ">> Please confirm if a statistical inform will be generated: (Boolean)\n"
            ">> An empty answer will set the configuration to 'False'.\n"
            ">> "))
        config["global_settings"].update(dict(statistics=gen_statistics))
        print("\n")

    else:
        logger.warning(':: The Process was interrupted: Any valid information informed!')
        return exit()

    with open(f'{working_dir}\\config.json', 'w+') as file:
        json.dump(config, file)

    return config
