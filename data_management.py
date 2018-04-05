import numpy as np
import root_numpy as rnm
import os
import datetime as dt

import metadata as md


# Export noise data
def exportNoiseData(noise, pedestal):

    exportROOTFile(noise,  "noise", "noise")
    exportROOTFile(pedestal, "noise", "pedestal")


# Export pulse data
def exportPulseData(peak_times, peak_values, rise_times, cfd05):

    exportROOTFile(peak_times, "pulse", "peak_time")
    exportROOTFile(peak_values, "pulse", "peak_value")
    exportROOTFile(rise_times, "pulse", "rise_time")
    exportROOTFile(cfd05, "pulse", "cfd05")


# Export timing data
def exportTimingLinearData(time_difference):

    exportROOTFile(time_difference, "timing","linear")


def exportTimingLinearRiseTimeRefData(time_difference):

    exportROOTFile(time_difference, "timing","linear_cfd05")


def exportTimingSysEqData(time_difference):

    exportROOTFile(time_difference, "timing","sys_eq")


def exportTimingSysEqRiseTimeRefData(time_difference):

    exportROOTFile(time_difference, "timing","sys_eq_cfd05")



def exportTrackingData(sensor_position):

    exportROOTFile(sensor_position, "tracking", "position")



# Export results

def exportNoiseResults(noise_results, sensor_info):

    exportROOTFile(noise_results, "results", "noise", sensor_info)


def exportPulseResults(pulse_results, sensor_info):

    exportROOTFile(pulse_results, "results", "pulse", sensor_info)


def exportTimingResults(timing_results, sensor_info, same_osc, cfd05):
    
    exportROOTFile(timing_results, "results", "timing", sensor_info, same_osc, cfd05)


def exportTimingResultsSysEq(timing_results, sensor_info, cfd05):
    
    exportROOTFile(timing_results, "results", "timing_sys_eq", sensor_info, False, cfd05)



# Export ROOT file with selected information
def exportROOTFile(data, group, category="", sensor_info=[], same_osc=False, cfd05=False):
    
    if group == "timing":
    
        fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+str(group)+"_"+str(category)+"_"+str(md.getRunNumber())+".root"
    
    elif category == "position":
    
        fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+str(category)+"_"+str(md.getBatchNumber())+".root"

    elif group == "results":
    
        if category == "timing":
        
            fileName = getSourceFolderPath()+"results_hgtd_efficiency_sep_2017/"+sensor_info[0]+"/"+category+"/normal/"+category+"_"+str(md.getBatchNumber())+"_"+sensor_info[1]+"_diff_osc_cfd05_results.root"
        
            if same_osc:
                fileName = fileName.replace("diff_osc", "same_osc")
        
            if not cfd05:
                fileName = fileName.replace("cfd05_", "")
    
        elif category == "timing_sys_eq":
            
            category = category.replace("timing_sys_eq", "timing")

            fileName = getSourceFolderPath()+"results_hgtd_efficiency_sep_2017/"+sensor_info[0]+"/"+category+"/system/"+category+"_"+str(md.getBatchNumber())+"_"+sensor_info[1]+"_sys_eq_cfd05_results.root"
            
            if not cfd05:
                fileName = fileName.replace("cfd05_", "")
        
        else:
        
            fileName = getSourceFolderPath()+"results_hgtd_efficiency_sep_2017/"+sensor_info[0]+"/"+category+"/"+category+"_"+str(md.getBatchNumber())+"_"+sensor_info[1]+"_results.root"

    
    else:
        fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+str(group)+"_"+str(category)+"/"+str(group)+"_"+str(category)+"_"+str(md.getRunNumber())+".root"

    if group != "timing" and group != "results":
        data = changeDTYPEOfData(data)


    rnm.array2root(data, fileName, mode="recreate")


def exportROOTHistogram(graphList, fileName):

    rootDestination = fileName.replace("plots_hgtd_efficiency_sep_2017", "plots_data_hgtd_efficiency_sep_2017")
    rootDestination = rootDestination.replace(".pdf", ".root")
    fileObject = ROOT.TFile(rootDestination, "RECREATE")
    fileObject.Close()



# Import noise data file
def importNoiseFile(category):
    
    return importROOTFile("noise", category)


def importNoiseFilePlot(category):
    
    return importROOTFile("noise_plot", category)


# Import pulse data file
def importPulseFile(category):

    return importROOTFile("pulse", category)

def importTrackingFile(category=""):

    return importROOTFile("tracking", category)

def importTimingFile(category):

    return importROOTFile("timing", category)


# import results

def importNoiseResults(sensor_info):

    return importROOTFile("results", "noise", sensor_info)


def importPulseResults(sensor_info):

    return importROOTFile("results", "pulse", sensor_info)


def importTimingResults(sensor_info, same_osc, cfd05):
    
    return importROOTFile("results", "timing", sensor_info, same_osc, cfd05)


def importTimingResultsSysEq(sensor_info, same_osc, cfd05):
    
    return importROOTFile("results", "timing_sys_eq", sensor_info, same_osc, cfd05)



