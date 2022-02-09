import config
import requests, os, re, string, shutil
from github import Github
import zipfile

g = Github(config.GITHUB_TOKEN)

turnOff = False

def splitList(_list):
    newList = []
    currentList = []
    x = 0
    for el in _list:
        if len(currentList) == 10 or x == len(_list):
            newList.append(currentList)
            currentList.clear()
        else:
            currentList.append(el)
        x+=1

def search_github(keywords):
    query = '+'.join(keywords) + '+in:readme+in:description'
    result = g.search_repositories(query, 'stars', 'desc')
    print(f'Found {result.totalCount} repo(s)')
    x = 0
    y = 0
    for repo in result:
        print(str(x) + ".", repo.clone_url, repo.stargazers_count, "stars")
        x += 1
    choice = ""
    while choice != "exit":
        text = """
\tType `page (number)` for go repository page.
\tType `exit` for leave to main menu.
\tType `all` for install all repositories from printed.
\tType id for install specific repository (eg. 1).
"""
        print(text)
        choice = input("Your choice: ")
        try:
            choice = int(choice)
            print(choice, "it is")
        except:
            if choice == "all":
                print("all it is")

def download_folder(url):
    r = requests.get(url, stream = True)
    zippedPath = os.getcwd() + "/projects/zipped/"
    unzippedPath = os.getcwd() + "/projects/unzipped/"
    with open(zippedPath + url.split("/")[4]+".zip", "wb") as repo:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                repo.write(chunk)
    with zipfile.ZipFile(zippedPath + url.split("/")[4]+".zip", 'r') as zip_ref:
        zip_ref.extractall(unzippedPath)
    print("Repository installed successfully.")

def checkModules(pythonFiles, path):
    modules = []
    for file in pythonFiles:
        fileLines = open(file, "r").readlines()
        for line in fileLines:
            if line.startswith("#"): continue
            if line.find("import") >= 0:
                if line.find("from") >= 0:
                    from_ = line.split("import")[0]
                    from_ = from_.replace("from ", "")
                    if from_.find(".") >= 0: from_ = from_.split(".")[0].replace(" ", "")
                    module = from_
                    alias = None
                    prefunctions = []
                    dotspl = str(str(line.split(" import ")[0]).split("from ")).split(".")
                    del dotspl[0]
                    if line.find(" as ") >= 0:
                        alias = line.split(" as ")[1]
                    else:
                        line = line.replace("from ", "")
                        if line.split("import")[1].find(",")>=0:
                            alias = []
                            for submod in line.split("import")[1].split(","):
                                alias.append(submod)
                        else:
                            alias = str(line.split("import")[1].replace(" ", "")).replace("\n", "")
                    for dot in dotspl:
                        if dot.find(" as ") >= 0:
                            dot = dot.split(" as ")[0]
                        prefunctions.append(str(dot.replace(" ", "")).replace("\n", ""))
                    if module != "*" and not module.lower() in [exclude.lower() for exclude in open(path + "/excludeList.txt", 'r').readlines()]:
                        if module in [x['module'] for x in modules]:
                            samem = [x for x in modules if x['module'] == module][0]
                            if type(samem['alias']) != list:
                                salias = samem['alias']
                                samem['alias'] = list()
                                samem['alias'].append(salias)
                                samem['alias'].append(alias)
                            else:
                                if type(alias) == list:
                                    for alias in alias:
                                        samem['alias'].append(alias)
                                else:
                                    samem['alias'].append(alias)
                            samem['prefunctions'].extend(prefunctions)
                            modules = [x for x in modules if not x['module'] == module] + [samem]
                        else:
                            arr = {"module": module, "alias": alias, "prefunctions": prefunctions}
                            modules.append(arr)
                elif line.find(",") >= 0:
                    for module in str(line.split("import")[1]).split(","):
                        module = module.replace("\n", "")
                        alias = None
                        if module.find(" as ") >= 0:
                            moas = module.split(" as ")
                            module = moas[0]
                            alias = moas[1]
                        puncs = 0
                        for char in module:
                            if char in string.punctuation:
                                puncs += 1
                        if puncs > 0: continue
                        if module != "*" and not module.lower() in [exclude.lower() for exclude in open(path + "/excludeList.txt", 'r').readlines()]:
                            arr = {"module": module, "alias": alias, "prefunctions": None}
                            modules.append(arr)
                elif line.find(".") >= 0:
                    module = str(line.split("import")[1]).split(".")[0]
                    alias = None
                    prefunctions = []
                    dotspl = str(line.split("import")[1]).split(".")
                    del dotspl[0]
                    if line.find(" as ") >= 0:
                        moas = line.split(" as ")
                        module = str(line.split("import")[1]).split(".")[0].replace(" ", "")
                        alias = moas[1].replace("\n", "")
                    for dot in dotspl:
                        if dot.find(" as ") >= 0:
                            dot = dot.split(" as ")[0]
                        prefunctions.append(str(dot.replace(" ", "")).replace("\n", ""))
                    puncs = 0
                    for char in module:
                        if char in string.punctuation:
                            puncs += 1
                    if puncs > 0: continue
                    if module != "*" and not module.lower() in [exclude.lower() for exclude in open(path + "/excludeList.txt", 'r').readlines()]:
                        arr = {"module": module, "alias": alias, "prefunctions": prefunctions}
                        modules.append(arr)
                else:
                    module = line.split("import")[-1].replace("\n", "")
                    alias = None
                    if module.find(" as ") >= 0:
                        moas = module.split(" as ")
                        module = moas[0].replace(" ", "")
                        alias = moas[1].replace("\n", "")
                    puncs = 0
                    for char in module:
                        if char in string.punctuation:
                            puncs += 1
                    if puncs > 0: continue
                    if module != "*" and not module.lower() in [exclude.lower().replace("\n", "") for exclude in open(path + "/excludeList.txt", 'r').readlines()]:
                        arr = {"module": module, "alias": alias, "prefunctions": None}
                        modules.append(arr)
    return modules

