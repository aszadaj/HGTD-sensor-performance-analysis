import ROOT
import root_numpy as rnm
import numpy as np

import noise_calculations as n_calc
import noise_plot as n_plot
import metadata as md
import data_management as dm

from pathos.multiprocessing import ProcessingPool as Pool

ROOT.gROOT.SetBatch(True)


# Start analysis of selected run numbers
def noiseAnalysis(batchNumbers):
    
    dm.checkIfRepositoryOnStau()
    
    startTime = md.getTime()
   
    runLog_batch = md.getRunLogBatches(batchNumbers)

    print "\nStart noise analysis, batches:", batchNumbers
 
    for runLog in runLog_batch:
    
        #runLog = runLog[0:1] # Consider only 1  files for now
    
        results_batch = []
    
        startTimeBatch = md.getTime()
        md.printTime()
        
        print "Analysing batch:", runLog[0][5], "with", len(runLog),"run files.\n"
      
        for index in range(0, len(runLog)):
            
            row = runLog[index]
            md.defineGlobalVariableRun(row)
            runNumber = md.getRunNumber()
            
            if (md.isRootFileAvailable(md.getTimeStamp())):
            
                print "Run", md.getRunNumber()
                results_batch.append(noiseAnalysisPerRun())
                print "Done with run", md.getRunNumber()
        
            else:
                print "WARNING! There is no root file for run number: " + str(runNumber) + "\n"
    
        # Done with the for loop and appending results, export and produce files
        print "Done with batch", md.getBatchNumber(),"producing plots and exporting file.\n"
        
        noise_average = np.empty(0, dtype=results_batch[0][0].dtype)
        noise_std = np.empty(0, dtype=results_batch[0][1].dtype)
      
        for results_run in results_batch:
            noise_average = np.concatenate((noise_average, results_run[0]), axis = 0)
            noise_std = np.concatenate((noise_std, results_run[1]), axis = 0)

        
        pedestal, noise = n_calc.getPedestalAndNoisePerChannel(noise_average, noise_std)
        dm.exportNoiseData(pedestal, noise)
        
        n_plot.produceNoiseDistributionPlots(noise_average, noise_std)
    
        print "\nDone with final analysis and export. Time analysing: "+str(md.getTime()-startTimeBatch)+"\n"

    print "Done with batch",runLog[0][5],".\n"


def noiseAnalysisPerRun():
    
    startTime = md.getTime()
    
    # Configure inputs for multiprocessing
    p = Pool(dm.threads)
    #max = md.getNumberOfEvents()
    max = 200000 # This is adapted to match the number of telescope files
    #max = 1000
    step = 7000
    ranges = range(0, max, step)
    
    dataPath = md.getSourceFolderPath() + "oscilloscope_data_sep_2017/data_"+str(md.getTimeStamp())+".tree.root"
    
    results = p.map(lambda chunk: multiProcess(dataPath,chunk,chunk+step),ranges)

    # results change form, now each element is a variable
    results_variables = n_calc.convertNoise(results)
    
    return results_variables


# Start multiprocessing analysis of noises and pulses in ROOT considerOnlyRunsfile
def multiProcess(dataPath, begin, end):
    
    data = rnm.root2array(dataPath, start=begin, stop=end)
    noise_average, noise_std = n_calc.findNoiseAverageAndStd(data)
    
    return noise_average, noise_std




