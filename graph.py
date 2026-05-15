import tkinter as tk
from tkinter import messagebox, ttk
import threading
import os
import sys
import io
import ctypes
import time
import generator
import ext_sort_py
import clean_file
C_LIB = None
C_AVAILABLE = False
CALLBACK_TYPE = ctypes.CFUNCTYPE(None, ctypes.c_int)
try:
    dll_name = "ext_sort_c.dll" if os.name == "nt" else "ext_sort_c.so"
    dll_path = os.path.join(os.path.dirname(__file__), dll_name)
    C_LIB = ctypes.CDLL(dll_path)
    C_LIB.sort_ext_c.argtypes = [
        ctypes.c_char_p, ctypes.c_int, ctypes.c_int,
        ctypes.c_int, ctypes.c_char_p, ctypes.c_void_p
    ]
    C_LIB.sort_ext_c.restype = ctypes.c_int
    C_AVAILABLE = True
except Exception:
    pass
root = tk.Tk()
root.geometry("620x780")
root.title("Внешняя сортировка CSV")
root.configure(bg="#FFE4C4")

title_lbl = tk.Label(root, text="Система внешней сортировки CSV файлов",bg="#FFE4C4", fg="#8B4513", font=("Arial", 14, "bold"))
title_lbl.pack(pady=10)
settings_frame = tk.Frame(root, bg="#FFE4C4", bd=2, relief="solid")
settings_frame.pack(pady=5, padx=20, fill=tk.X)
tk.Label(settings_frame, text="Модуль сортировки: ", bg="#FFE4C4",font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=10, pady=5)
module_var = tk.StringVar(value="Python")
module_combo = ttk.Combobox(settings_frame, textvariable=module_var,state="readonly", width=15)
module_combo['values'] = ["Python", "C"] if C_AVAILABLE else ["Python"]
module_combo.grid(row=0, column=1, padx=5, pady=5)
tk.Label(settings_frame, text="Ключ сортировки: ", bg="#FFE4C4",font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
key_var = tk.StringVar(value="Пробег")
key_combo = ttk.Combobox(settings_frame, textvariable=key_var,state="readonly", width=15)
key_combo['values'] = ["Марка автомобиля", "Пробег", "Год выпуска", "Количество владельцев"]
key_combo.grid(row=1, column=1, padx=5, pady=5)
tk.Label(settings_frame, text="Порядок сортировки: ", bg="#FFE4C4",font=("Arial", 10)).grid(row=2, column=0, sticky="w", padx=10, pady=5)
order_var = tk.StringVar(value="По возрастанию")
order_combo = ttk.Combobox(settings_frame, textvariable=order_var,state="readonly", width=15)
order_combo['values'] = ["По возрастанию", "По убыванию"]
order_combo.grid(row=2, column=1, padx=5, pady=5)

tk.Label(settings_frame, text="Диапазон строк: ", bg="#FFE4C4", font=("Arial", 10)).grid(row=3, column=0, sticky="w", padx=10, pady=5)
range_var = tk.StringVar(value="0-50")
range_combo = ttk.Combobox(settings_frame, textvariable=range_var,state="readonly", width=15)
range_combo['values'] = ["0-50", "2000000-2000050", "3999950-4000000"]
range_combo.grid(row=3, column=1, padx=5, pady=5)
buttons_frame = tk.Frame(root, bg="#FFE4C4")
buttons_frame.pack(pady=15)
but_gen = tk.Button(buttons_frame, text="Сгенерировать", bg="#D2B48C", fg="white", font=("Arial", 10, "bold"), width=18, height=2)
but_gen.grid(row=0, column=0, padx=10, pady=5)
but_sort = tk.Button(buttons_frame, text="Сортировать", bg="#D2B48C", fg="white", font=("Arial", 10, "bold"), width=18, height=2)
but_sort.grid(row=0, column=1, padx=10, pady=5)
but_view_csv = tk.Button(buttons_frame, text="Просмотр L5.csv", bg="#D2B48C", fg="white", font=("Arial", 10, "bold"), width=18, height=2)
but_view_csv.grid(row=1, column=0, padx=10, pady=5)
but_clean = tk.Button(buttons_frame, text="Очистить", bg="#D2B48C", fg="white", font=("Arial", 10, "bold"), width=18, height=2)
but_clean.grid(row=1, column=1, padx=10, pady=5)
but_range = tk.Button(buttons_frame, text="Показать диапазон", bg="#D2B48C", fg="white", font=("Arial", 10, "bold"), width=18, height=2)
but_range.grid(row=2, column=0, columnspan=2, pady=5)
status_lbl = tk.Label(root, text="Готов к работе", bg="#FFE4C4", fg="#8B4513", font=("Arial", 10, "italic"))
status_lbl.pack(pady=5)
progress_frame = tk.Frame(root, bg="#FFE4C4")
progress_frame.pack(pady=2, padx=20, fill=tk.X)
progress_var = tk.IntVar(value=0)
progress_bar = ttk.Progressbar(
    progress_frame,
    variable=progress_var,
    maximum=100,
    length=400,
    mode="determinate"
)
progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

progress_lbl = tk.Label(
    progress_frame,
    text="0%",
    bg="#FFE4C4",
    fg="#8B4513",
    font=("Arial", 10, "bold"),
    width=5
)
progress_lbl.pack(side=tk.LEFT)

file_name_lbl = tk.Label(root, text="L5.csv", bg="#FFE4C4", fg="#8B4513",font=("Arial", 10))
file_name_lbl.pack(pady=2)

content_lbl = tk.Label(root, text="Содержимое файла:", bg="#FFE4C4", fg="#8B4513", font=("Arial", 10, "bold"))
content_lbl.pack(pady=(10, 0), anchor="w", padx=20)
frame_list = tk.Frame(root)
frame_list.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)
scrollbar = tk.Scrollbar(frame_list)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
list_display = tk.Listbox(frame_list, height=18, bg="#FFF8DC", fg="#8B4513",font=("Courier", 9), yscrollcommand=scrollbar.set)
list_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=list_display.yview)
is_busy = False
current_file = "L5.csv"
COL_MAP = {"Марка автомобиля": 0, "Пробег": 1, "Год выпуска": 2, "Количество владельцев": 3}
BUTTONS = []

