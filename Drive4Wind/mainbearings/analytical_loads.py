import numpy as np
from data.constants import gravity

# ---------------
def analytical_MB_Forces( Fx,Fy,Fz, Mx,My,Mz, L_h1,L_12, flag_jac=False ):
    """
    Analytical low-fidelity (quick) main bearing force calculation,
    using static equilibrium or moment balance, 
    unlike higher fidelity `Hub_Rotor_LSS_Frame` using pyFrame3DD.
    [depr.]

    Inputs
    -------
    F* : array[ # of time steps , # of wind speeds ]
        Forces (aero) on the hub center/main shaft input; for FLS, shape=(72e4,10)
    M* : array[ # of time steps , # of wind speeds ]
        Moment (aero) on the hub center/main shaft input; for FLS, shape=(72e4,10)
    L_h1 : float
        length along main shaft btw hub and mb1
    L_12 : float
        length along main shaft btw mb1 and mb2
    flag_jac : Boolean
        whether to provide analytical derivatives (True) or not (False)

    Outputs
    -------
    F_mb1 : All forces on the 1. main bearing
        shape = (4, shape(F*) )
    F_mb2 : All forces on the 2. main bearing
        shape = (4, shape(F*) )
    
    --- if flag_jac = True ---
    dFmb1_dLh1 : All derivatives of mb1 forces wrt. L_h1
        shape = (4, shape(F_mb1) )
    dFmb1_dLh1 : All derivatives of mb1 forces wrt. L_12
        shape = (4, shape(F_mb1) )
    dFmb2_dLh1 : All derivatives of mb2 forces wrt. L_h1
        shape = (4, shape(F_mb2) )
    dFmb2_dL12 : All derivatives of mb2 forces wrt. L_12
        shape = (4, shape(F_mb2) )

    Internal Progress
    --------------
    - DONE : implement as a openMDAO Explicit Component
        depr, due to 'known and fixed' shape of F* and M*
    - DONE : implement as a function, general purpose
    - DONE : add analytical gradients
    - TODO : mag of F* and M* is O(6)! exploding jac? how to scale
    """
    
    ### === Loads on bearings ===
    # init
    n_ts, n_ws = Fx.shape[0], Fx.shape[1] # = 72e4, 10
    F_mb1 = np.zeros( (n_ts,n_ws,4) ) # for 4 forces (ax,y,z,rad)
    F_mb2 = np.zeros( (n_ts,n_ws,4) ) # for 4 forces (ax,y,z,rad)

    # ----- MB2 (downwind) reactions
    F_mb2_ax = np.abs(Fx)   # 2TRB typically
    F_mb2_y = (-Mz + Fy * L_h1) / L_12  #
    F_mb2_z = (My + Fz * L_h1) / L_12   #
    # stable, vectorized hypot (handles overflow/underflow)
    F_mb2_rad = np.hypot(F_mb2_y, F_mb2_z) # element-wise

    # ----- MB1 (upwind) reactions
    F_mb1_ax = np.zeros_like( F_mb2_ax )  # CRB typically
    F_mb1_y = -F_mb2_y - Fy #
    F_mb1_z = -F_mb2_z - Fz #
    F_mb1_rad = np.hypot(F_mb1_y, F_mb1_z)

    # ----- collect for outputs
    F_mb1 = np.stack([F_mb1_ax, F_mb1_y, F_mb1_z, F_mb1_rad])
    F_mb2 = np.stack([F_mb2_ax, F_mb2_y, F_mb2_z, F_mb2_rad])

    if not flag_jac:
        return F_mb1, F_mb2
    # ==============================

    else:
    ### === Derivatives of loads wrt. L_* ===
    # init
        dFmb1_dLh1 = F_mb1                # ----- main jac outputs -----
        dFmb1_dL12 = F_mb1
        dFmb2_dLh1 = F_mb2
        dFmb2_dL12 = F_mb2

        # ----- MB2 -----            
        dFmb2ax_dLh1 = np.zeros_like(F_mb2_ax)
        dFmb2ax_dL12 = np.zeros_like(F_mb2_ax)
        # NOTE: no need to use `utils/smooth_abs` coz dFx_dL* = 0 anyway
            
        # ----- mb2_y diff wrt. L_
        dFmb2y_dLh1 = Fy / L_12
        dFmb2y_dL12 = (-1/L_12) * F_mb2_y

        # ----- mb2_z diff wrt. L_
        dFmb2z_dLh1 = Fz / L_12
        dFmb2z_dL12 = (-1/L_12) * F_mb2_z
        
        # ----- mb2_r diff wrt. y, z
        dFmb2rad_dFmb2y = F_mb2_y / F_mb2_rad
        dFmb2rad_dFmb2z = F_mb2_z / F_mb2_rad
        # ----- mb2_r diff wrt. L_
        dFmb2rad_dLh1 = (dFmb2rad_dFmb2y*dFmb2y_dLh1) + (dFmb2rad_dFmb2z*dFmb2z_dLh1)
        dFmb2rad_dL12 = (dFmb2rad_dFmb2y*dFmb2y_dL12) + (dFmb2rad_dFmb2z*dFmb2z_dL12)
        # ---------------

        # ----- MB1 -----
        dFmb1ax_dLh1 = F_mb1_ax # both 0s
        dFmb1ax_dL12 = F_mb1_ax
        
        # ----- mb1_y diff wrt. L_
        dFmb1y_dLh1 = -dFmb2y_dLh1
        dFmb1y_dL12 = -dFmb2y_dL12

        # ----- mb1_z diff wrt. L_
        dFmb1z_dLh1 = -dFmb2z_dLh1
        dFmb1z_dL12 = -dFmb2z_dL12
        
        # ----- mb1_r diff wrt. y, z
        dFmb1rad_dFmb1y = F_mb1_y / F_mb1_rad
        dFmb1rad_dFmb1z = F_mb1_z / F_mb1_rad
        # ----- mb1_r wrt. L_
        dFmb1rad_dLh1 = (dFmb1rad_dFmb1y*dFmb1y_dLh1) + (dFmb1rad_dFmb1z*dFmb1z_dLh1)
        dFmb1rad_dL12 = (dFmb1rad_dFmb1y*dFmb1y_dL12) + (dFmb1rad_dFmb1z*dFmb1z_dL12)
        # ---------------

        # ----- collect for outputs
        dFmb1_dLh1 = np.stack([dFmb1ax_dLh1,dFmb1y_dLh1,dFmb1z_dLh1,dFmb1rad_dLh1])
        dFmb1_dL12 = np.stack([dFmb1ax_dL12,dFmb1y_dL12,dFmb1z_dL12,dFmb1rad_dL12])

        dFmb2_dLh1 = np.stack([dFmb2ax_dLh1,dFmb2y_dLh1,dFmb2z_dLh1,dFmb2rad_dLh1])
        dFmb2_dL12 = np.stack([dFmb2ax_dL12,dFmb2y_dL12,dFmb2z_dL12,dFmb2rad_dL12])

        return F_mb1, F_mb2, dFmb1_dLh1, dFmb1_dL12, dFmb2_dLh1, dFmb2_dL12
    # ==============================

