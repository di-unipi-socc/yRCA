import os
import sys
import time

def postProcess(id,n):
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
            print("Processing " + file)

            # variable for computing avg time 
            avgTime = 0
           
            # get absolute of log file 
            logFile = os.path.join(logSubfolder,file)
            
            # get frontend "failures" in considered "logFile"
            grepFailures = "grep ERROR " + logFile + " | grep _edgeRouter | grep -v own"
            allFailures = os.popen(grepFailures)
            failures = list(allFailures) #[-100:] # considering the last 100 failures
            
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

                # process failure file with "explain.py"
                explanations = os.path.join(cwd,"explanations")
                os.chdir("../../../..")
                runExplainer = "python3 explain.py " + failureFile + " " + logFile + " " + templates
                startTime = time.time()
                os.system(runExplainer + " > " + explanations)
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

                # repeat run for a total of 10 times to measure avgTime of the run
                avgTimeRun = endTime - startTime
                for _ in range(n-1):
                    startTime = time.time()
                    os.system(runExplainer + " > /dev/null")
                    endTime = time.time()
                    avgTimeRun += (endTime - startTime) 
                avgTimeRun = avgTimeRun / n    

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
    if len(sys.argv) < 2:
        print("ERROR: please specify the number of iterations")
        exit(-1)
    n = int(sys.argv[1])

    # repeat post-processing for both version (with and without ids)
    ids = ["","-noid"]
    for id in ids:
        postProcess(id,n)