#%%
# IMPORTS
import numpy as np

#%%
def spectrum_pierson_moskowitz( frequencies, Hs, Tp ):
    """
    Pierson-Moskowitz Spectrum
    to describe random sea waves

    reference: sec.6.4.3.2, eq.6.57, Manwell 2024 - Wind Energy Explained
    """
    fp = 1.0 / Tp

    S = (
        0.3125
        * (Hs**2)
        * (fp**4)
        * np.maximum(frequencies, 1e-6)**(-5)
        * np.exp(
            -1.25 * (fp / np.maximum(frequencies,1e-6))**4
        )
    )

    return S

#%%
def spectrum_jonswap(frequencies, Hs, Tp, gamma=3.3):
    """
    JONSWAP Spectrum
    to describe random sea waves

    reference: sec.6.4.3.3, Manwell 2024 - Wind Energy Explained
    """

    def calculate_gamma_from_Hs_Tp(Hs, Tp):
        """
        reference: eq.6.59
        """
        ratio = Tp / np.sqrt(Hs)

        if ratio < 3.6:
            gamma = 5
        elif ratio <= 5:
            gamma = np.exp( 5.75 - 1.15*ratio )
        else:
            gamma = 1

        return gamma

    if gamma == None: gamma = calculate_gamma_from_Hs_Tp(Hs, Tp)

    fp = 1.0 / Tp

    sigma = np.where(          # eq. 6.60
        frequencies <= fp,
        0.07,
        0.09
    )

    alpha = np.exp(
        -(
            (frequencies - fp)**2
        ) /
        (
            2.0 * (sigma**2) * (fp**2)
        )
    )

    C = 1 - 0.287 * np.log(gamma) # eq. 6.61

    S = (
        C
        * spectrum_pierson_moskowitz(frequencies,Hs,Tp)
        * (gamma**alpha)
    )

    return S
#%%
def spectrum_kaimal(
        frequencies,
        U,
        Hhub=150.0,
        sigma_u=0.14):
    """
    Kaimal Spectrum
    to describe turbulent wind

    reference: eq. 6.10, Manwell 2024 - Wind Energy Explained
    """

    lambda1 = np.where(             # eq. 6.11
        Hhub <= 60., 0.7*Hhub, 42
    )

    L = 8.1*lambda1

    n = 6.0 * frequencies * L / U

    S = (
        4 * sigma_u**2 * L / U
        /
        (1 + n)**(5.0/3.0)
    )

    return S
#%%
def calculate_2_std_of_rotor_speed_samples(
        rotor_speed_ts, rpm_min, rpm_rated
    ):
    """
    for 1P, 3P bands.

    Under an approximately normal distribution, +/- 2 sigma covers about 95% of the values.
    Rotor-speed distribution from eg. `OpenFAST/WEIS`.

    Output
    _____
    margins for 1P and 3P bands
    """

    # ==================================================
    # 1P / 3P bands with ±2 standard deviations
    # ==================================================

    # Obtain this from rotor-speed time-series data [rpm]
    # Example:
    rotor_speed_samples_rpm = np.asarray(rotor_speed_ts)

    sigma_rpm = np.std(rotor_speed_samples_rpm, ddof=1)

    # Nominal frequency ranges [Hz]
    f_1P = np.sort(np.array([rpm_min, rpm_rated]) / 60.0)
    f_3P = 3.0 * f_1P

    # Frequency standard deviations [Hz]
    sigma_f_1P = sigma_rpm / 60.0
    sigma_f_3P = 3.0 * sigma_rpm / 60.0

    # ±2σ margins
    margin_1P = 2.0 * sigma_f_1P
    margin_3P = 2.0 * sigma_f_3P

    return margin_1P, margin_3P