# Import selected ROOT file
def importROOTFile(group, category="", sensor_info=[], same_osc=False, cfd05=False):

    if group == "tracking":
        
        if category == "":
        
            fileName = getSourceFolderPath()+"tracking_data_sep_2017/tracking"+md.getTimeStamp()+".root"
        
        else:
            fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+group+"/"+category+"_"+str(md.getBatchNumber())+".root"

    
    elif group == "timing":
    
        fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+str(group)+"_"+str(category)+"_"+str(md.getRunNumber())+".root"


    elif group == "results":
    
        if category == "timing":
        
            fileName = getSourceFolderPath()+"results_hgtd_efficiency_sep_2017/"+sensor_info[0]+"/"+category+"/diff_osc/"+category+"_"+str(md.getBatchNumber())+"_"+sensor_info[1]+"_diff_osc_cfd05_results.root"
        
            if same_osc:
                fileName = fileName.replace("diff_osc", "same_osc")
        
            if not cfd05:
                fileName = fileName.replace("cfd05_", "")
    
        elif category == "timing_sys_eq":
            
            category = category.replace("timing_sys_eq", "timing")

            fileName = getSourceFolderPath()+"results_hgtd_efficiency_sep_2017/"+sensor_info[0]+"/"+category+"/system/"+category+"_"+str(md.getBatchNumber())+"_"+sensor_info[1]+"_sys_eq_cfd05_results.root"
            
            if not cfd05:
                fileName = fileName.replace("cfd05_", "")
        
        else:
        
            fileName = getSourceFolderPath()+"results_hgtd_efficiency_sep_2017/"+sensor_info[0]+"/"+category+"/"+category+"_"+str(md.getBatchNumber())+"_"+sensor_info[1]+"_results.root"
    
    elif group == "noise_plot":
    
        group = group.replace("noise_plot", "noise")
    
        fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+str(group)+"_"+str(category)+"_plot/"+str(group)+"_"+str(category)+"_"+str(md.getRunNumber())+".root"
    
    
    else:
    
        fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+str(group)+"_"+str(category)+"/"+str(group)+"_"+str(category)+"_"+str(md.getRunNumber())+".root"
        
        
    return rnm.root2array(fileName)

def convertNoiseData(noise_average, noise_std):
    
    for chan in noise_std.dtype.names:
        noise_average[chan] =  np.multiply(noise_average[chan], -1000)
        noise_std[chan] = np.multiply(noise_std[chan], 1000)

    return noise_average, noise_std



def convertPulseData(peak_values):
    
    for chan in peak_values.dtype.names:
        peak_values[chan] =  np.multiply(peak_values[chan], -1000)

    return peak_values

def convertRiseTimeData(rise_times):
    
    for chan in rise_times.dtype.names:
        rise_times[chan] =  np.multiply(rise_times[chan], 1000)

    return rise_times



def changeDTYPEOfData(data):


    if len(data.dtype.names) == 7:
    
        data = data.astype(  [('chan0', '<f8'), ('chan1', '<f8') ,('chan2', '<f8') ,('chan3', '<f8') ,('chan4', '<f8') ,('chan5', '<f8') ,('chan6', '<f8') ] )

    else:
        data = data.astype(  [('chan0', '<f8'), ('chan1', '<f8') ,('chan2', '<f8') ,('chan3', '<f8') ,('chan4', '<f8') ,('chan5', '<f8') ,('chan6', '<f8') ,('chan7', '<f8')] )

    return data


# Create array for exporting center positions, inside tracking
def createCenterPositionArray():

    dt = (  [('chan0', '<f8', 2), ('chan1', '<f8', 2) ,('chan2', '<f8', 2) ,('chan3', '<f8', 2) ,('chan4', '<f8', 2) ,('chan5', '<f8', 2) ,('chan6', '<f8', 2) ,('chan7', '<f8', 2)] )
    
    return np.zeros(1, dtype = dt)


# Check if the repository is on the stau server
def checkIfRepositoryOnStau():

    threadNumber = 4
    
    # sourceFolderPath is for plots, data, tracking data etc
    sourceFolderPath = "/Users/aszadaj/cernbox/SH203X/HGTD_material/"
    
    if os.path.dirname(os.path.realpath(__file__)) == "/home/aszadaj/Gitlab/HGTD-Efficiency-analysis":
    
        threadNumber = 16
        sourceFolderPath = "/home/warehouse/aszadaj/HGTD_material/"
        onStau = True
    
        setIfOnHDD(False)

    defineNumberOfThreads(threadNumber)
    defineDataFolderPath(sourceFolderPath)


# Get actual time
def getTime():

    return dt.datetime.now().replace(microsecond=0)


# Print time stamp
def printTime():

    time = str(dt.datetime.now().time())
    print  "\nTime: " + str(time[:-7])

def setIfOnHDD(value):

    global hdd
    hdd = value

def isOnHDD():

    return hdd

def setIfOnHITACHI(value):

    global hitachi
    hitachi = value

def isOnHITACHI():

    return hitachi

# Define folder where the pickle files should be
def defineDataFolderPath(source):

    global sourceFolderPath
    sourceFolderPath = source


# Return path of data files
def getSourceFolderPath():

    return sourceFolderPath


def getDataPath():

    dataPath = getSourceFolderPath() + "oscilloscope_data_sep_2017/data_"+str(md.getTimeStamp())+".tree.root"
    
    if isOnHDD():
    
        dataPath = "/Volumes/HDD500/" + "oscilloscope_data_sep_2017/data_"+str(md.getTimeStamp())+".tree.root"

    elif isOnHITACHI():
    
        dataPath = "/Volumes/HITACHI/" + "oscilloscope_data_sep_2017/data_"+str(md.getTimeStamp())+".tree.root"


    return dataPath


# Define thread number or multiprocessing
def defineNumberOfThreads(number):

    global threads
    threads = number

def setNumberOfThreads(number):
    threads = number

