import ROOT
import numpy as np
import root_numpy as rnm

import noise_calculations as n_calc
import run_log_metadata as md
import data_management as dm

from pathos.multiprocessing import ProcessingPool as Pool

ROOT.gROOT.SetBatch(True)


def noiseAnalysis():
    
    dm.defineDataFolderPath()
    startTime = md.dm.getTime()
    runLog_batch = md.getRunLogBatches(md.batchNumbers)
    
    print "\nStart NOISE analysis, batches:", md.batchNumbers
 
    for runLog in runLog_batch:
        
        if md.limitRunNumbers != 0:
            runLog = runLog[0:md.limitRunNumbers] # Restrict to some run numbers
    
        startTimeBatch = dm.getTime()
        dm.printTime()
        
        print "Batch:", runLog[0][5], len(runLog), "run files.\n"
      
        for index in range(0, len(runLog)):
     
            md.defineGlobalVariableRun(runLog[index])

            print "Run", md.getRunNumber()
            
            noise_average, noise_std = noiseAnalysisPerRun()
            dm.exportNoiseDataPlot(noise_std, noise_average)
            
            print "Done with run", md.getRunNumber(),"\n"


        print "Done with batch",runLog[0][5],"Time analysing: "+str(md.dm.getTime()-startTimeBatch)+"\n"

    print "Done with NOISE analysis. Time analysing: "+str(md.dm.getTime()-startTime)+"\n"

def noiseAnalysisPerRun():
    
    # Configure inputs for multiprocessing
    max = md.getNumberOfEvents()
    step = 10000
    threads = 4
    
    p = Pool(threads)
    ranges = range(0, max, step)
    
    dataPath = dm.getDataPath()
    results = p.map(lambda chunk: multiProcess(dataPath, chunk, chunk+step), ranges)

    # results change form, now each element is a variable
    results_variables = n_calc.concatenateResults(results)
    
    return results_variables


# Start multiprocessing analysis of noises and pulses in ROOT considerOnlyRunsfile
def multiProcess(dataPath, begin, end):

    data = rnm.root2array(dataPath, start=begin, stop=end)

    return n_calc.findNoiseAverageAndStd(data)



