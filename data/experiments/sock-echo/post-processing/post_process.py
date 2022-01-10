import os
import time

if __name__ == "__main__":
    # output files
    outputsFile = "outputs.txt"
    outputs = open(outputsFile,"w")
    timesFile = "times.txt"
    times = open(timesFile,"w")

    # get absolute path of explainer
    explainer = os.path.abspath("../../../../explain.py")

    # get absolute path of folder with logs
    logFolder = os.path.abspath("../generated-logs")

    # get absolute path of templater
    templates = os.path.abspath("../../../templates/chaos-echo.yml")
    # templates = os.path.abspath("../../../templates/chaos-echo-noid.yml")

    # process log subfolders, separately
    subfolders = os.listdir(logFolder)
    for subfolder in subfolders:
        # get logfiles in subfolder
        logSubfolder = os.path.join(logFolder,subfolder)
        logFiles = os.listdir(logSubfolder)

        # write subfolder name in outputs
        outputs.write("*"*3 + subfolder + "*"*3 + "\n")
        times.write("*"*3 + subfolder + "*"*3 + "\n")

        # process each log file, separately
        for file in logFiles:
            print("Processing " + file)
            
            # get absolute of log file 
            logFile = os.path.join(logSubfolder,file)
            
            # get frontend "failures" in considered "logFile"
            grepFailures = "grep ERROR " + logFile + " | grep _edgeRouter | grep -v own"
            allFailures = os.popen(grepFailures)
            failures = list(allFailures) #[-100:] # considering the last 100 failures
            
            # write headings in output files
            heading = file + "(" + str(len(failures)) + " failures)\n"
            outputs.write(heading)
            times.write(heading)

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
                runExplainer = "python3 explain.py " + failureFile + " " + logFile + " " + templates + " > " + explanations
                startTime = time.time()
                os.system(runExplainer)
                endTime = time.time()
                os.chdir(cwd)

                # write computed "outputs"
                expLines = open(explanations, "r")
                exps = list(expLines)[:-1] # consider all lines (but the last one)
                if len(exps) == 0:
                    outputs.write("XXX\n")
                else: 
                    for exp in exps: 
                        if exp != "  \n": # exclude newlines
                            outputs.write(exp)

                # write elapsed time on timeFile
                times.write(str(endTime - startTime) + "\n")
            
                # flush output files' buffers
                outputs.flush()
                times.flush()

            # add newline on output files (to separate experiments)
            outputs.write("\n")
            times.write("\n")
    outputs.close()
    times.close()