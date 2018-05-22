import numpy as np
import metadata as md
import ROOT

def getTimeDifferencePerRun(time_location):
    
    time_difference = np.zeros(len(time_location), dtype = time_location.dtype)
    
    SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")

    for chan in time_location.dtype.names:
        
        if SiPM_chan == chan:
            continue
            
        for event in range (0, len(time_location)):
            if time_location[SiPM_chan][event] != 0 and time_location[chan][event] != 0:
                time_difference[chan][event] = (time_location[chan][event] - time_location[SiPM_chan][event])*1000


    return time_difference


# This is used to produce ROOT files which have multiple solutions
# Note that the system of equations only applies to the first oscilloscope
# Reason: the first oscilloscope contains different sensors.
def getTimeDifferencePerRunSysEq(time_location):
    
    dt = (  [('chan0',  '<f8', 3), ('chan1',  '<f8', 3) ,('chan2',  '<f8', 3) ,('chan3',  '<f8', 3)] )
    
    time_difference = np.zeros(len(time_location), dtype = dt)

    osc1 = ["chan0", "chan1", "chan2", "chan3"]

    for chan in osc1:
    
        chan2_list = list(osc1)
        chan2_list.remove(chan)
        
        for event in range(0, len(time_location[chan])):
            
            time_difference[chan][event] = np.zeros(3)
            
            for index in range(0, len(chan2_list)):
                chan2 = chan2_list[index]
                if time_location[chan][event] != 0 and time_location[chan2][event] != 0:
                   
                    value = (time_location[chan][event] - time_location[chan2][event])*1000
                    time_difference[chan][event][index] = value


    return time_difference

# The input is of the convoluted form, that is \sigma_{ij} (here the DUT and the SiPM) and the
# corresponding errors, that is \Delta\sigma_{ij}
# Output are the solutions for the individual widths, \sigma_{k} and
# the corresponding errors, \Delta\sigma_{k}, where k is the connected LGAD in
# the oscilloscope (up to four different)
def solveLinearEq(sigmas, sigmas_error):

    # Non-singular matrix selected
    matrix = np.matrix([[1, 0, 0, 1], [0, 1, 1, 0], [0, 0, 1, 1], [0, 1, 0, 1]])
    inverse = np.linalg.inv(matrix)
    
    sigma_vector = np.power(np.array([sigmas[0][3], sigmas[1][2], sigmas[2][3], sigmas[1][3]]), 2)
    sigma_vector_error = np.power(np.array([sigmas_error[0][3], sigmas_error[1][2], sigmas_error[2][3], sigmas_error[1][3]]), 2)
    
    sigma_chan = np.sqrt(inverse.dot(sigma_vector))
    sigma_chan_error = np.sqrt((inverse.dot(sigma_vector)).dot(sigma_vector_error)*np.power(inverse.dot(sigma_vector), -1))
    
    
    # Given that width can be expressed as \sigma_{i}^2 = C_1\sigma_{A}^2 + C_2\sigma_{B}^2 and
    # the error is given for \Delta\sigma_{A} and \Delta\sigma_{A},
    # then the total error for \sigma_{i} will be
    #
    # \Delta_sigma_{i} = \sqrt{\frac{C_1\sigma_{A}^2\Delta\sigma_{A}^2 + C_2\sigma_{B}^2\Delta\sigma_{B}^2}{C_1\sigma_{A}^2 + C_2\sigma_{B}^2}}
    
    return sigma_chan, sigma_chan_error


def getSigmasFromFit(th1d_list, chan):

    # Find the maximal value
    MPV_bin = th1d_list.GetMaximumBin()
    MPV_time_diff = int(th1d_list.GetXaxis().GetBinCenter(MPV_bin))
    MPV_entries = th1d_list.GetMaximum()
    
    # Change the window
    window_range = 1000
    xMin = MPV_time_diff - window_range
    xMax = MPV_time_diff + window_range
    th1d_list.SetAxisRange(xMin, xMax)
    
    # Fit using normal gaussian
    N = 3
    sigma_window = th1d_list.GetStdDev()
    mean_window = th1d_list.GetMean()
    xMin = mean_window - N * sigma_window
    xMax = mean_window + N * sigma_window

    # Within the same oscilloscope
    if md.checkIfSameOscAsSiPM(chan):
        
        fit_function = ROOT.TF1("gaus_fit", "gaus", xMin, xMax)

    # Else in different oscilloscopes
    else:

        fit_function = ROOT.TF1("gaus_fit", "[0]*exp(-0.5*((x-[3])/[2])^2) + [1]*exp(-0.5*((x-([3]+100))/[2])^2)", xMin, xMax)
        fit_function.SetParameters(MPV_entries, MPV_entries, sigma_window, mean_window)
        fit_function.SetParNames("Constant 1", "Constant 2", "\sigma_{tot}", "Mean 1")

    try:
        # Create fit and calculate the width
        th1d_list.Fit("gaus_fit", "Q", "", xMin, xMax)
        sigma_SiPM = md.getSigmaSiPM()
        sigma_fit = th1d_list.GetFunction("gaus_fit").GetParameter(2)
        sigma_fit_error = th1d_list.GetFunction("gaus_fit").GetParError(2)
    
        if sigma_fit > sigma_SiPM:
            sigma_DUT = np.sqrt(np.power(sigma_fit, 2) - np.power(sigma_SiPM, 2))

        else:
            sigma_DUT = 0

    # In case that the fit fails, due to no data, ignore the result.
    except:

        sigma_DUT = 0
        sigma_fit_error = 0


    return sigma_DUT, sigma_fit_error
