
import ROOT
import csv
import os
import datetime as dt


########## METADATA ##########

# Return run log imported from a .csv file
def getRunLog():
    
    tb_2017_run_log_file_name = "resources/run_list_tb_sep_2017.csv"
    metaData = []
    
    with open(tb_2017_run_log_file_name, "rb") as csvFile:
        fileData = csv.reader(csvFile, delimiter=";")
        for row in fileData:
            metaData.append(row)

    del metaData[0:2]
    return metaData


# Check inside folder which runs should be considered
def restrictToUndoneRuns(metaData, analysisType):

    folderPath = "data_hgtd_efficiency_sep_2017/pulse_files/pulse_amplitudes/"
    
    if analysisType == "noise":
        
        folderPath = "data_hgtd_efficiency_sep_2017/noise_files/noise_noise/"


    availableFiles = readFileNames(folderPath, analysisType)

    runLog = []
    
    for index in range(0, len(metaData)):
        if int(metaData[index][3]) not in availableFiles:
            runLog.append(metaData[index])
    
    return runLog



# Check inside folder which runs should be considered
def restrictToBatch(metaData, batchNumber):
   
    runLog = []
    
    for index in range(0, len(metaData)):
        if int(metaData[index][5]) == batchNumber:
            runLog.append(metaData[index])
    
    return runLog



# Restrict runs for telescope analysis for available files
def getRunLogForTelescopeAnalysis(numberOfBatches, numberOfRunsPerBatch):

    metaData = getRunLog()
    folderPath = "forAntek/"
    availableTimeStamps = readFileNames(folderPath, "telescope")
    
    runLog = []
    actualBatch = 0
    firstBatch = True
    numberOfRuns = numberOfRunsPerBatch
    
    for index in range(0, len(metaData)):
    
        if numberOfBatches == 0:
            break
    
        elif int(metaData[index][4]) in availableTimeStamps:
        
            currentBatch = int(metaData[index][5])
            
            if firstBatch:
                actualBatch = currentBatch
                firstBatch = False
        
            if numberOfRuns != 0 and actualBatch == currentBatch:
                runLog.append(metaData[index])
                numberOfRuns -= 1
            
            if actualBatch != currentBatch:
                numberOfBatches -= 1
                actualBatch = currentBatch
                numberOfRuns = numberOfRunsPerBatch

    return runLog

# Get run log for timing analysis
# Check this function if it correctly returns the right amount of runs
def getRunLogForTimingAnalysis(numberOfBatches, numberOfRunsPerBatch):

    metaData = getRunLog()
    
    runLog = []
    actualBatch = 0
    firstBatch = True
    numberOfRuns = numberOfRunsPerBatch
    
    for index in range(0, len(metaData)):
        
        currentBatch = int(metaData[index][5])
        
        if firstBatch:
            actualBatch = currentBatch
            firstBatch = False
        
        if actualBatch != currentBatch:
            numberOfBatches -= 1
            actualBatch = currentBatch
            numberOfRuns = numberOfRunsPerBatch
        
        if numberOfBatches == 0:
            break
        
        if numberOfRuns != 0:
            runLog.append(metaData[index])
            numberOfRuns -= 1

    return runLog


# Check if repository is on the stau server
def isRootFileAvailable(timeStamp):

    folderPath = "oscilloscope_data_sep_2017/"
    availableFiles = readFileNames(folderPath, "")
    
    found = False
    
    for file_name in availableFiles:
        if file_name == int(timeStamp):
            found = True
            break

    return found

# Check which files are available (either on stau or local)
def availableRunFiles():

    folderPath = "oscilloscope_data_sep_2017/"
    availableFiles = readFileNames(folderPath, "")

    runLog = getRunLog()

    availableRuns = []

    for row in runLog:
        if int(row[4]) in availableFiles:
            availableRuns.append(int(row[3]))

    return availableRuns



# Define folder where the pickle files should be
def defineDataFolderPath(source):

    global sourceFolderPath
    sourceFolderPath = source


# Return path of data files
def getSourceFolderPath():

    return sourceFolderPath


def readFileNames(folderPath, fileType):
    
    if fileType == "telescope": #tracking1504949898.root
        first_index = 8
        last_index = 18
    
    elif fileType == "noise": #noise_noise_3656 or pulse_amplitudes_3656
        first_index = 12
        last_index = 16

    elif fileType == "pulse":
        first_index = 17
        last_index = 21

    # Else, return timestamp of converted ROOT files data_'timestamp'.tree.root
    else:
        first_index = 5
        last_index = -10
    
    folderPath = getSourceFolderPath() + folderPath
    availableFiles = [int(f[first_index:last_index]) for f in os.listdir(folderPath) if os.path.isfile(os.path.join(folderPath, f)) and f != '.DS_Store']
    availableFiles.sort()

    return availableFiles


# Get current run number
def getRunNumber(timeStamp=""):
    
    if timeStamp == "":
        return runInfo[3]
    
    else:
        runLog = getRunLog()

        for row in runLog:
            if int(row[4]) == timeStamp:
                return int(row[3])


# Get current time stamp (which corresponds to the run number)
def getTimeStamp(runNumber=""):
    
    if runNumber == "":
        return runInfo[4]

    else:
        runLog = getRunLog()

        for row in runLog:
            if int(row[3]) == runNumber:
                return int(row[4])


# Get number of events inside the current ROOT file
def getNumberOfEvents():
    
    return int(runInfo[6])


# Get index for the name of the sensor in run log
def getChannelNameForSensor(sensor):

    for index in range(0,7):
        if runInfo[13+index*5] == sensor:
            return "chan"+str(index)


# Return name of sensor for chosen run and channel
def getNameOfSensor(chan):

    index = int(chan[-1:])
    return runInfo[13+index*5]


# Return batch number
def getBatchNumber():

    return int(runInfo[5])

# Return row in run log for given run number
def getRowForRunNumber(runNumber):

    runLog = getRunLog()

    for row in runLog:
        if int(row[3]) == runNumber:
            return row

# Set run info for selected run
def defineGlobalVariableRun(row):
    
    global runInfo
    runInfo = row


# Get actual time
def getTime():

    return dt.datetime.now().replace(microsecond=0)


# Print time stamp
def printTime():

    time = str(dt.datetime.now().time())
    print  "\nTime: " + str(time[:-7])

# Function for setting up ATLAS style plots
def setupATLAS():

    ROOT.gROOT.SetBatch()
    ROOT.gROOT.LoadMacro("./resources/style/AtlasStyle.C")
    ROOT.SetAtlasStyle()



