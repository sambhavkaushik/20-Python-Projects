import FreeSimpleGUI as fsg
import functions 

label = fsg.Text("Type in a To-Do")
input_box = fsg.InputText(tooltip="Enter To-Do", key="todo")
add_button = fsg.Button("Add")
exit_button = fsg.Button("Exit")
list_box = fsg.Listbox(values=functions.readFile(), key='todos', 
                       enable_events=True, size=[45, 10])
edit_button = fsg.Button("Edit")
  
window = fsg.Window("My To Do App", 
                    layout=[[label, input_box, add_button], 
                            [exit_button], 
                            [list_box, edit_button]],
                    font=('Helvetica', 20))
while True:
    event, values = window.read()

    if event == "Add":
        todos = functions.readFile()
        new_todo = values['todo'] + '\n'
        todos.append(new_todo)
        functions.writeFile(todos)
        window["todos"].update(values=todos)

    if event == "Edit":
        todo_to_edit = values['todos'][0]
        new_todo = values['todo']
        todos = functions.readFile()
        index = todos.index(todo_to_edit)
        todos[index] = new_todo
        functions.writeFile(todos)
        window['todos'].update(values=todos)
    
    if event == 'todos':
        window['todo'].update(value=values['todos'][0])


    if event == "Exit":
        break

    if fsg.WIN_CLOSED:
        break
print("Helloo world")
window.close()