def set_status(msg):
    root.after(0, lambda: status_lbl.config(text=msg))

def set_progress(pct):
    pct = max(0, min(100, int(pct)))
    def _update():
        progress_var.set(pct)
        progress_lbl.config(text=f"{pct}%")
    root.after(0, _update)

def show_data(filepath):
    list_display.delete(0, tk.END)
    if not os.path.exists(filepath):
        list_display.insert(tk.END, "Файл не найден")
        return
    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            lines = f.readlines(52 * 1024)
        if lines:
            header = lines[0].strip()
            formatted_header = " | ".join(header.split(", "))
            list_display.insert(tk.END, formatted_header)
            list_display.insert(tk.END, "-" * len(formatted_header))
            for i, line in enumerate(lines[1:], start=1):
                if i > 50:
                    list_display.insert(tk.END, "...")
                    break
                list_display.insert(tk.END, " | ".join(line.strip().split(", ")))
    except Exception as e:
        list_display.insert(tk.END, f"Ошибка чтения: {e}")

def disable_buttons():
    root.after(0, lambda: [b.config(state="disabled") for b in BUTTONS])

def enable_buttons():
    root.after(0, lambda: [b.config(state="normal") for b in BUTTONS])

def execute(task):
    global is_busy
    if is_busy:
        messagebox.showwarning("Внимание", "Операция уже выполняется")
        return
    is_busy = True
    disable_buttons()
    threading.Thread(target=run_worker, args=(task,), daemon=True).start()

