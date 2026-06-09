import numpy as np

# ---------------
def bin_counting_of_load(load_series, ws, probabilities, 
                         p=10/3, nBins=100):
    """
    Compute equivalent load using bin counting method (histogram).
    NOTE: BINNING BAD WITHIN OPTIMIZATION, TODO: DOCUMENT FAILURE AND SOLUTION!

    Inputs
    -------
    load_series : array[ # of time steps , # of wind speeds ]
        Time series of loads (forces or moments); for FLS, shape=(72e4,10)
    ws : array[ 1, # of wind speeds ]
        Wind speed bins corresponding to load_series columns, shape=(1,10)
    probabilities : array[ 1, # of wind speeds ]
        Probability of occurance of each wind speed
    p : float
        Exponent for equivalent load calculation (default: 10/3 for roller bearings)
    nBins : int
        Number of bins to use for histogramming the load data
    
    Outputs
    -------
    load_eq : array[ # of wind speeds ]
        Equivalent load per wind speed bin, shape=(10,)

    Internal Progress
    ______
    - DONE : implementation
    - DONE : replace coeff_weibull with ws probabilities directly as input
    - TODO : CORRECT this wrong implementation 
    """
    # init
    P = load_series  # shape=(72e4,10)
    n_t, n_w = P.shape[0], P.shape[1] # 72e3, 11
    # ws_pdf = pdf_norm_int_using_cdf(ws, coeff_weibull) # (1,10)
    ws_pdf = probabilities.reshape(1,n_w)
    
    Pmax = np.max(P) if np.max(P) > 0 else np.finfo(float).eps
    
    edges_P = np.linspace(0, Pmax, nBins + 1)
    centers_P = (edges_P[:-1] + edges_P[1:]) / 2
    
    P_hist = np.zeros(nBins)    
    for ec in range(len(ws)):
        hist_count, _ = np.histogram(P[:, ec], bins=edges_P, density=True) #density, for it is PDF
        # hist_count = hist_count / np.sum(hist_count) if np.sum(hist_count) > 0 else hist_count #divide to normalize (sum=1), not needed coz density=True
        P_hist += ws_pdf[0,ec] * hist_count

    P_sum = (np.sum((centers_P ** (p)) * P_hist)) ** (1/p)
    return P_sum

# --------------
def compute_LRD(load_series, omega, p=10/3, dt=0.05, n_bins=100):
    """
    Compute Load-Revolution Distribution (LRD) for one wind speed bin

    Parameters
    ----------
    load_series : array
        Equivalent bearing load time series
    omega : array
        Revolutions per minute
    p : float
        Bearing life exponent; default 10/3 for roller bearings
    dt : float
        time step (of integration); default 0.05 for 20Hz sampling
    n_bins : int
        Number of load bins

    Returns
    -------
    P_bin_center : array
        Load bin centers
    N_rev_bin : array
        Number of revolutions per load bin
    """
    # RPM to RPS to R per time step
    rev = (omega/60)*dt

    # Load bins
    P_bins = np.linspace(
        load_series.min(), load_series.max(),
        n_bins + 1 )
    P_bin_center = 0.5 * (P_bins[:-1] + P_bins[1:])

    # Assign each load sample to a bin
    bin_idx = np.digitize(load_series, P_bins) - 1
    bin_idx = np.clip(bin_idx, 0, n_bins - 1)

    # Accumulate revolutions
    N_rev_bin = np.zeros(n_bins)
    np.add.at(N_rev_bin, bin_idx, rev) # .at = in-place operation

    # Compute equivalent load
    # - total revs
    N_rev_tot = np.sum(N_rev_bin, axis=0)
    Peq_j = (np.sum(
        N_rev_bin * (P_bin_center**p),
        axis=0
        ) / N_rev_tot)**(1.0/p)

    return Peq_j
# --------------