def makeModuleList(modules):
    moduleList = {}
    for module in modules:
        orgmodule = module
        module = module['module'].replace(" ", "")
        moduleList[module] = []
        if type(orgmodule['prefunctions']) == list:
            if len(orgmodule['prefunctions']) > 0:
                for prefunc in orgmodule['prefunctions']:
                    for character in string.punctuation:
                        if character == "_": continue
                        prefunc = prefunc.replace(character, '')
                    moduleList[module].append(prefunc)
    return moduleList

def checkFunctions(modules, pythonFiles, moduleList):
    for file in pythonFiles:
        fileLines = open(file, "r").readlines()
        for line in fileLines:
            if line.startswith("#"): continue
            for module in modules:
                orgmodule = module['module']
                try:
                    if module['alias']:
                        module = module['alias']
                    else:
                        module = module['module']
                except:
                    module = module['module']
                if type(module) == list:
                    for module in module:
                        if line.find(module + ".") >= 0 and line.find("import") < 0 and line.find("from") < 0:
                            functionList = re.findall(module + r"\.(.*?)\(", line)
                            for function in functionList:
                                if function.find(".") >= 0:
                                    function = function.replace(".", " -> ")
                                if function.find("=") >= 0: function = function.split("=")[1]
                                puncs = 0
                                for char in function:
                                    if char != "_" and char in string.punctuation:
                                        puncs += 1
                                if puncs > 0:
                                    continue
                                else:
                                    moduleList[orgmodule.replace(" ", "")].append(function)
                        elif line.find(orgmodule + ".") >= 0 and line.find("import") >= 0 and line.split("import ")[1].find(".") >= 0 and line.find("from") < 0:
                            funt = line.split("import ")[1]
                            f = funt.split(".")
                            f[1] = f[1].replace("\n", "")
                            f[0] = f[0].replace(" ", "")
                            function = ""
                            if len(f) > 2:
                                x = 1
                                for frrom in f:
                                    if x == len(f):
                                        function += " " + frrom
                                    elif x == 1:
                                        function += frrom + "->"
                                    else:
                                        function += " " + frrom + "->"
                                    x+=1
                            else:
                                function = f[1]
                            if function.find("as") >= 0: function = function.split(" as ")[0]
                            puncs = 0
                            for char in function:
                                if char != "_" and char in string.punctuation:
                                    puncs += 1
                                if puncs > 0:
                                    continue
                            moduleList[orgmodule.replace(" ", "")].append(function)   
                else:
                    if line.find(module + ".") >= 0 and line.find("import") < 0 and line.find("from") < 0:
                        functionList = re.findall(module + r"\.(.*?)\(", line)
                        for function in functionList:
                            if function.find(".") >= 0:
                                function = function.replace(".", " -> ")
                            if function.find("=") >= 0: function = function.split("=")[1]
                            puncs = 0
                            for char in function:
                                if char != "_" and char in string.punctuation:
                                    puncs += 1
                            if puncs > 0:
                                continue
                            else:
                                moduleList[orgmodule.replace(" ", "")].append(function)
                    elif line.find(orgmodule + ".") >= 0 and line.find("import") >= 0 and line.split("import ")[1].find(".") >= 0 and line.find("from") < 0:
                            funt = line.split("import ")[1]
                            f = funt.split(".")
                            f[1] = f[1].replace("\n", "")
                            f[0] = f[0].replace(" ", "")
                            function = ""
                            if len(f) > 2:
                                x = 1
                                for frrom in f:
                                    if x == len(f):
                                        function += " " + frrom
                                    elif x == 1:
                                        function += frrom + "->"
                                    else:
                                        function += " " + frrom + "->"
                                    x+=1
                            else:
                                function = f[1]
                            if function.find("as") >= 0: function = function.split(" as ")[0]
                            puncs = 0
                            for char in function:
                                if char != "_" and char in string.punctuation:
                                    puncs += 1
                                if puncs > 0:
                                    continue
                            moduleList[orgmodule.replace(" ", "")].append(function)
    return moduleList

