import os
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tkinter as tk
from tkinter import ttk

class FileHandler(FileSystemEventHandler):
    def __init__(self, name_var, desc_var, file_count_var, last_file_var, last_name_var, last_desc_var):
        self.name_var = name_var
        self.desc_var = desc_var
        self.file_count_var = file_count_var
        self.last_file_var = last_file_var
        self.last_name_var = last_name_var
        self.last_desc_var = last_desc_var
        self.modified_dir = "./Modified_Files"
        if not os.path.exists(self.modified_dir):
            os.makedirs(self.modified_dir)
        self.last_position = None

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".json"):
            return
        self.process_file(event.src_path)

    def process_file(self, file_path):
        if self.is_new_file(file_path):
            self.modify_json(file_path)
        else:
            print("Этот файл уже был обработан.")

    def is_new_file(self, file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
        current_position = tuple(data.get('position', ()))
        is_new = (current_position != self.last_position)
        if is_new:
            self.last_position = current_position
        return is_new

    def modify_json(self, file_path):
        new_name = self.name_var.get()
        new_desc = self.desc_var.get()
        with open(file_path, 'r') as f:
            data = json.load(f)
        data['name'] = new_name
        data['description'] = new_desc

        existing_files = [f for f in os.listdir(".") if f.endswith(".json") and f.replace(".json", "").isdigit()]
        if existing_files:
            max_num = max([int(f.replace(".json", "")) for f in existing_files])
            new_filename = f"{max_num + 1}.json"
        else:
            new_filename = "1.json"

        new_file_path = os.path.join(".", new_filename)
        with open(new_file_path, 'w') as f:
            json.dump(data, f, indent=4)
        os.remove(file_path)
        self.update_interface(new_filename, data)

    def update_interface(self, new_filename, data):
        existing_files = [f for f in os.listdir(".") if f.endswith(".json") and f.replace(".json", "").isdigit()]
        self.file_count_var.set(f"Файлов было создано: {len(existing_files)}")
        if existing_files:
            last_file = max(existing_files, key=lambda f: int(f.replace(".json", "")))
            self.last_file_var.set(f"Последний файл: {last_file}")
            with open(last_file, 'r') as f:
                last_data = json.load(f)
            self.last_name_var.set(f"Name: {last_data['name']}")
            self.last_desc_var.set(f"Description: {last_data['description']}")
        else:
            self.last_file_var.set(f"Последний файл: ")
            self.last_name_var.set(f"Name: ")
            self.last_desc_var.set(f"Description: ")

def bind_shortcuts(entry, shortcuts):
    entry.bind('<Control-a>', shortcuts['select_all'])
    entry.bind('<Control-x>', shortcuts['cut'])
    entry.bind('<Control-c>', shortcuts['copy'])
    entry.bind('<Control-v>', shortcuts['paste'])

def add_value(entry, dropdown):
    value = entry.get()
    if value and value not in dropdown['values']:
        dropdown['values'] = (*dropdown['values'], value)

def remove_value(dropdown):
    value = dropdown.get()
    values = list(dropdown['values'])
    if value in values:
        values.remove(value)
        dropdown['values'] = values

def create_gui():
    root = tk.Tk()
    root.title("JSON File Modifier")
    root.geometry("500x180")
    root.resizable(False, False)

    tk.Label(root, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
    tk.Label(root, text="Description:").grid(row=1, column=0, padx=5, pady=5, sticky='w')

    name_var = tk.StringVar()
    desc_var = tk.StringVar()
    topmost_var = tk.BooleanVar(value=False)

    file_count_var = tk.StringVar(value="Файлов было создано: 0")
    last_file_var = tk.StringVar(value="Последний файл: ")
    last_name_var = tk.StringVar(value="Name: ")
    last_desc_var = tk.StringVar(value="Description: ")

    tk.Button(root, text="X", command=lambda: name_var.set("")).grid(row=0, column=1, padx=5, pady=5, sticky='w')
    name_entry = tk.Entry(root, textvariable=name_var, width=25)
    name_entry.grid(row=0, column=2, padx=5, pady=5)

    tk.Button(root, text="X", command=lambda: desc_var.set("")).grid(row=1, column=1, padx=5, pady=5, sticky='w')
    desc_entry = tk.Entry(root, textvariable=desc_var, width=25)
    desc_entry.grid(row=1, column=2, padx=5, pady=5)

    name_dropdown = ttk.Combobox(root, values=["Создать новое значение"], state="readonly", width=25)
    name_dropdown.grid(row=0, column=3, padx=5, pady=5)

    desc_dropdown = ttk.Combobox(root, values=["Создать новое значение"], state="readonly", width=25)
    desc_dropdown.grid(row=1, column=3, padx=5, pady=5)

    tk.Button(root, text="O", command=lambda: add_value(name_entry, name_dropdown)).grid(row=0, column=4, padx=5, pady=5)
    tk.Button(root, text="O", command=lambda: add_value(desc_entry, desc_dropdown)).grid(row=1, column=4, padx=5, pady=5)
    tk.Button(root, text="X", command=lambda: remove_value(name_dropdown)).grid(row=0, column=5, padx=5, pady=5)
    tk.Button(root, text="X", command=lambda: remove_value(desc_dropdown)).grid(row=1, column=5, padx=5, pady=5)

    file_count_label = tk.Label(root, textvariable=file_count_var, anchor='w')
    file_count_label.grid(row=2, column=0, columnspan=6, padx=5, pady=5, sticky='w')

    last_file_label = tk.Label(root, textvariable=last_file_var, anchor='w')
    last_file_label.grid(row=3, column=0, columnspan=6, padx=5, pady=5, sticky='w')

    last_name_label = tk.Label(root, textvariable=last_name_var, anchor='w')
    last_name_label.grid(row=4, column=0, columnspan=6, padx=5, pady=5, sticky='w')

    last_desc_label = tk.Label(root, textvariable=last_desc_var, anchor='w')
    last_desc_label.grid(row=5, column=0, columnspan=6, padx=5, pady=5, sticky='w')

    shortcuts = {
        'select_all': lambda e: (name_entry.select_range(0, 'end') if root.focus_get() == name_entry else desc_entry.select_range(0, 'end')),
        'cut': lambda e: root.focus_get().event_generate('<<Cut>>'),
        'copy': lambda e: root.focus_get().event_generate('<<Copy>>'),
        'paste': lambda e: root.focus_get().event_generate('<<Paste>>')
    }

    bind_shortcuts(name_entry, shortcuts)
    bind_shortcuts(desc_entry, shortcuts)

    def toggle_topmost(event):
        is_topmost = topmost_var.get()
        root.attributes('-topmost', not is_topmost)
        topmost_var.set(not is_topmost)

    root.bind('<Control-Shift_L>', toggle_topmost)

    event_handler = FileHandler(name_var, desc_var, file_count_var, last_file_var, last_name_var, last_desc_var)
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=False)
    observer.start()

    try:
        root.mainloop()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    create_gui()
