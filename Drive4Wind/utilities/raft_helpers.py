#%%
# IMPORTS

import os
import pandas as pd
import numpy as np
from wisdem.commonse.fileIO import var_df2dict

#%%
# PROCESS RESULTS FROM CSVs FOR USER DEFINED VARIABLES

# list of variables to extract from weis csv results
lst_variables=[
    "drivese.F_aero_hub",
    "drivese.M_aero_hub",

    "drivese.nacelle_mass",
    "drivese.nacelle_cm",

    "drivese.base_F",
    "drivese.base_M",

    "towerse.tower.turbine_F",
    "towerse.tower.turbine_M",

    "floatingse.f1",
    "floatingse.f2",

    "raft.rigid_body_periods",

    "raft.Max_Offset",
    "raft.heave_avg",
    "raft.Max_PtfmPitch",
    "raft.max_nac_accel",
    "raft.max_tower_base",

    "raft.stats_surge_max",
    "raft.stats_Mbase_max",
    "raft.stats_Tmoor_max",
    "raft.stats_AxRNA_max"
]

def parse_variables_from_csv_to_dict(
        lst_csv_outputs,
        lst_variables,
        tendon_index = 0,
    ):
    """
    Inputs
    _____
    lst_csv_outputs: list of strings

        each string is the full path of the csv output
    
    tendon_index: int

        index of the tendon to analyse


    Outputs
    _____
    outputs_df: pandas DataFrame
    
    outputs_dict: dict
    """

    # -- Tendon-1 anchor tensions
    str_max_Tmoor_anchor = f"raft.max_Tmoor_{tendon_index+1}_anchor"

    # output init
    outputs_dict = {}
    outputs_dict["name"] = []
    outputs_dict[ str_max_Tmoor_anchor ] = []

    # loop over each output csv
    for i, csv_dir in enumerate(lst_csv_outputs):
        csv_file = os.path.join( csv_dir )

        df = pd.read_csv(csv_file)

        dict_vals = var_df2dict( df )

        # NOTE: add first column as 'name' with names of each design 'iea15_UN_*'
        outputs_dict["name"].append( csv_dir.split("\\")[-2] )

        # loop each variable in this csv
        for iv, var in enumerate(lst_variables):
            if var not in outputs_dict.keys(): outputs_dict[ var ] = []
            outputs_dict[ var ].append( dict_vals[ var ] )

            # Tendon-tension
            # = given tendon_index's anchor
            # = extr DLC 6.1 vals
            # = 0 deg yaw misalign
            if "Tmoor" in var:
                stats_Tmoor_max = np.asarray( eval(
                        str( dict_vals[ var ] )
                        ), dtype=float
                    )
                val_Tmoor_tendon_dlc61 = float(
                    stats_Tmoor_max[-2,tendon_index]
                )   
                outputs_dict[ str_max_Tmoor_anchor ].append(val_Tmoor_tendon_dlc61)

    outputs_df = pd.DataFrame( outputs_dict )

    return outputs_df, outputs_dict

#%%
