#############################################
#                                           #
#                                           #
#         HGTD EFFICIENCY ANALYSIS          #
#                                           #
#                                           #
#############################################

import noise
import pulse
import telescope
import timing
import metadata

#md.setupATLAS()

def main():

    ######  NOISE, PULSE, TELESCOPE AND TIMING   ######
    
    batchNumber = [101]
    
    metadata.setLimitRunNumbers(4) # How many run numbers in each batch
    metadata.setQuickParameter(False) # Quick check
    
    noise.noiseAnalysis           (batchNumber)
    
    pulse.pulseAnalysis           (batchNumber)
    
    #telescope.telescopeAnalysis   (batchNumber)
    
    timing.timingAnalysis         (batchNumber)
    
    
    exit()


main()

# Log1 09.12.2017
# redefined sigma value after check in the waveforms function
# Program is adapted to receive code in batches and exports them as pickle files
# amplitudes and rise time are large, but not too large.
# New file rise time half maximum is a reference point for

# Log2
# The lowered sigma gives more values but the SiPM have a higher noise and the sigma is
# too low. There fore testing with sigma = 6 for SiPM and sigma=5 for rest of the sensors

# log3
# Checked how many values are removed percentually and its about
#Fraction of removed amplitudes, due to critical value
#0.001 chan0
#0.001 chan1
#0.001 chan2
#0.001 chan3
#0.015 chan4
#0.009 chan5
#0.0135 chan6


# log

# improved the polyfit analysis, now check how the distributions look like

# Changed also the way of obtaining the first index when calculating a pulse. I removed earlier three points, now there is only one, deduced that from observing where the threshold is situated


# log 15122017 changed analysis of noise, noted that there is a problem with selecting the area
# and how the dataset is chosen
# noted that the fix will be better if condition set on len of data points which should be 1002.

# Available batch numbers:
# 101, 102, 103, 104, 105, 106, 107, 108
# 203, 204, 205, 206, 207,
# 301, 302, 303, 304, 305, 306,
# 401, 403, 404, 405, 406,
# 501, 502, 503, 504, 505, 506, 507,
# 701, 702, 703, 704, 705, 706, 707