def formatModuleList(modules, moduleList):
    for module in modules:
        module = module['module']
        module = module.replace(" ", "")
        moduleList[module] = list(set(moduleList[module]))
        moduleList[module] = [x for x in moduleList[module] if x != ""]
    return moduleList

def createTree(modules, moduleList, original_path, path):
    treePath = original_path + "/trees/" + path.split("/")[-1] + "/"
    try:
        open(treePath + "tree.txt", "w")
    except:
        os.mkdir(treePath)    
        open(treePath + "tree.txt", "w")
    for module in moduleList:
        module = module.replace(" ", "")
        agac = open(treePath + "tree.txt", "r").read()
        open(treePath + "tree.txt", "w").write(agac + module + "\n")
        if len(moduleList[module]) > 0:
            for function in moduleList[module]:
                agac = open(treePath + "tree.txt", "r").read()
                open(treePath + "tree.txt", "w").write(agac + "\t" + function + "\n")
    return True

def repoCheck(path):
    original_path = os.getcwd()
    os.chdir(path)

    pythonFiles = [os.getcwd()+"/" + x for x in os.listdir(os.getcwd()) if x.endswith(".py")]
    directories = [x[0] for x in os.walk(os.getcwd())]
    del directories[0]

    for directory in directories:
        pythonFiles = pythonFiles + [directory+"/" + x for x in os.listdir(directory) if x.endswith(".py")]
    pythonFiles = list(set(pythonFiles))

    modules = checkModules(pythonFiles, original_path)
    moduleList = makeModuleList(modules)
    moduleList = checkFunctions(modules, pythonFiles, moduleList)
    moduleList = formatModuleList(modules, moduleList)
    tree = createTree(modules, moduleList, original_path, path)
    os.chdir(original_path)
    return tree

def checkRepos():
    repoPath = os.getcwd() + "/projects/unzipped/"
    repos = [x for x in os.listdir(repoPath) if os.path.isdir(repoPath + x) == True]
    if len(repos) == 0:
        print("No repositories found.")
    else:
        selected = ""
        while selected != "exit":
            x = 0
            for repo in repos:
                print(str(x) + ".", repo)
                x+=1
            text = """
\tType `exit` for return main menu.
\tType `all` for check all repositories and create tree scheme.
\tType id of repository to check specific repository.            
"""
            print(text)
            selected = input("Your choice: ")
            if selected == "all":
                for repo in repos:
                    try:
                        check = repoCheck(repoPath + repo)
                        print("Tree creation for " + repo + "successfully finished." if check == True else "Tree couldn't created successfully for " + repo)
                    except Exception as e:
                        print("Tree couldn't created successfully for", repo)
                        print("Error:", e)
            elif selected == "exit":
                break
            else:
                try:
                    selected = int(selected)
                    try:
                        check = repoCheck(repoPath + repos[selected])
                        print("Tree creation for " + repos[selected] + "successfully finished." if check == True else "Tree couldn't created successfully for " + repos[selected])
                    except Exception as e:
                        print("Tree couldn't created successfully for", repos[selected])
                        print("Error:", e)
                except Exception as e:
                    print("Please select choice in menu!")

def eraseData():
    folders = [os.getcwd() + "/trees", os.getcwd() + "/projects/unzipped", os.getcwd() + "/projects/zipped"]
    for folder in folders:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    if not file_path.endswith("__init__.py") == True:
                        os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                print("Successfully cleared path: %s" % file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
    print("Done erasing.")

def checkChoice(choice):
    global turnOff
    if choice == 0:
        turnOff = True
    elif choice == 1:
        print("Under maintenance!")
        #keywords = input('Enter keyword(s)[e.g python, flask, postgres]: ')
        #search_github([keyword.strip() for keyword in keywords.split(',')])
    elif choice == 2:
        url = input('Enter folder url: ')
        download_folder(url)
    elif choice == 3:
        checkRepos()
    elif choice == 4:
        eraseData()
    
welcomeText = f"""
\tWelcome to RepoChecker v{config.VERSION}
\n
\t0. Exit
\t1. Search with keywords. (Maintenance)
\t2. Download public repository.
\t3. Check downloaded repositories.
\t4. Erase all data.
"""
while turnOff == False:
    print(welcomeText)
    try:
        choice = int(input("Select from menu (eg. 1): "))
    except:
        print("Chocie must be integer!")
        continue
    checkChoice(choice)