def run_worker(task):
    global is_busy
    finish_evt = threading.Event()
    try:
        if task == "gen":
            set_status("Генерация файла...")
            set_progress(0)
            sys.stdout = io.StringIO()

            def gen_cb(msg, pct):
                set_status(f"Генерация {pct}%")
                set_progress(pct)

            generator.generate_car_data("L5.csv", target_bytes=1_073_741_824,
                callback=gen_cb)
            sys.stdout = sys.__stdout__
            set_progress(100)
            set_status("Генерация завершена")
            root.after(0, lambda: show_data("L5.csv"))
            root.after(0, lambda: messagebox.showinfo("Успех", "Файл L5.csv создан"))

        elif task == "sort":
            set_status("Сортировка...")
            set_progress(0)
            idx = COL_MAP[key_var.get()]
            reverse = order_var.get() == "По убыванию"
            module = module_var.get()
            sys.stdout = io.StringIO()

            if module == "C" and C_AVAILABLE:
                set_status("Сортировка (C)...")
                out_path = "sorted_c.txt"

                def _cb(pct):
                    set_status(f"Сортировка... {pct}%")
                    set_progress(pct)

                cb_func = CALLBACK_TYPE(_cb)
                ret = C_LIB.sort_ext_c(
                    b"L5.csv",
                    ctypes.c_int(idx),
                    ctypes.c_int(50),
                    ctypes.c_int(1 if reverse else 0),
                    out_path.encode("utf-8"),
                    cb_func
                )
                if ret != 0:
                    raise RuntimeError(f"C сортировка вернула код {ret}")
            else:
                set_status("Сортировка (Python)...")
                out_path = "sorted_py.txt"

                def sort_cb(pct):
                    set_status(f"Сортировка (Python) {pct}%")
                    set_progress(pct)

                ext_sort_py.sort_ext("L5.csv", idx, reverse=reverse,
                    callback=sort_cb)

            sys.stdout = sys.__stdout__
            set_progress(100)
            set_status("Сортировка завершена")
            root.after(0, lambda: show_data(out_path))
            root.after(0, lambda: messagebox.showinfo("Успех", f"Результат в {out_path}"))

        elif task == "view_csv":
            set_status("Обновление...")
            root.after(0, lambda: show_data("L5.csv"))

        elif task == "view_res":
            set_status("Обновление...")
            module = module_var.get()
            f_name = "sorted_c.txt" if module == "C" else "sorted_py.txt"
            if os.path.exists(f_name):
                root.after(0, lambda n=f_name: show_data(n))
            else:
                set_status("Файл не найден")

        elif task == "clean":
            set_status("Очистка проекта...")
            sys.stdout = io.StringIO()
            clean_file.clean_project()
            sys.stdout = sys.__stdout__
            set_progress(0)
            set_status("Проект очищен")

    except Exception as e:
        err_msg = str(e)
        sys.stdout = sys.__stdout__
        set_status("Ошибка")
        root.after(0, lambda: messagebox.showerror("Ошибка", err_msg))
    finally:
        finish_evt.set()
        is_busy = False
        enable_buttons()
        set_status("Готов к работе")

def show_selected_range():
    module = module_var.get()
    f_name = "sorted_c.txt" if module == "C" else "sorted_py.txt"
    if not os.path.exists(f_name):
        set_status(f"Файл {f_name} не найден. Выполните сортировку.")
        messagebox.showwarning(
            "Файл не найден",
            f"Отсортированный файл '{f_name}' не найден.\n"
            f"Сначала выполните сортировку модулем «{module}»."
        )
        return
    range_str = range_var.get()
    start, end = map(int, range_str.split("-"))
    col_name = key_var.get()
    list_display.delete(0, tk.END)
    info = f"Файл: {f_name} | Ключ: {col_name} | Строки: {range_str}"
    list_display.insert(tk.END, info)
    list_display.insert(tk.END, "=" * len(info))
    try:
        with open(f_name, "r", encoding="utf-8-sig") as f:
            # Показываем заголовок CSV если есть
            first_line = f.readline().strip()
            if not first_line:
                list_display.insert(tk.END, "Файл пуст")
                return
            if "Марка" in first_line or "Пробег" in first_line:
                formatted_header = " | ".join(first_line.split(","))
                list_display.insert(tk.END, formatted_header)
                list_display.insert(tk.END, "-" * len(formatted_header))
                data_start = 0
            else:
                f.seek(0)
                data_start = 0
            count = 0
            for i, line in enumerate(f):
                if i < start:
                    continue
                if i > end:
                    break
                stripped = line.strip()
                if stripped:
                    list_display.insert(
                        tk.END,
                        " | ".join(stripped.split(","))
                    )
                    count += 1

        set_status(f"Показаны строки {range_str} из {f_name} | Ключ: {col_name}")

    except Exception as e:
        list_display.insert(tk.END, f"Ошибка чтения: {e}")
        set_status("Ошибка при чтении файла")

BUTTONS.extend([but_gen, but_sort, but_view_csv, but_clean, but_range])
but_gen.config(command=lambda: execute("gen"))
but_sort.config(command=lambda: execute("sort"))
but_view_csv.config(command=lambda: execute("view_csv"))
but_clean.config(command=lambda: execute("clean"))
but_range.config(command=show_selected_range)

root.mainloop()