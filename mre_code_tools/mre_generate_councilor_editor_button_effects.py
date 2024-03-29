import argparse
from datetime import datetime
import os
import time
import sys
from json import load as json_load

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
)

"""
  ______ ______ ______ ______ _____ _______ _____ 
 |  ____|  ____|  ____|  ____/ ____|__   __/ ____|
 | |__  | |__  | |__  | |__ | |       | | | (___  
 |  __| |  __| |  __| |  __|| |       | |  \___ \ 
 | |____| |    | |    | |___| |____   | |  ____) |
 |______|_|    |_|    |______\_____|  |_| |_____/ 

"""

def iterate_traits_generate_btn_fx_for_regulatory():
    pass

def iterate_traits_generate_btn_fx_for_cognitive():
    pass

def iterate_traits_generate_btn_fx_for_growth():
    pass

def iterate_traits_generate_btn_fx_for_legion():
    pass

def iterate_traits_generate_button_effects_for_councilor(
        organized_traits_dict: dict,
        councilor_type: str
):
    councilor_editor_fx_blob = [AUTOGENERATED_HEADER]
    councilor_subclass = GESTALT_COUNCILOR_SUBCLASS_MAP[councilor_type]

    for rarity_level in RARITIES:
        for leader_making_trait in organized_traits_dict['councilor_editor_traits'][rarity_level]:
            trait_name = [*leader_making_trait][0]
            root = leader_making_trait[trait_name]

            if trait_req_subclass := root.get('required_subclass'):
                if trait_req_subclass != councilor_subclass:
                    print(
                        f"Skipping {trait_name}, req subclass is {trait_req_subclass}"
                        f" and this councilor is {councilor_subclass}"
                    )
                    continue

            councilor_editor_fx_code_for_trait = gen_councilor_editor_traits_button_effects_code(
                councilor_type=councilor_type,
                trait_name=trait_name,
                rarity=root['rarity'],
                required_subclass=root.get('required_subclass', None),
                prerequisites=root.get('prerequisites', [])
            )
            councilor_editor_fx_blob.append(councilor_editor_fx_code_for_trait)
    return '\n'.join(councilor_editor_fx_blob)


def gen_councilor_editor_traits_button_effects_code(
        councilor_type: str, trait_name: str, rarity: str, requires_paragon_dlc: bool=False,
        required_subclass: str = None, prerequisites: list = [],
):
    """ Councilors can't change class so they're restricted to just 1 class & subclass
    which means outside this code we just have to iterate one leader class' of traits """

    """ TODO: allow statements for:
    - paragon dlc
    - trait needs any dlc dependency
    - trait has any tech requirement
    MORE TODO:
    - conditionally call effect to remove T1 or T2 trait

    """
    # Figure out base trait name
    trait_ends_in_num = trait_name[-1].isdigit()
    if trait_ends_in_num:
        trait_name_no_tier = trait_name.rsplit('_',1)[0]
    else:
        trait_name_no_tier = trait_name
    
    # Calculate any additional statements to add to the "allow" block
    allowances = []
    if requires_paragon_dlc:
        allowances.append("has_paragon_dlc = yes")
    # Get fancy about picking up DLC requirements per trait
    if dlc_dependecy := TRAITS_REQUIRING_DLC.get(trait_name):
        allowances.append(f"{dlc_dependecy} = yes")
    # Assuming that prerequisites will always be tech *fingers crossed*
    if len(prerequisites):
        for tech in prerequisites:
            allowances.append(f"has_technology = {tech}")
    leader_class = GESTALT_COUNCILOR_CLASS_MAP["regulatory"]
    subclass_check_trigger = f"oxr_mdlc_councilor_editor_check_leader_has_required_subclass = {{ SUBCLASS = {required_subclass} }}"

    return f"""
#{councilor_type} #{trait_name} #{rarity}
oxr_mdlc_councilor_editor_{councilor_type}_{trait_name}_add_button_effect = {{
	potential = {{
		event_target:oxr_mdlc_councilor_editor_target = {{ NOT = {{ has_trait = {trait_name} }} }}
	}}
	allow = {{
		oxr_mdlc_councilor_editor_check_trait_resources_cost_{rarity} = yes
		event_target:oxr_mdlc_councilor_editor_target = {{
			oxr_mdlc_councilor_editor_check_trait_points_cost_{rarity} = yes
			oxr_mdlc_councilor_editor_check_trait_picks = yes
			{"#" if required_subclass is None else ''}{subclass_check_trigger}
		}}
		{"\n        ".join(allowances)}
	}}
	effect = {{
		custom_tooltip = oxr_mdlc_councilor_editor_show_trait_total_cost_{rarity}
		event_target:oxr_mdlc_councilor_editor_target = {{
			oxr_mdlc_councilor_editor_remove_tier_1_or_2_traits_effect = {{ TRAIT_NAME = {trait_name_no_tier} }}
			add_trait_no_notify = {trait_name}
		}}
		hidden_effect = {{
			oxr_mdlc_councilor_editor_deduct_trait_resources_cost_{rarity} = yes
			event_target:oxr_mdlc_councilor_editor_target = {{
				oxr_mdlc_councilor_editor_deduct_trait_points_cost_{rarity} = yes
				oxr_mdlc_councilor_editor_deduct_trait_pick = yes
			}}
		}}
	}}
}}
oxr_mdlc_councilor_editor_{councilor_type}_{trait_name}_remove_button_effect = {{
	potential = {{
		event_target:oxr_mdlc_councilor_editor_target = {{ has_trait = {trait_name} }}
	}}
	allow = {{ always = yes }}
	effect = {{
		custom_tooltip = xvcv_mdlc_core_modifying_tooltip_remove_{leader_class}_{trait_name}
		hidden_effect = {{
			event_target:oxr_mdlc_councilor_editor_target = {{
				remove_trait = {trait_name}
				oxr_mdlc_councilor_editor_refund_trait_points_cost_{rarity} = yes
				oxr_mdlc_councilor_editor_refund_trait_pick = yes
			}}
			oxr_mdlc_councilor_editor_refund_trait_resources_cost_{rarity} = yes
		}}
	}}
}}
"""

if __name__ == "__main__":
    print(CODE_HEADER)
    print("Generate Councilor Editor button effects code")
    
    for councilor in GESTALT_COUNCILOR_TYPES:
        source_file = GESTALT_COUNCILOR_SOURCE_TRAITS_FILES[councilor]
        btn_fx_outfile = OUTPUT_FILES_DESTINATIONS[COUNCILOR_EDITOR]["effects"][councilor]

        traits_json_blob = ""
        with open(source_file, "r") as source_codegen_data:
            traits_json_blob = json_load(source_codegen_data)
        
        sys.stdout.write(f"Going to make {councilor} button effects code, writing to {btn_fx_outfile}...")
        councilor_gui_blob = iterate_traits_generate_button_effects_for_councilor(
            councilor_type=councilor, organized_traits_dict=traits_json_blob
        )
        with open(btn_fx_outfile, "wb") as councilor_btn_fx_outfile:
            councilor_btn_fx_outfile.write(
                councilor_gui_blob.encode('utf-8')
            )
        sys.stdout.write("Done."); print("")
    print("Done writing button effects code.")
