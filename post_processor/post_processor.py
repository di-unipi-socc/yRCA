def post_process(rootCauses,applicationLogs):
    print("TODO: post-processing (based on " + applicationLogs + ")\n")
    print("N SOLS: ", len(rootCauses))
    for rc in rootCauses:
        # each rc is a list itself
        for c in rc["C"]:
            print(c, end="->")
        print("END") 
        #print(rc["C"])