# ---------------
def analytical_MBforces_realistic( Fx,Fy,Fz, Mx,My,Mz, m_carrier,delta,tilt,
        L_h1,L_12, flag_jac=False ):
    """
    Analytical low-fidelity main bearing force calculation,
    using static equilibrium about MB2 (fixed; TRB2)
    Using 4-node formulation, includes carrier mass at shaft-end (GB-input)

    Inputs
    -------
    F* : float array[ # of time steps , # of wind speeds ], [N]
        Forces (aero) on the hub center/main shaft input; for FLS, shape=(72e4,10)
    M* : float array[ # of time steps , # of wind speeds ], [Nm]
        Moment (aero) on the hub center/main shaft input; for FLS, shape=(72e4,10)
    m_carrier : float, [kg]
        mass of the planet carrier (gearbox's first stage): calculated in gearbox.py
    delta : float, [m]
        separation between MB2 and gearbox attachment (constant 0.5 in layout.py)
    tilt : float, [rad]
        drivetrain tilt angle
    L_h1 : float
        length along main shaft btw hub and mb1
    L_12 : float
        length along main shaft btw mb1 and mb2
    flag_jac : Boolean
        whether to provide analytical derivatives (True) or not (False)

    Outputs
    -------
    F_mb1 : All forces on the 1. main bearing
        shape = (4, shape(F*) )
    F_mb2 : All forces on the 2. main bearing
        shape = (4, shape(F*) )
    
    --- if flag_jac = True ---
    dFmb1_dLh1 : All derivatives of mb1 forces wrt. L_h1
        shape = (4, shape(F_mb1) )
    dFmb1_dLh1 : All derivatives of mb1 forces wrt. L_12
        shape = (4, shape(F_mb1) )
    dFmb2_dLh1 : All derivatives of mb2 forces wrt. L_h1
        shape = (4, shape(F_mb2) )
    dFmb2_dL12 : All derivatives of mb2 forces wrt. L_12
        shape = (4, shape(F_mb2) )

    Internal Progress
    --------------
    - DONE : implement as a function, general purpose
    - TODO?: implement as a openMDAO Explicit Component
    - TODO : add analytical gradients
    """
    # init
    g = 9.81 # m^2/s
    x3 = L_h1 + L_12
    n_ts, n_ws = Fx.shape[0], Fx.shape[1] # = 72e4, 10
    ### === Loads on bearings ===
    F_mb1 = np.zeros( (n_ts,n_ws,4) ) # for 4 forces (ax,y,z,rad)
    F_mb2 = np.zeros( (n_ts,n_ws,4) ) # for 4 forces (ax,y,z,rad)
        
    # --- MB1 (CRB) ---
    F_mb1_ax = np.zeros_like(Fx)
    F_mb1_y = ( Mz - (Fy*x3) ) / L_12
    F_mb1_z = ( - My - (Fz*x3) + (m_carrier*g*np.cos(tilt)*delta) ) / L_12
    F_mb1_rad = np.hypot(F_mb1_y, F_mb1_z) # element-wise

    # --- MB2 (DRTRB) ---
    F_mb2_ax = np.abs( -Fx - (m_carrier*g*np.sin(tilt)) ) # `abs` coz mb2 reacts to the axial load, regardless if tensile or compressive.
    F_mb2_y = -Fy - F_mb1_y
    F_mb2_z = -Fz - F_mb1_z + (m_carrier*g*np.cos(tilt))
    F_mb2_rad = np.hypot(F_mb2_y, F_mb2_z) # element-wise

    # ----- collect for outputs
    F_mb1 = np.stack([F_mb1_ax, F_mb1_y, F_mb1_z, F_mb1_rad])
    F_mb2 = np.stack([F_mb2_ax, F_mb2_y, F_mb2_z, F_mb2_rad])

    if not flag_jac:
        return F_mb1, F_mb2
    # ==============================

    else:
    ### === Derivatives of loads wrt. L_* ===
    # init
        dFmb1_dLh1 = F_mb1                # ----- main jac outputs -----
        dFmb1_dL12 = F_mb1
        dFmb2_dLh1 = F_mb2
        dFmb2_dL12 = F_mb2

        # ---- MB1 derivatives ----       # TODO
        # dFmb1y_dLh1 = -Fy / L12
        # dFmb1y_dL12 = -(Fy * L12 - Fy * x3) / L12**2

        # dFmb1z_dLh1 = -Fz / L12
        # dFmb1z_dL12 = -(Fz * L12 - Fz * x3) / L12**2

        # # ---- MB2 depends on MB1 ----
        # dFmb2y_dLh1 = -dFmb1y_dLh1
        # dFmb2y_dL12 = -dFmb1y_dL12

        # dFmb2z_dLh1 = -dFmb1z_dLh1
        # dFmb2z_dL12 = -dFmb1z_dL12

        # ----- collect for outputs
        # dFmb1_dLh1 = np.stack([dFmb1ax_dLh1,dFmb1y_dLh1,dFmb1z_dLh1,dFmb1rad_dLh1])
        # dFmb1_dL12 = np.stack([dFmb1ax_dL12,dFmb1y_dL12,dFmb1z_dL12,dFmb1rad_dL12])

        # dFmb2_dLh1 = np.stack([dFmb2ax_dLh1,dFmb2y_dLh1,dFmb2z_dLh1,dFmb2rad_dLh1])
        # dFmb2_dL12 = np.stack([dFmb2ax_dL12,dFmb2y_dL12,dFmb2z_dL12,dFmb2rad_dL12])

        return F_mb1, F_mb2, dFmb1_dLh1, dFmb1_dL12, dFmb2_dLh1, dFmb2_dL12
    # ==============================

