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
        self.modified_dir = None
        self.processed_files = {}

    def set_directory(self, directory):
        self.modified_dir = directory
        if not os.path.exists(self.modified_dir):
            os.makedirs(self.modified_dir)
        self.update_existing_files()
        self.update_interface()

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".json"):
            return
        self.process_file(event.src_path)

    def on_deleted(self, event):
        if event.is_directory or not event.src_path.endswith(".json"):
            return
        self.update_existing_files()
        self.update_interface()

    def process_file(self, file_path):
        if file_path in self.processed_files:
            return
        self.processed_files[file_path] = None
        if self.is_new_file(file_path):
            self.modify_json(file_path)
        else:
            print("Этот файл уже был обработан.")

    def is_new_file(self, file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            current_position = tuple(data.get('position', ()))
            return file_path not in self.processed_files or self.processed_files[file_path] != current_position
        except (IOError, json.JSONDecodeError):
            return False

    def modify_json(self, file_path):
        base_name = os.path.basename(file_path)
        if base_name.replace(".json", "").isdigit():
            print(f"Пропущен файл с номером: {base_name}")
            return
        
        new_name = self.name_var.get()
        new_desc = self.desc_var.get()
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            data['name'] = new_name
            data['description'] = new_desc

            existing_files = [f for f in os.listdir(self.modified_dir) if f.endswith(".json") and f.replace(".json", "").isdigit()]
            if existing_files:
                max_num = max([int(f.replace(".json", "")) for f in existing_files])
                new_filename = f"{max_num + 1}.json"
            else:
                new_filename = "1.json"
            new_file_path = os.path.join(self.modified_dir, new_filename)

            with open(new_file_path, 'w') as f:
                json.dump(data, f, indent=4)
            os.remove(file_path)
            
            self.update_existing_files()
            self.update_interface()
        except (IOError, json.JSONDecodeError) as e:
            print(f"Ошибка обработки файла {file_path}: {e}")

    def update_existing_files(self):
        if self.modified_dir is None:
            return
        self.processed_files = {}
        existing_files = [f for f in os.listdir(self.modified_dir) if f.endswith(".json") and f.replace(".json", "").isdigit()]
        for f in existing_files:
            self.processed_files[os.path.join(self.modified_dir, f)] = None

    def update_interface(self):
        if self.modified_dir is None:
            return
        existing_files = [f for f in os.listdir(self.modified_dir) if f.endswith(".json") and f.replace(".json", "").isdigit()]
        file_count = len(existing_files)
        self.file_count_var.set(f"Файлов было создано: {file_count}")
        if existing_files:
            last_file = max(existing_files, key=lambda f: int(f.replace(".json", "")))
            self.last_file_var.set(f"Последний файл: {last_file}")
            with open(os.path.join(self.modified_dir, last_file), 'r') as f:
                last_data = json.load(f)
            self.last_name_var.set(f"Name: {last_data.get('name', 'Не задано')}")
            self.last_desc_var.set(f"Description: {last_data.get('description', 'Не задано')}")
        else:
            self.last_file_var.set(f"Последний файл: ")
            self.last_name_var.set(f"Name: ")
            self.last_desc_var.set(f"Description: ")

def set_working_directory(path_entry, path_dropdown, event_handler):
    path = path_entry.get()
    global observer
    if os.path.isdir(path):
        if observer:
            observer.stop()
            observer.join()
        observer = Observer()
        event_handler.set_directory(path)
        observer.schedule(event_handler, path, recursive=True)
        observer.start()
        print(f"Рабочая директория изменена на: {path}")
    else:
        print(f"Некорректный путь: {path}")

def add_value(entry, dropdown, path_dict):
    value = entry.get()
    if value:
        short_path = "/".join(value.split("\\")[-3:])
        values = list(dropdown['values'])
        if short_path not in values:
            values.append(short_path)
            dropdown['values'] = values
            dropdown.set(short_path)
            path_dict[short_path] = value

def remove_value(dropdown, path_dict):
    value = dropdown.get()
    if value:
        values = list(dropdown['values'])
        if value in values:
            values.remove(value)
            dropdown['values'] = values
            dropdown.set("")
            try:
                del path_dict[value]
            except KeyError:
                # Игнорировать ошибку, если значение не найдено в словаре
                pass

def clear_entry(entry):
    entry.delete(0, tk.END)

def toggle_topmost(root, topmost_var):
    is_topmost = topmost_var.get()
    root.attributes('-topmost', not is_topmost)
    topmost_var.set(not is_topmost)

def on_dropdown_select(event, path_dropdown, path_entry, path_dict):
    selected_short_path = path_dropdown.get()
    if selected_short_path in path_dict:
        path_entry.delete(0, tk.END)
        path_entry.insert(0, path_dict[selected_short_path])

def create_gui():
    global observer
    global event_handler

    root = tk.Tk()
    root.title("JSON File Modifier")
    root.geometry("500x220")
    root.resizable(False, False)

    topmost_var = tk.BooleanVar(value=False)
    root.bind('<Control-Shift_L>', lambda e: toggle_topmost(root, topmost_var))

    tk.Label(root, text="Path:").grid(row=0, column=0, padx=5, pady=5, sticky='w')

    path_entry = tk.Entry(root, width=25)
    path_entry.grid(row=0, column=2, padx=5, pady=5, sticky='w')

    path_dropdown = ttk.Combobox(root, values=["Выберите путь"], state="readonly", width=25)
    path_dropdown.grid(row=0, column=3, padx=5, pady=5, sticky='w')

    tk.Button(root, text="P", command=lambda: set_working_directory(path_entry, path_dropdown, event_handler)).grid(row=0, column=1, padx=5, pady=5, sticky='w')
    tk.Button(root, text="O", command=lambda: add_value(path_entry, path_dropdown, path_dict)).grid(row=0, column=4, padx=5, pady=5, sticky='w')
    tk.Button(root, text="X", command=lambda: remove_value(path_dropdown, path_dict)).grid(row=0, column=5, padx=5, pady=5, sticky='w')

    tk.Label(root, text="Name:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
    tk.Label(root, text="Description:").grid(row=2, column=0, padx=5, pady=5, sticky='w')

    tk.Button(root, text="X", command=lambda: clear_entry(name_entry)).grid(row=1, column=1, padx=5, pady=5, sticky='w')
    name_entry = tk.Entry(root, width=25)
    name_entry.grid(row=1, column=2, padx=5, pady=5)

    tk.Button(root, text="X", command=lambda: clear_entry(desc_entry)).grid(row=2, column=1, padx=5, pady=5, sticky='w')
    desc_entry = tk.Entry(root, width=25)
    desc_entry.grid(row=2, column=2, padx=5, pady=5)

    name_dropdown = ttk.Combobox(root, values=["Создать новое значение"], state="readonly", width=25)
    name_dropdown.grid(row=1, column=3, padx=5, pady=5)

    desc_dropdown = ttk.Combobox(root, values=["Создать новое значение"], state="readonly", width=25)
    desc_dropdown.grid(row=2, column=3, padx=5, pady=5)

    tk.Button(root, text="O", command=lambda: add_value(name_entry, name_dropdown, path_dict)).grid(row=1, column=4, padx=5, pady=5, sticky='w')
    tk.Button(root, text="O", command=lambda: add_value(desc_entry, desc_dropdown, path_dict)).grid(row=2, column=4, padx=5, pady=5, sticky='w')
    tk.Button(root, text="X", command=lambda: remove_value(name_dropdown, path_dict)).grid(row=1, column=5, padx=5, pady=5, sticky='w')
    tk.Button(root, text="X", command=lambda: remove_value(desc_dropdown, path_dict)).grid(row=2, column=5, padx=5, pady=5, sticky='w')

    file_count_var = tk.StringVar(value="Файлов было создано: 0")
    tk.Label(root, textvariable=file_count_var).grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky='w')

    last_file_var = tk.StringVar(value="Последний файл: ")
    tk.Label(root, textvariable=last_file_var).grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky='w')

    last_name_var = tk.StringVar(value="Name: ")
    tk.Label(root, textvariable=last_name_var).grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky='w')

    last_desc_var = tk.StringVar(value="Description: ")
    tk.Label(root, textvariable=last_desc_var).grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky='w')

    path_dict = {}
    event_handler = FileHandler(name_entry, desc_entry, file_count_var, last_file_var, last_name_var, last_desc_var)

    path_dropdown.bind("<<ComboboxSelected>>", lambda e: on_dropdown_select(e, path_dropdown, path_entry, path_dict))

    root.mainloop()

if __name__ == "__main__":
    observer = None
    create_gui()
