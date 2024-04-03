import argparse
from datetime import datetime
import os
import time
import sys
from json import load as json_load
from typing import List

from mre_common_vars import (
    AUTOGENERATED_HEADER,
    BUILD_FOLDER,
    CORE_MODIFYING,
    EXCLUDE_SUBCLASSES_FROM_CORE_MODIFYING,
    EXCLUDE_TRAITS_FROM_CORE_MODIFYING,
    GESTALT_COUNCILOR_CLASS_MAP,
    GESTALT_COUNCILOR_SUBCLASS_MAP,
    GESTALT_COUNCILOR_TYPES,
    GUI_FOOTER_TEXT,
    GUI_HEADER_TEXT,
    INPUT_FILES_FOR_CODEGEN,
    LEADER_CLASSES,
    LEADER_MAKING,
    LEADER_SUBCLASSES_NAMES,
    LEADER_SUBCLASSES,
    LOCALISATION_HEADER,
    MACHINE_LOCALISATIONS_MAPFILE,
    OUTPUT_FILES_DESTINATIONS,
    TRAITS_REQUIRING_DLC,
    RARITIES,
    COUNCILOR_EDITOR,
    FILE_NUM_PREFIXES,
    GESTALT_COUNCILOR_SOURCE_TRAITS_FILES,
    CODE_HEADER,
    EXCLUDE_TRAITS_FROM_PARAGON_DLC,
)

"""
  _______ _____  _____ _____  _____ ______ _____   _____ 
 |__   __|  __ \|_   _/ ____|/ ____|  ____|  __ \ / ____|
    | |  | |__) | | || |  __| |  __| |__  | |__) | (___  
    | |  |  _  /  | || | |_ | | |_ |  __| |  _  / \___ \ 
    | |  | | \ \ _| || |__| | |__| | |____| | \ \ ____) |
    |_|  |_|  \_\_____\_____|\_____|______|_|  \_\_____/ 
                                                         
"""

def gen_councilor_check_can_use_reset_button() -> List[str]:
    """ generate the trigger that determines if the reset button can be pushed
    trigger saying that any of the selectable traits are selected
    
    either generate one trigger for each, or one trigger for all
    
    go thru all 99_ files, for each class,
    iterate all the traits in councilor_editor_traits and make a set
    then return that list and print the trigger """
    unsorted_traits = {
        "common": [],
        "veteran": [],
        "paragon": []
    }
    scripted_trigger_header = """
oxr_mdlc_councilor_editor_check_can_use_reset_button = {
    # One trigger to rule them all
	optimize_memory
    OR = {
"""
    scripted_trigger_footer = """
    }
}
"""
    indentation = "            "
    trait_limit_lines = []
    for processed_traits_file in INPUT_FILES_FOR_CODEGEN:
        with open(
            os.path.join(BUILD_FOLDER, processed_traits_file)
        ) as organized_traits_dict_data:
            organized_traits_dict = json_load(organized_traits_dict_data)
            for rarity in RARITIES:
                for leader_trait in organized_traits_dict["councilor_editor_traits"][rarity]:
                    trait_name = [*leader_trait][0]
                    if EXCLUDE_TRAITS_FROM_PARAGON_DLC.get(trait_name):
                        print(f"Skipping {trait_name}...")
                    unsorted_traits[rarity].append(trait_name)
    conditional_limit = "            has_trait = {trait_name}"
    # Sort them all
    for rarity in RARITIES:
        for trait_name in sorted(set(unsorted_traits[rarity])):
            if "subclass" not in trait_name:
                trait_limit_lines.append(
                    conditional_limit.format(trait_name=trait_name)
                )
    return f"""{scripted_trigger_header}
{"\n".join(trait_limit_lines)}
{scripted_trigger_footer}"""

if __name__ == "__main__":
    print("0xRetro Magic COde creat0r")
    print("Making oxr_mdlc_councilor_editor_check_can_use_reset_button ...")
    scripted_trigger = gen_councilor_check_can_use_reset_button()
    with open(
        os.path.join(
            BUILD_FOLDER,
            f"{FILE_NUM_PREFIXES["triggers"]}_oxr_mdlc_councilor_editor_check_can_use_reset_button.txt"
        ), 'wb'
    ) as outfile:
        outfile.write(scripted_trigger.encode('utf-8'))
    print("done.")