# --------------
def compute_LRD_matrix_vectorized(
        loads_DLC, dt, omega,
        probabilities=[], p=10/3, n_bins=100, P_bins=None):
    """
    Fully vectorized Load-Revolution Distribution (LRD) for HPC,
    without any wind-speed loop
    method: flatten → encode → accumulate → reshape
    Advantages:
    - ~10 ~ 20x faster than looping
    - Safe inside optimization
    Limitations:
    - Exact analytical partials through binning are non-smooth (enhancement: smoothed LRD (Gaussian kernel bins))
      use Rainflow or damage equivalent load formulation instead
    
    Inputs
    ----------
    loads_DLC : array[ # time steps, # wind speeds ]
        full set of DLC loads: at main shaft-hub (output of openFAST)
    dt : float, [s]
        Time step used for integration
    omega  : array[ # time steps, # wind speeds ]
        rotations per minute (of main shaft/bearings)
    probabilities : array[ # wind speeds ]
        wind speed probabilities
    p : float
        Bearing life exponent; default 10/3 for roller bearings
    n_bins : int
        number of bins for counting
    P_bins : array or None
        (optional) predefined load bins

    Outputs
    -------
    if probabilities == []
        P_bin_center : array (n_bins,)
        N_rev : array (n_bins, Nws)
    else
        equivalent load over all wind speeds

    Internal Progress
    _________________
    - DONE : implementation
    """
    # ---- init and sanity check
    Nt, Nws = loads_DLC.shape
    rev = (omega/60)*dt # RPM to RPS to R per time step
    if len(probabilities) == 0: output_P_eq = False
    else: output_P_eq = True; pdf_ws = probabilities.reshape(1,Nws)

    # ---- Load bins (shared across all wind speeds)
    if P_bins is None:
        P_min = loads_DLC.min()
        P_max = loads_DLC.max()
        P_bins = np.linspace(P_min, P_max, n_bins + 1)

    P_bin_center = 0.5 * (P_bins[:-1] + P_bins[1:])

    # ---- Flatten everything
    # ----- representing (i_t, i_ws)
    P_flat = loads_DLC.ravel()
    rev_flat = rev.ravel()

    # ---- Bin index (not count) for loads
    load_bin = np.digitize(P_flat, P_bins) - 1
    load_bin = np.clip(load_bin, 0, n_bins - 1)

    # ---- Wind speed index per flattened entry
    ws_idx = np.tile(np.arange(Nws), Nt)

    # ---- 2D bin index → 1D linear index
    # ----- global bin mapping: (i_load * n_ws) + ws_idx
    # ----- coz of (n_bins*Nws) in var `N_rev_flat` below
    lin_idx = load_bin * Nws + ws_idx

    # ---- Accumulate revolutions
    N_rev_flat = np.zeros(n_bins * Nws)
    np.add.at(N_rev_flat, lin_idx, rev_flat)

    # ---- Reshape back
    N_rev_bin = N_rev_flat.reshape(n_bins, Nws)

    # ---- return now, without computing equivalent load
    if not output_P_eq:
        return P_bin_center, N_rev_bin
    
    # ---- P_eq from LRD
    else:
        # total revs
        N_rev_tot = np.sum(N_rev_bin, axis=0)
        P_bin_center = np.reshape(P_bin_center,(n_bins,1))
        # compute P_eq^p for each wind speed
        Peq_j_raised_p = np.sum(
            N_rev_bin * (P_bin_center**p),
                axis=0
            ) / N_rev_tot
        # compute overall P_eq
        P_eq_LRD = np.sum(Peq_j_raised_p * pdf_ws)**(1.0/p)

        return P_eq_LRD
# ---------------

