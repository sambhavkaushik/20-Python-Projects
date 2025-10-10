from functions import readFile, writeFile
import time

samay = time.strftime("%d %b, %Y; %H:%M")
print(samay)

while True:
    user_action = input("Enter add, show,edit, complete or exit:")

    if user_action.startswith("add"):
        todo = user_action[4:]
        todos = readFile()
        todos.append(todo + '\n') #New input got appended in the list 
        writeFile(todos)    
        print("Your task has been added succesfully!")

        '''
        Our current workflow is like this:
        The file saved before is opened, its data is read and saved in a list
        After which the new input is appended in that new list. 
        Which is list is later written in the file. So the file has the new appended data of the list as well  
        '''

    elif user_action.startswith("show"):
        todos = readFile()
        for index, todo in enumerate(todos):
            print(f"{index+1}-{todo}", end="")
        print()

    elif user_action.startswith("edit"):
        try:   
            number = int(user_action[5:]) #slicing
            number -= 1
            todos = readFile()
            new_todo = input("Please enter a new todo:")
            todos[number] = new_todo + '\n'
            writeFile(todos)
            print("Your list has been updated! ") 
        
        except:
            print("Your command is not valid")
            continue

    elif user_action.startswith("complete"):
        try:
            num = int(user_action[9:]) #slicing
            todos = readFile()
            todos.pop(num-1)
            writeFile(todos)
            print("Your task is completed! Remaining are:")
            for index, todo in enumerate(todos):
                print(f"{index+1}-{todo}", end="")
            print()

        except IndexError:
            print("Please enter correct index number")
            continue
        except:
            print("Your command is not valid")
            continue

    elif user_action.startswith("exit"):
        break

    else:
        print("Please enter a valid command")

print("Bye bye")