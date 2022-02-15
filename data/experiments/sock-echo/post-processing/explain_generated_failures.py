import os
import random 
import sys
import time

def postProcess(id,nFailures,nIterations):
    # output files
    outputsFile = "outputs" + id + ".txt"
    outputs = open(outputsFile,"w")
    timesFile = "times" + id + ".csv"
    times = open(timesFile,"w")

    # get absolute path of folder with logs
    logFolder = os.path.abspath("../generated-logs")

    # get absolute path of templater
    templates = os.path.abspath("../../../templates/chaos-echo" + id + ".yml")

    # process log subfolders, separately
    subfolders = os.listdir(logFolder)
    subfolders.sort()
    for subfolder in subfolders:
        print("Processing logs in " + subfolder)

        # get logfiles in subfolder
        logSubfolder = os.path.join(logFolder,subfolder)
        logFiles = os.listdir(logSubfolder)
        logFiles.sort()

        # write subfolder name in outputs
        outputs.write("* "*20 + "\n")
        outputs.write("*\t" + subfolder + "\n")
        outputs.write("* "*20 + "\n\n")

        # process each log file, separately
        for file in logFiles:
            print("|- " + file)

            # variable for computing avg time 
            avgTime = 0
           
            # get absolute of log file 
            logFile = os.path.join(logSubfolder,file)
            
            # get frontend "failures" in considered "logFile"
            grepFailures = "grep ERROR '" + logFile + "' | grep _edgeRouter | grep -v own"
            allFailures = os.popen(grepFailures)
            failures = list(allFailures)
            # failures = failures[:nFailures] # considering the first generated failures
            failures = random.sample(failures,nFailures) # considering the a random subset of generated failures
            # failures = failures[-nFailures:] # considering the last generated failures

            # write heading in outputs
            outputs.write("> " + file + " (" + str(len(failures)) + " failures)\n\n")
            
            # process each failure event of the frontend, separately
            for failure in failures:
                # generate JSON file containing the failure to explain 
                failureJSON = open("failure","w")
                failureJSON.write(failure)
                failureJSON.close()
                cwd = os.getcwd()
                failureFile = os.path.join(cwd,"failure")

                # write failure on outputs
                outputs.write(failure)

                # process failure file with "yrca.py"
                explanations = os.path.join(cwd,"explanations")
                os.chdir("../../../..")
                runExplainer = "python3 yrca.py '" + failureFile + "' '" + logFile + "' '" + templates + "'"
                startTime = time.time()
                os.system(runExplainer + " > '" + explanations + "'")
                endTime = time.time()

                # write computed "outputs"
                expLines = open(explanations, "r")
                exps = list(expLines)
                if len(exps) == 1:
                    outputs.write(exps[0])
                else: 
                    for exp in exps[:-1]: # copy all lines (but the last one)
                        if exp != "  \n": # exclude newlines
                            outputs.write(exp)

                # flush outputs' buffer
                outputs.flush()      

                # repeat run for a total of "nIterations" times to measure "avgTime" of the run
                avgTimeRun = endTime - startTime
                for _ in range(nIterations-1):
                    startTime = time.time()
                    os.system(runExplainer + " > /dev/null")
                    endTime = time.time()
                    avgTimeRun += (endTime - startTime) 
                avgTimeRun = avgTimeRun / nIterations    

                # get back to post-processing folder
                os.chdir(cwd)

                # update avgTime
                avgTime += avgTimeRun

            # add newline on outputs (to separate experiments)
            outputs.write("\n")

            # write "avgTime" and "fileSize" on "times"
            avgTime = avgTime / len(failures)
            fileSize = (os.path.getsize(logFile) / 1024) / 1024 # return bytes, converted to megabytes
            timePerMB = avgTime / fileSize # avgTime : fileSize = timePerMB : 1
            times.write(subfolder + "," + file + "," + str(avgTime) + "," + str(fileSize) + "," + str(timePerMB) + "\n")
            times.flush()

    outputs.close()
    times.close()

if __name__ == "__main__":
    # store number "n" of iterations
    # (used to determine average explanation times)
    if len(sys.argv) < 3:
        print("ERROR: please specify the number of failures to consider and how many iterations to repeat")
        exit(-1)
    nFailures = int(sys.argv[1])
    nIterations = int(sys.argv[2])

    # repeat post-processing for both version (with and without ids)
    print("* * Explaining WITH ids * *")
    postProcess("",nFailures,nIterations)
    # print("\n* * Explaining WITHOUT ids * *")
    # postProcess("-noid",nFailures,nIterations)