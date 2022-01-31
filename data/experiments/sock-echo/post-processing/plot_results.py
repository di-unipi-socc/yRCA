import math
import matplotlib.pyplot as plt
import os
import re

plotsDir = "plots"

def parseOutputs(outputsFile):
    out = { }
    out["count"] = {}
    out["roots"] = {}
    out["accuracy"] = {}
    outputs = open(outputsFile)

    experiment = None
    value = None
    count = None
    nFailures = None
    noExps = None
    roots = None
    for outputLine in list(outputs):
        if "logs_exp" in outputLine: # case: new experiment
            #addOutput(out,experiment,value,nFailures,count,noExps,roots)
            experiment = adaptLabel(outputLine[:-1])
            out["count"][experiment] = []
            out["roots"][experiment] = []
            out["accuracy"][experiment] = []
            value = None
            count = None
            roots = None
        elif outputLine[0] == ">": # case: new experiment's value
            #addOutput(out,experiment,value,nFailures,count,noExps,roots)
            logFileInfo = re.match(r'> all-(?P<value>.*).log \((?P<n>.*) failures\)',outputLine)
            value = adaptValue(logFileInfo.group("value"))
            nFailures = int(logFileInfo.group("n"))
            count = 0
            noExps = 0
            roots = 0
            rootVals = {}
        elif outputLine[0] == "[": # case: new solution
            count += 1
        elif "no failure cascade" in outputLine: # case: no solution found
            noExps += 1 
        elif ": unreachable" in outputLine or ": <internal error>" in outputLine: # case: root cause
            rootVal = outputLine.split(":")[0].replace(" ","")[2:]
            if not rootVal in rootVals: # added only if not already considered as a root cause for current failure
                rootVals[rootVal] = True
                roots +=1
        elif outputLine[0] == "{": # case: new failure for an experiment's value
            rootVals = {}
        elif outputLine == "\n":
            addOutput(out,experiment,value,nFailures,count,noExps,roots)
    outputs.close()

    # sort experiments' lists by experiment value
    for experiment in out["count"]:
        out["count"][experiment].sort(key=lambda pair:pair[0])
    for experiment in out["count"]:
        out["roots"][experiment].sort(key=lambda pair:pair[0])
    for experiment in out["accuracy"]:
        out["accuracy"][experiment].sort(key=lambda pair:pair[0])

    return out

# function to add an output, if experiment and value are both defined
def addOutput(outputs,experiment,value,nFailures,count,noExps,roots):
    if experiment and value and count:
        nExplainedFailures = nFailures - noExps
        outputs["count"][experiment].append([value,count/nExplainedFailures])
        outputs["roots"][experiment].append([value,roots/nExplainedFailures])
        accuracy = nExplainedFailures * 100 / nFailures
        outputs["accuracy"][experiment].append([value,accuracy])

# function to parse a csv timeFile
# with lines s.t. "experiment,logFile,elapsedTime,fileSize,timePerMB"
def parseTimes(timesFile):
    times = {}

    # process each csv line separately
    csvTimes = open(timesFile)
    for csvTime in list(csvTimes):
        splittedTime = csvTime.split(",")
        # add "experiment" to "times", if not there already
        experiment = adaptLabel(splittedTime[0])
        if experiment not in times:
            times[experiment] = []
        # add pair [n,timePerMB], where n is the value used in the experiment run 
        # (n excerpted from logFile name)    
        logFile = splittedTime[1]
        logFileInfo = re.match(r'all-(?P<value>.*).log',logFile)
        value = adaptValue(logFileInfo.group("value"))
        millisPerMB = float(splittedTime[4][:-1]) * 1000
        times[experiment].append([value,millisPerMB])
    
    # sort experiments' lists by experiment value
    for experiment in times:
        times[experiment].sort(key=lambda pair:pair[0])

    return times

def adaptLabel(experimentLabel):
    # excerpt label from experiment name
    label = experimentLabel.split("_")[2]
    label = re.sub("([A-Z])"," \g<0>",label).lower()
    # add unit (if needed) based on type of experiment
    if "rate" in label:
        label += " (req/s)"
    elif "probability" in label:
        label += " (%)"
    
    return label

# function to adapt a given "experimentValue" 
# - if load rate (of the form "0.x"), translated to rate of requests/s
# - if probability (of the form "x%"), unchanged
# - if name of root causing service, translated to length of corresponding cascade
def adaptValue(experimentValue):
    try: # case: numeric value
        num = float(experimentValue)
        if num < 1: # case: load rate
            return int(1/num)
        else: # case: percentage
            return num
    except: # case: name of root causing service
        if experimentValue == "frontend":
            return 1
        elif experimentValue == "orders":
            return 2
        elif experimentValue == "shipping":
            return 3
        elif experimentValue == "rabbitMq":
            return 4
    
    # unknown cases
    return None

# function to plot "experiment" list
def plot(pdfName,experiment,xLabel,yLabel,yTop):
    # excerpt x/y coordinates from list of pairs
    x = [p[0] for p in experiment]
    y = [p[1] for p in experiment]
    
    # configure plot 
    axes = plt.gca()
    axes.set_xticks(x)
    axes.set_ylim([0, yTop])
    plt.plot(x,y,"--bo") 
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)

    # label area
    plt.subplots_adjust(bottom=0.18)
    plt.subplots_adjust(left=0.18)

    # store plot on PDF
    pdfName = plotsDir + "/" + xLabel.split(" ")[0] + "_" + pdfName + ".pdf"
    plt.savefig(pdfName)
    plt.clf()

# function to print experiment results
def printResults(heading,results):
    print()
    print("* "*3 + heading.upper() + " *"*3)
    for experiment in results:
        print(experiment)
        for pair in results[experiment]:
            print(" " + str(pair[0]) + "\t" + str(pair[1]))

if __name__ == "__main__":
    print("Generating plots...",end="",flush=True)

    # create folder where to store plots (if not existing)
    if not os.path.exists(plotsDir):
        os.makedirs(plotsDir)

    # confige plt's defaults
    plt.rcParams.update({'font.size': 20}) 

    # ----------------
    # plot outputs
    # ----------------
    outputs = parseOutputs("outputs.txt")
    for o in outputs["count"]:
        plot("count",outputs["count"][o],o,"number",4)
        plot("success_percentage",outputs["accuracy"][o],o,"explained failures (%)",100) # change label into "successfully explained failures"?
    

    # ----------------
    # plot times
    # ----------------
    times = parseTimes("times.csv")
    for t in times:
        plot("time",times[t],t,"time (ms/MB)",275)

    print("done!")

    printResults("count",outputs["count"])
    printResults("success_percentage",outputs["accuracy"])
    printResults("times",times)

    print()
    print(outputs["count"])
    
    print()
    print(outputs["roots"])
    