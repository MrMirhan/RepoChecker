import os, re, json, string
pythonFiles = [os.getcwd()+"/" + x for x in os.listdir(os.getcwd()) if x.endswith(".py") and x != __file__.replace(os.getcwd()+"/", "")]
directories = [x[0] for x in os.walk(os.getcwd())]
del directories[0]
for directory in directories:
    pythonFiles = pythonFiles + [directory+"/" + x for x in os.listdir(directory) if x.endswith(".py")]
pythonFiles = list(set(pythonFiles))
modules = []
for file in pythonFiles:
    fileLines = open(file, "r").readlines()
    for line in fileLines:
        if line.startswith("#"): continue
        if line.find("import") >= 0:
            if line.find(",") >= 0:
                for modull in line.replace("import ", "").split(","):
                    if modull.find("as") >= 0: modull = modull.split("as")[0]
                    modull = modull.replace("\n", "")
                    puncs = 0
                    for char in modull:
                        if char in string.punctuation:
                            puncs += 1
                    if puncs > 0: continue
                    if modull != "*":
                        modules.append(modull)
            else:
                module = line.split("import")[-1].replace("\n", "")
                if module.find("as") >= 0: module = module.split("as")[1]
                puncs = 0
                for char in module:
                    if char in string.punctuation:
                        puncs += 1
                if puncs > 0: continue
                if module != "*":
                    modules.append(module)
                    
moduleList = {}
for module in modules:
    module = module.replace(" ", "")
    moduleList[module]= []

for file in pythonFiles:
    fileLines = open(file, "r").readlines()
    for line in fileLines:
        if line.startswith("#"): continue
        for module in modules:
            if line.find(module + ".") >= 0 and line.find("import") < 0:
                functionList = re.findall(r"\.(.*?)\(", line)
                subFunctions = re.findall(r"\.(.*?)\.", line)
                for function in functionList:
                    if function.find(".") >= 0:
                        function = function.replace(".", " -> ")
                    if function.find("=") >= 0: continue
                    puncs = 0
                    for char in function:
                        if char in string.punctuation:
                            puncs += 1
                    if puncs > 0: continue
                    moduleList[module.replace(" ", "")].append(function)

for module in modules:
    module = module.replace(" ", "")
    moli = set(moduleList[module])
    moduleList[module] = list(moli)
    moduleList[module] = [x for x in moduleList[module] if x != ""]

for module in modules:
    module = module.replace(" ", "")
    agac = open("agacsemasi.txt", "r").read()
    open("agacsemasi.txt", "w").write(agac + module + "\n")
    if len(moduleList[module]) > 0:
        for function in moduleList[module]:
            agac = open("agacsemasi.txt", "r").read()
            open("agacsemasi.txt", "w").write(agac + "\t" + function + "\n")