import numpy as np
import sys

import data_management as dm
import run_log_metadata as md

def pulseAnalysis(data, pedestal, noise):

    channels = data.dtype.names
    
    osc_limit = findOscilloscopeLimit(data)

    # Set the time scope to 0.1 ns
    defTimeScope()
    
    # Time in event when the pulse reaches maximum
    peak_time       =   np.zeros(len(data), dtype = data.dtype)
    
    # Pulse amplitude
    peak_value      =   np.zeros(len(data), dtype = data.dtype)
    
    # Rise time
    rise_time       =   np.zeros(len(data), dtype = data.dtype)
    
    # Time at 50% of the rising edge
    cfd05           =   np.zeros(len(data), dtype = data.dtype)
    
    # Points above the threshold
    points           =   np.zeros(len(data), dtype = data.dtype)
    
    # Max sample of event given that there are points above the threshold
    max_sample      =   np.zeros(len(data), dtype = data.dtype)
    
    # Charge collected from the MIP
    charge          =   np.zeros(len(data), dtype = data.dtype)
    
    properties = [peak_time, peak_value, rise_time, cfd05, points, max_sample, charge]

    for chan in channels:
        for event in range(0, len(data)):
        
            variables = [data[chan][event], pedestal[chan], noise[chan], osc_limit[chan]]
            
            results = getPulseInfo(variables)
            
            for type in range(0, len(results)):
                properties[type][event][chan] = results[type]

    return properties


def getPulseInfo(variables):

    [data, pedestal, noise, osc_limit] = [i for i in variables]
    
    # Set start values
    peak_value = 0
    peak_time = 0
    rise_time = 0
    cfd05 = 0
    max_sample = 0
    points = 0
    charge = 0
    
    # Invert waveform data
    data = -data
    pedestal = -pedestal
    osc_limit = -osc_limit
    
    # Define threhsold and sigma level
    N = 4
    # This number has been argumented as a combined plot between max sample
    # point and number of points above the threhsold. See report.
    threshold_points = 5
    threshold = N * noise + pedestal
    
    if np.sum(data > threshold) >= threshold_points:
        
        points = calculatePoints(data, threshold)
        max_sample = np.amax(data)
        peak_value, peak_time  = calculatePeakValue(data, pedestal, noise, osc_limit)
        rise_time, cfd05  = calculateRiseTime(data, pedestal, noise)
        charge = calculateCharge(data, threshold)

        # Condition: if rise time or peak value cannot be found, disregard the pulse
        if peak_value == 0 or rise_time == 0:
            
            peak_value = peak_time = rise_time = cfd05 = charge = 0
        
    # Invert again to maintain the same shape
    return peak_time, -peak_value, rise_time, cfd05, points, -max_sample, charge


# Get Rise time
def calculateRiseTime(data, pedestal, noise, graph=False):
    
    # Default values
    rise_time = 0
    cfd05 = 0
    linear_fit = [0, 0]
    linear_fit_indices = [0]
    
    # Select points betweem 10 and 90 procent, before the max point
    linear_fit_bool = (data < np.amax(data)*0.9) & (data > np.amax(data)*0.1) & (np.nonzero(data) < np.argmax(data))[0]
    
    if np.sum(linear_fit_bool) > 0:
    
        linear_fit_indices = np.argwhere(linear_fit_bool).flatten()
        linear_fit_indices = getConsecutiveSeriesLinearFit(linear_fit_indices)
  
        # Require three points above threshold
        if len(linear_fit_indices) >= 3:

            x_values = linear_fit_indices * timeScope
            y_values = data[linear_fit_indices]
           
            linear_fit = np.polyfit(x_values, y_values, 1)
        
            if linear_fit[0] > 0:
                
                # Get rise time and CFD Z = 0.5 of the rising edge, pedestal corrected
                rise_time = 0.8 * (np.amax(data) - pedestal) / linear_fit[0]
                cfd05 = (0.5 * (np.amax(data) - pedestal) - linear_fit[1]) / linear_fit[0]

    if graph:
        return rise_time, cfd05, linear_fit, linear_fit_indices
    
    else:
        return rise_time, cfd05


def calculatePeakValue(data, pedestal, noise, osc_limit=350, graph=False):

    # Default values
    peak_value = 0
    peak_time = 0
    poly_fit = [0, 0, 0]

    # Select indices
    point_difference = 2
    first_index = np.argmax(data) - point_difference
    last_index = np.argmax(data) + point_difference
    poly_fit_indices = np.arange(first_index, last_index+1)
    
    
    # This is to ensure that the obtained value is the entry window
    if 2 < np.argmax(data) < 999:
    
        poly_fit_data = data[poly_fit_indices]
        poly_fit = np.polyfit((poly_fit_indices * timeScope), poly_fit_data, 2)

        if poly_fit[0] < 0:
            
            peak_time = -poly_fit[1]/(2 * poly_fit[0])
            peak_value = poly_fit[0] * np.power(peak_time, 2) + poly_fit[1] * peak_time + poly_fit[2] - pedestal
    

    # This is an extra check to prevent the second degree fit to fail and assign the maximum value instead
    if np.abs(np.amax(data) - osc_limit) < 0.01:

        peak_time = 0
        peak_value = np.amax(data)


    if graph:
        return peak_value, peak_time, poly_fit
    
    else:
        return peak_value, peak_time


def calculateCharge(data, threshold):
    
    # transimpendence is the same for all sensors, except for W4-RD01, which is unknown
    transimpendence = 4700
    voltage_integral = np.trapz(data[data > threshold], dx = timeScope)*10**(-9)
    charge = voltage_integral / transimpendence

    return charge

def calculatePoints(data, threshold):

    point_bool = data > threshold
    if np.any(point_bool):
        points_condition = np.argwhere(point_bool).flatten()
        points_condition = getConsecutiveSeriesPointCalc(data, points_condition)
        return len(points_condition)
    else:
        return 0



# Group each consequential numbers in each separate list
def group_consecutives(data, stepsize=1):
    return np.split(data, np.where(np.diff(data) != stepsize)[0]+1)



def getConsecutiveSeriesLinearFit(data):

    group_points = group_consecutives(data)
    group_points_max = [np.amax(group) for group in group_points]
    max_arg_series = group_points[group_points_max.index(max(group_points_max))]
    
    return max_arg_series


def getConsecutiveSeriesPointCalc(data, points_condition):

    group_points = group_consecutives(points_condition)
    group_points_max = [np.amax(data[group]) for group in group_points]
    max_arg_series = group_points[group_points_max.index(max(group_points_max))]
    
    return max_arg_series



# Get maximum values for given channel and oscilloscope
def findOscilloscopeLimit(data):

    channels = data.dtype.names
    osc_limit = np.empty(1, dtype=data.dtype)
    
    for chan in channels:
        osc_limit[chan] = np.amin(np.concatenate(data[chan]))

    return osc_limit


# related to multiprocessing
def concatenateResults(results):

    variable_array = []

    for variable_index in range(0, len(results[0])):
        
        variable = np.empty(0, dtype=results[0][variable_index].dtype)
        
        for clutch in range(0, len(results)):
        
            variable  = np.concatenate((variable, results[clutch][variable_index]), axis = 0)
        
        variable_array.append(variable)
    
        del variable

    return variable_array


def defTimeScope():
    global timeScope
    timeScope = 0.1
    return timeScope


