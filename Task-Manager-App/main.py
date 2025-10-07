todos = []


while True:
    user_action = input("Enter add, show,edit, complete or exit:")
    match user_action:
        case 'add':
            todo = input("Enter a todo:")
            todos.append(todo)
        case 'show':
            for i in range(0, len(todos)):
                print(f"{i+1}. {todos[i]}")
            print()
        case 'edit':
            number = int(input("Enter S.no of the todo to edit:"))
            number -= 1
            new_todo = input("Please enter a new todo:")
            todos[number] = new_todo
            print("Your list has been updated! ")
        case "exit":
            break
        case "complete":
            num = int(input("Which index is completed:"))
            # num -= 1
            # # todos.remove(todos[num])
            todos.pop(num-1)
            print("Your task is marked complete")
        case blah_blah:
            print("Please enter a valid command")


print("Bye bye")
