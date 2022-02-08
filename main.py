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

def checkModules(pythonFiles):
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
    return modules

def makeModuleList(modules):
    moduleList = {}
    for module in modules:
        module = module.replace(" ", "")
        moduleList[module]= []
    return moduleList

def checkFunctions(modules, pythonFiles, moduleList):
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
    return moduleList

def formatModuleList(modules, moduleList):
    for module in modules:
        module = module.replace(" ", "")
        moli = set(moduleList[module])
        moduleList[module] = list(moli)
        moduleList[module] = [x for x in moduleList[module] if x != ""]
    return moduleList

def createTree(modules, moduleList, original_path, path):
    treePath = original_path + "/trees/" + path.split("/")[-1] + "/"
    try:
        open(treePath + "tree.txt", "w")
    except:
        os.mkdir(treePath)    
        open(treePath + "tree.txt", "w")
    for module in modules:
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

    modules = checkModules(pythonFiles)
    moduleList = makeModuleList(modules)
    moduleList = checkFunctions(modules, pythonFiles, moduleList)
    moduleList = formatModuleList(modules, moduleList)
    tree = createTree(modules, moduleList, original_path, path)
    os.chdir(original_path)
    return tree

def checkRepos():
    repoPath = os.getcwd() + "/projects/unzipped/"
    repos = os.listdir(repoPath)
    x = 0
    for repo in repos:
        print(str(x) + ".", repo)
    selected = ""
    while selected != "exit":
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
                print(e)
                print("Please select choice in menu!")

def eraseData():
    folders = [os.getcwd() + "/trees", os.getcwd() + "/projects/unzipped", os.getcwd() + "/projects/zipped"]
    for folder in folders:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
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
