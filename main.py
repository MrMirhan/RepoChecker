import config
from github import Github

g = Github(config.GITHUB_TOKEN)

turnOff = False

def search_github(keywords):
    query = '+'.join(keywords) + '+in:readme+in:description'
    result = g.search_repositories(query, 'stars', 'desc')
    print(f'Found {result.totalCount} repo(s)')
    
    

    x = 0
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

def checkChoice(choice):
    global turnOff
    if choice == 0:
        turnOff = True
    elif choice == 1:
        keywords = input('Enter keyword(s)[e.g python, flask, postgres]: ')
        search_github([keyword.strip() for keyword in keywords.split(',')])

welcomeText = f"""
\tWelcome to RepoChecker v{config.VERSION}
\n
\t0. Exit
\t1. Search with keywords.
\t2. Download public repository.
\t3. Check downloaded repositories.
"""
while turnOff == False:
    print(welcomeText)
    try:
        choice = int(input("Select from menu (eg. 1): "))
    except:
        print("Chocie must be integer!")
        continue
    checkChoice(choice)
