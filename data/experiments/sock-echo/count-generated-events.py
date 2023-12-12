import os

ls = os.listdir("generated-logs")

print("experiment,log_file,events,errors")
for folder in ls:
    if "logs" in folder:
        files = os.listdir("generated-logs/" + folder)
        for fileName in files:
            path = "generated-logs/" + folder + "/" + fileName
            f = open(path)
            lines = 0
            errors = 0
            for line in f:
                lines += 1
                if "ERROR" in line:
                    errors += 1
            print(folder + "," + fileName + "," + str(lines) + "," + str(errors))
   
