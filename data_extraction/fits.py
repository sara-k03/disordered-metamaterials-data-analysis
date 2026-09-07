import numpy as np
from scipy.optimize import curve_fit

"""
Power law
x - x inputs
M - Type here 
n - Type here
"""
def power_law(x, M, n):
    return M * x ** n

"""
Type details about the function here
"""
def power_law_shift(x, M, n, x0):
    return M * (x - x0) ** n

def linear(x, a, b):
    return a*x + b

"""
Type details about the function here
"""
def shift_raw(x_up, y_up, x_down, y_down):
    
    # Shifting data to origin of COMPRESSION CYCLE
    
    x0 = x_up[np.argmin(x_up)]
    y0 = y_up[np.argmin(y_up)]

    x_up = x_up - x0
    y_up = y_up - y0
        
    x_down = x_down - x0
    y_down = y_down - y0

    return x_up, y_up, x_down, y_down, x0, y0


"""
Type details about the function here 
"""
def linear_fit( x_up, y_up, x_down, y_down ):
    # Shifting data to origin of COMPRESSION CYCLE

    x_up, y_up, x_down, y_down, x0, y0 = shift_raw(x_up, y_up, x_down, y_down)

    # Discards near-zero values to get rid of some negative numbers for noise
    mask_up = (y_up > 0) & (x_up > 0)  
    x_data_up = x_up[mask_up]
    y_data_up = y_up[mask_up]

    mask_down = (y_down > 0) & (x_down > 0) 
    x_data_down = x_down[mask_down]
    y_data_down = y_down[mask_down]

    alpha = 20

    # COMPRESSION CYCLE
    # Upper-end favoring fit directly in linear space 
    compression_params, _ = curve_fit(linear, x_data_up, y_data_up, sigma=1/(y_data_up**alpha), p0=[100, 1]) # p0 is the inital guess, sigma=1/y which favors the higher points  
    compression_slope, compression_intercept = compression_params

    # RELEASE CYCLE
    # Upper-end favoring fit directly in linear space 
    release_params, cov = curve_fit(linear, x_data_down, y_data_down, sigma=1/(y_data_down**alpha), p0=[100, 1]) # p0 is the inital guess, sigma=1/y which favors the higher points  
    release_slope, release_intercept = release_params

    release_errors = np.sqrt(np.diag(cov))
    release_slope_err, release_intercept_err = release_errors

    # FINDING LINEAR MODULUS
    # Y --> Young's Modulus 
    # Y = (Force / Area) / (L / L0) = (F * L0) / (Area * L) = ( F / L) * (L0 / Area) 
    # F / L is the slope of the graph in this case, so I multiply the slope by L0/Area to get Y

    l0 = 75 # The side length of a sample is 75 mm. The displacement is in mm, so we can keep the units in mm. 
    area = 75 * 75 # The area of the sample face is 75 * 75 mm^2
    linear_modulus = release_slope * ( l0 / area )
    linear_modulus_err = release_slope_err * (l0 / area)

    # Dimensional Analysis:
    # F / L --> N / mm 
    # L0 / area = 1 / mm
    # Y = F / m^2 --> Which is a pascal, which is correct

    # Equations
    compression_eq = f"F={compression_slope:.2e}x + {compression_intercept:.2f}"
    release_eq = f"F={release_slope:.2e}x + {release_intercept:.2f}"

    return linear_modulus, linear_modulus_err, x_data_up, linear(x_data_up, *compression_params), compression_eq, x_data_down, linear(x_data_down, *release_params), release_eq
     

"""
Type details about the function here
"""
def power_fit( x_up, y_up, x_down, y_down ):

    # Shifting data to origin of COMPRESSION CYCLE

    x_up, y_up, x_down, y_down, x0, y0 = shift_raw(x_up, y_up, x_down, y_down)

    # Discards near-zero values to get rid of some negative numbers for noise
    mask_up = (y_up > 0) & (x_up > 0)  
    x_data_up = x_up[mask_up]
    y_data_up = y_up[mask_up]

    mask_down = (y_down > 0) & (x_down > 0) 
    x_data_down = x_down[mask_down]
    y_data_down = y_down[mask_down]

    # COMPRESSION CYCLE
    # Upper-end favoring fit directly in linear space 
    compression_params, c_cov = curve_fit(power_law, x_data_up, y_data_up, sigma=1/y_data_up, p0=[100, 1]) # p0 is the inital guess, sigma=1/y which favors the higher points  
    M_compression, n_compression = compression_params

    compression_errors = np.sqrt(np.diag(c_cov))
    _, n_compression_err = compression_errors

    # RELEASE CYCLE
    # Upper-end favoring fit directly in linear space 
    release_params, r_cov = curve_fit(power_law_shift, x_data_down, y_data_down, sigma=1/y_data_down, p0=[100, 1, 0]) # p0 is the inital guess, sigma=1/y which favors the higher points  
    M_release, n_release, x0_release = release_params

    release_errors = np.sqrt(np.diag(r_cov))
    _, n_release_err, _ = release_errors

    # Individual Values
    compression_data = [M_compression, n_compression, x0, y0]
    release_data = [M_release, n_release, x0_release, x0, y0]

    # Equations
    compression_eq = f"F={M_compression:.2e} * x^{n_compression:.2f}"
    release_eq = f"F={M_release:.2e} * (x-{x0_release:.2f})^{n_release:.2f}"

    # The first two values being returned are compression exponent and release exponent
    return compression_data[1], release_data[1], x_data_up, power_law(x_data_up, *compression_params), compression_eq, x_data_down, power_law_shift(x_data_down, *release_params), release_eq, n_compression_err, n_release_err 


    