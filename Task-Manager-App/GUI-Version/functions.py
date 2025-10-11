FILE_PATH = r"C:\Users\sambh\OneDrive\Desktop\Python code\20-Python-Projects\Task-Manager-App\GUI-Version\todos.txt" #file apth


def readFile():
    with open(FILE_PATH, 'r') as file:#reading the previous saved data from file
        todos = file.readlines()#adding those data in todos list
    return todos


def writeFile(todos):
    with open(FILE_PATH, 'w') as file:#Start overwritting that file
        file.writelines(todos)#Rewrite the whole file with new input in it
    