# ---------------
# two-bearing EB-beam shaft model for moment-reacting MB2
def solve_bearing_system(M,F, L_h1,L_12,delta, G,EI,k):
    """
    _Solve bearing system in one plane_\\
    using EB-beam theory between the two bearing span (A-B),
    with MB2 @ B supports moment `M`, with stiffness `k`, so: `M = k*theta`.

    Diagram
    --------
    -          A          B          -          \\
        L_h1       L_12      delta              \\
    |----------|----------|----------|          \\
    Hub       MB1        MB2         GB-input   \\
    ^          ^          ^          v          \\
    |          |          |          |          \\
    F, M       RA         RB, MB     G          \\
    
    Convention: +ve =
    ----------
    Forces  : vertical upward
    Bending moment  : sagging (eg. upward force on left = clock-wise (CW) moment)

    Internal Progress
    -----------------
    - DONE : implementation
    """
    # define intermediate parameters
    C = -G*(L_12+delta) - (F*L_h1) - M
    lam = (k*L_12)/(3*EI) # Non-dimensional stiffness ratio
    lamL = lam*L_12
    x3 = L_h1+L_12
    # Left bearing reaction (closed-form solution) 
    RA = ( -M-F*x3 +G*delta)/( L_12*(1+lam) )
    # Force equilibrium
    RB = - G - F - RA
    # Rotation at B from beam slope relation -> Bearing moment
    MB = lamL*RA # derived from first-principles    # eq.3
    return RA, RB, MB