# ---------------
def del_bearing_computation(load_series, ws_bins, t_step, omega,
                    probabilities, p=10/3, dP_dL=[]):
    """
    Compute Damage Equivalent Load (DEL) using full time series method.

    Inputs
    -------
    load_series : array[ # of time steps , # of wind speeds ]
        Time series of loads (forces or moments); for FLS, shape=(72e4,10)
    ws : array[ 1, # of wind speeds ]
        Wind speed bins corresponding to load_series columns, shape=(1,10)
    t_step : float, [s]
        Time step used for integration
    omega : array[ # of time steps , # of wind speeds ]
        Rotational speed time series corresponding to load_series; shape=(72e4,10)
    p : float
        Exponent for equivalent load calculation (default 10/3 for bearings)
    probabilites : array, same size as ws
        or pdf of occurence of each ws
    dP_dL : array, same size as load_series ('P')
        gradient of P wrt. the length segments of the main shaft (L_*)
        if provided, the gradients are computed; otherwise if empty, no gradients
    
    Outputs
    -------
    DEL : float
        Damage Equivalent Load weighted-averaged over all wind speeds
        provided as the only output if no gradients are computed (len(dP_dL)==0)
    dDEL_dL : float
        Gradients of DEL wrt. L (length of main shaft segments)
        returned as the second output if dP_dL is input to the function (size~=0)

    Internal Progress
    --------------
    - DONE : implement as a function, general purpose
    - DONE : add analytical gradients; vectorize more?
    - TODO : remove ws_bins from inputs (not used, probab input directly instead)
    """
    # init
    P = load_series

    # take out dimenstions
    n_t, n_w = omega.shape[0], omega.shape[1] # 72e3, 11
    ws = ws_bins.reshape(1,n_w)
    pdf_ws = probabilities.reshape(1,n_w)

    # start computing DEL
    N = (omega/60 * t_step) # element wise multiplication, broadcasting (72e3,11)
    n = np.sum(N, axis=0).reshape(1, n_w) # (1,11)

    numerator = np.sum((P**p) * N, axis=0).reshape(1,n_w) # (1,11)

    DEL_j = (numerator/n)**(1/p) # (1,11)

    DEL = np.sum( DEL_j**p * pdf_ws )**(1/p) # float
    # provide DEL without gradients
    if len(dP_dL)==0:
        return DEL
    
    # provide DEL with gradients (DEL, gradients)
    else:
        dDELj_dL = (1/p)*(DEL_j**(1-p))*(1/n)*np.sum(
            p*(P**(p-1))*dP_dL*N,
            axis=0
        )
        dDEL_dL = (1/p)*(DEL**(1-p)) * np.sum(
            p*(DEL_j**(p-1))*dDELj_dL*pdf_ws
        )
        return DEL, dDEL_dL

# def compute_partials(self, inputs, partials):
#     """
#     Analytic gradient: d(L10) / d(DEL)
    
#     Given:
#         DEL_w = (Σ DEL[i]^m × p[i])^(1/m)     ... weighted DEL
#         L10 = (Cr / DEL_w)^m                   ... ISO 281
    
#     Want: ∂L10/∂DEL[j]
    
#     Chain rule:
#         ∂L10/∂DEL[j] = (∂L10/∂DEL_w) × (∂DEL_w/∂DEL[j])
    
#     Step 1: ∂L10/∂DEL_w
#         L10 = Cr^m × DEL_w^(-m)
#         ∂L10/∂DEL_w = -m × Cr^m × DEL_w^(-m-1)
    
#     Step 2: ∂DEL_w/∂DEL[j]
#         DEL_w = (Σ DEL[i]^m × p[i])^(1/m)
#         Let S = Σ DEL[i]^m × p[i], so DEL_w = S^(1/m)
#         ∂DEL_w/∂DEL[j] = (1/m) × S^(1/m - 1) × m × DEL[j]^(m-1) × p[j]
#                        = S^(1/m - 1) × DEL[j]^(m-1) × p[j]
#                        = DEL_w^(1-m) × DEL[j]^(m-1) × p[j]
    
#     Combining:
#         ∂L10/∂DEL[j] = -m × Cr^m × DEL_w^(-m-1) × DEL_w^(1-m) × DEL[j]^(m-1) × p[j]
#                      = -m × Cr^m × DEL_w^(-2m) × DEL[j]^(m-1) × p[j]
#     """
#     m = 10.0 / 3.0
#     DEL = inputs['DEL_mb1']
#     ws_pdf = inputs['ws_pdf']
#     Cr = inputs['Cr_mb1']
    
#     # Intermediate values
#     S = np.sum((DEL ** m) * ws_pdf)
#     DEL_w = S ** (1.0 / m)
    
#     # Gradient w.r.t. each DEL[j]
#     dL10_dDEL = -m * (Cr ** m) * (DEL_w ** (-2*m)) * (DEL ** (m-1)) * ws_pdf
    
#     partials['L10_mb1', 'DEL_mb1'] = dL10_dDEL
    
#     # Gradient w.r.t. Cr
#     # L10 = (Cr/DEL_w)^m = Cr^m × DEL_w^(-m)
#     # ∂L10/∂Cr = m × Cr^(m-1) × DEL_w^(-m)
#     partials['L10_mb1', 'Cr_mb1'] = m * (Cr ** (m-1)) * (DEL_w ** (-m))
# ---------------

