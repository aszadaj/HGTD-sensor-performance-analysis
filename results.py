import ROOT
import root_numpy as rnm
import numpy as np
import os
import math

import metadata as md
import data_management as dm

def produceResults():
    
    dm.checkIfRepositoryOnStau()
    startTime = md.dm.getTime()
   
    runLog = md.getRunLog()
    
    fileDirectoryResults = dm.getSourceFolderPath() + "results/"
    
    print "\nStart RESULTS"
    
    resultGraphs = dict()
    legend = dict()
    
    canvas = ROOT.TCanvas("Results", "Results")
    
    sensorNames = md.getAllSensorNames()
    #sensorNames = ["W4-S1061"]
    sensorNames.remove("SiPM-AFP")
    
    sourceResultsFiles = dm.getSourceFolderPath() + "results_hgtd_efficiency_sep_2017/"
    
    #categories = ["noise", "pedestal", "peak_value", "rise_time" "timing_normal", "timing_system"]
    categories = ["noise", "pedestal", "peak_value", "rise_time", "timing_normal"]

    #categories = ["timing_system"]
    #categories = ["peak_value"]
    
    resultsDict = dict()
    
    for sensor in sensorNames:
        
        if sensor != "W9-LGA44" and sensor != "W4-S1030":
            continue
    
        print "\nSensor", sensor
        fileDirectory = sourceResultsFiles + sensor + "/"
 
        for category in categories:
            # Have to define the global variable to make the code work
            
            if category == "timing_system" and (sensor == "W4-S215" or sensor == "W4-S204_6e14" or sensor == "W4-RD01"):
                continue
            
            files = readFileNames(fileDirectory+"/"+category)
            file = files[0]
            fileName = fileDirectory+category+"/"+file
            chan = "chan" + file[file.find("chan")+4]
            results = rnm.root2array(fileName)
            batchNumber = getBatchNumberFromFile(file)
            md.defineGlobalVariableRun(md.getRowForBatchNumber(batchNumber))
            
            extend_legend_box = 0
            
            if len(md.availableDUTPos(sensor, chan)) > 3:
            
                extend_legend_box = 0.1
            
            if category == "noise" or category == "pedestal":
                
                legend[category] = ROOT.TLegend(0.6, 0.9, 0.9, 0.7-extend_legend_box)
            
            elif category == "rise_time" or category == "timing_normal" or category == "timing_system":
            
                legend[category] = ROOT.TLegend(0.75, 0.9, 0.9, 0.7-extend_legend_box)
            
            else:
            
                legend[category] = ROOT.TLegend(0.15, 0.9, 0.3, 0.7-extend_legend_box)
            

            if category == "noise":
                titleGraph = "Noise values per bias voltage "
                xTitle = "Bias voltage [V]"
                yTitle = "Noise [mV]"
            
            elif category == "pedestal":
                titleGraph = "Pedestal values per bias voltage "
                xTitle = "Bias voltage [V]"
                yTitle = "Pedestal [mV]"

            elif category == "peak_value":
            
                titleGraph = "Pulse amplitude values per voltage "
                xTitle = "Bias voltage [V]"
                yTitle = "Pulse amplitude [mV]"

            elif category == "rise_time":
                
                titleGraph = "Rise time values per voltage "
                xTitle = "Bias voltage [V]"
                yTitle = "Rise time [ps]"

            elif category == "timing_normal":
            
                titleGraph = "Time resolution values per voltage "
                xTitle = "Bias voltage [V]"
                yTitle = "Time resolution [ps]"
            
            elif category == "timing_system":
            
                titleGraph = "Time resolution values per voltage (system)"
                xTitle = "Bias voltage [V]"
                yTitle = "Time resolution [ps]"


            # Goal: create three TGraphAsym

            resultsDict.clear()

            # Fill TGraphs according to DUT pos and temperature
            
            resultsDict["22"] = dict()
            resultsDict["-30"] = dict()
            resultsDict["-40"] = dict()
            
            for pos in md.availableDUTPos(sensor, chan):
            
                resultsDict["22"][pos] = []
                resultsDict["-30"][pos] = []
                resultsDict["-40"][pos] = []

            
            resultGraphs[category] = ROOT.TMultiGraph()
            

            for file in files:
                
                fileName = fileDirectory+category+"/"+file
                chan = "chan" + file[file.find("chan")+4]
                results = rnm.root2array(fileName)
            
                batchNumber = getBatchNumberFromFile(file)
                md.defineGlobalVariableRun(md.getRowForBatchNumber(batchNumber))
                
                voltage = md.getBiasVoltage(sensor)
                temperature = str(md.getTemperature())
                DUT_pos = md.getDUTPos(sensor, chan)
                resultsDict[temperature][DUT_pos].append([voltage, results])
        
            # At this point, all info is collected

            colorNumber = 6


            graph = dict()
            
            for temperature in ["22", "-30", "-40"]:
                markerStyle = 20
                for pos in md.availableDUTPos(sensor, chan):
                    if len(resultsDict[temperature][pos]) != 0:
                        graph[category] = ROOT.TGraphErrors()

                        graph[category].SetMarkerColor(colorNumber)
                        graph[category].SetMarkerStyle(markerStyle)
                        i = 0
    


                        for voltage, result in resultsDict[temperature][pos]:
                            graph[category].SetPoint(i, voltage, result[category][0])
                            
                            # For now, the error is not obtained
                            if category != "timing_system":
                                graph[category].SetPointError(i, 0, result[category][1])
                            else:
                                graph[category].SetPointError(i, 0, 0)
                            i += 1
                        
                        
                        resultGraphs[category].Add(graph[category])
                        
                        if category == "noise":
                            legend[category].AddEntry(graph[category], str(temperature) + " \circC, " + str(round(graph[category].GetMean(2),1)) + " \pm "+ str(round(graph[category].GetRMS(2),1)) + " mV" , "p")
                        else:
                            legend[category].AddEntry(graph[category], str(temperature) + " \circC", "p")

                    markerStyle += 1
                colorNumber += 1


            resultGraphs[category].Draw("AP")
            legend[category].SetTextSize(0.03)
            legend[category].SetBorderSize(1)
            legend[category].Draw()

            resultGraphs[category].SetTitle((titleGraph+" "+sensor))
            resultGraphs[category].GetXaxis().SetTitle(xTitle)
            resultGraphs[category].GetYaxis().SetTitle(yTitle)

            yMin = resultGraphs[category].GetHistogram().GetMinimum()
            yMax = resultGraphs[category].GetHistogram().GetMaximum()
            d = yMax-yMin

            dist = 7

            y_low = yMin - dist*d
            y_high = yMax + dist*d


            # Adapt this depending on graph
            if category == "noise" or category == "pedestal":
                resultGraphs[category].SetMinimum(y_low)
                resultGraphs[category].SetMaximum(y_high)

            canvas.Update()

            fileName = fileDirectoryResults +category+"/" + category + "_results_"+sensor+".pdf"

            canvas.Print(fileName)

            canvas.Clear()


def readFileNames(directory):

    # select those which have cfd05 reference
    if directory.find("timing") != -1:
        
        # CFD reference
        availableFiles = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f != '.DS_Store' and f.find("cfd05") != -1]
        
        # Peak reference
        availableFiles = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f != '.DS_Store' and f.find("cfd05") == -1]
    
    else:
        availableFiles = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f != '.DS_Store']
    availableFiles.sort()

    return availableFiles


def getBatchNumberFromFile(file):
    return int(file[file.find("chan")-4:file.find("chan")-1])