def analytical_MBforces_EBbeam(
        Fx,Fy,Fz, Mx,My,Mz, m_carrier,delta,tilt,
        L_h1,L_12, EI, k, return_M=False
    ):
    """
    Two-bearing euler-bernoulli beam shaft model for moment reacting MB2\\
    using EB-beam theory between the two bearing span (A-B),\\
    with MB2 @ B supports moment `M`, with stiffness `k`, so: `M = k*theta`.

    Internal Progress
    -----------------
    - DONE : implementation
    - TODO : analytical derivatives; add arg 'flag_jac=Bool' as other funcs
    """
    # === sanity check and init ===
    gy = 0.0
    gx = gravity * np.sin(tilt)
    gz = -gravity * np.cos(tilt)
    n_ts, n_ws = Fx.shape[0], Fx.shape[1] # = 72e4, 10

    # === Loads on bearings ===
    F_mb1 = np.zeros( (n_ts,n_ws,4) ) # for 4 forces (ax,y,z,rad)
    F_mb2 = np.zeros( (n_ts,n_ws,4) ) # for 4 forces (ax,y,z,rad)

    # solve bearing system in planes
    # 1. y-x
    G = m_carrier*gy
    F_mb1_y, F_mb2_y, M_mb2_y = solve_bearing_system(
                -Mz, Fy, L_h1, L_12, delta, G, EI, k)
    # 1. z-x
    G = m_carrier*gz
    F_mb1_z, F_mb2_z, M_mb2_z = solve_bearing_system(
                +My, Fz, L_h1, L_12, delta, G, EI, k)

    # assemble forces
    # --- MB1 (CRB) ---
    F_mb1_ax = np.zeros_like(Fx)
    F_mb1_rad = np.hypot(F_mb1_y, F_mb1_z) # element-wise

    # --- MB2 (DRTRB) ---
    G = m_carrier*gx
    F_mb2_ax = np.abs( -Fx - G ) # `abs` coz mb2 reacts to the axial load, regardless if tensile or compressive.
    F_mb2_rad = np.hypot(F_mb2_y, F_mb2_z) # element-wise

    # ----- collect for outputs
    F_mb1 = np.stack([F_mb1_ax, F_mb1_y, F_mb1_z, F_mb1_rad])
    F_mb2 = np.stack([F_mb2_ax, F_mb2_y, F_mb2_z, F_mb2_rad])
    
    if not return_M: return F_mb1, F_mb2
    else:
        M_mb2 = np.stack([M_mb2_y, M_mb2_z])
        return F_mb1, F_mb2, M_mb2
# ---------------