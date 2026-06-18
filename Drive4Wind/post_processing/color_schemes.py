#%%
import csv
import numpy as np
import os
# ---------------
loc_clr_scheme_m4w = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "color-scheme-made4wind.csv"
)

plot_rcParams_update = {
        "font.size": 24,
        "axes.labelsize": 24,
        "legend.fontsize": 24, # 16 for pdf of `var_with_iter` plot
        "lines.linewidth": 2,
        "lines.markersize": 6,
    }

def read_color_scheme(path):
    """
    Read a 2-row CSV color scheme file and return a dict

    Inputs
    __________
    2-row CSV file, with:

    Row 1 -> names\\
    Row 2 -> hex colors

    Example:
        Dark_Teal,Aqua
        #0494A3,#06B2D8

    Returns
    __________
        {
            "Dark_Teal": "#0494A3",\\
            "Aqua": "#06B2D8"
        }
    """

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)

        rows = list(reader)

    if len(rows) < 2:
        raise ValueError("CSV must contain at least two rows (names + colors).")

    names = [c.strip() for c in rows[0]]
    colors = [c.strip() for c in rows[1]]

    if len(names) != len(colors):
        raise ValueError("Number of names and colors must match.")

    color_dict = dict(zip(names, colors))

    return color_dict
# ---------------
#%%
if __name__ == "__main__":
    dict_color = read_color_scheme( loc_clr_scheme_m4w )
    dict_color
# %%
