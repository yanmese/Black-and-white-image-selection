import os
import shutil
from PIL import Image
import tkinter as tk
from tkinter import filedialog
import threading
import concurrent.futures


def is_image_file(file_path):
    _, ext = os.path.splitext(file_path)
    return ext.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']


def is_low_saturation(image_path):
    try:
        image = Image.open(image_path)
        image = image.convert('HSV')
        saturation = image.split()[1]
        saturation = saturation.histogram()
        total_pixels = sum(saturation)
        low_saturation_pixels = sum(saturation[:10])
        ratio = low_saturation_pixels / total_pixels
        return ratio > 0.95
    except (OSError, PIL.UnidentifiedImageError):
        return False


def copy_low_saturation_images(source_dir, dest_dir, progress_var, filename_var, pause_var):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    total_files = 0
    processed_files = 0

    for root, dirs, files in os.walk(source_dir):
        if pause_var.is_set():
            break

        for filename in files:
            if pause_var.is_set():
                break

            file_path = os.path.join(root, filename)
            if os.path.isfile(file_path) and is_image_file(file_path):
                if is_low_saturation(file_path):
                    relative_path = os.path.relpath(file_path, source_dir)
                    dest_path = os.path.join(dest_dir, relative_path)
                    dest_folder = os.path.dirname(dest_path)
                    if not os.path.exists(dest_folder):
                        os.makedirs(dest_folder)
                    shutil.copy2(file_path, dest_path)

            processed_files += 1
            progress_var.set(f"处理进度: {processed_files}/{total_files}")
            filename_var.set(f"当前文件: {filename}")
            window.update()

        total_files += len(files)

    progress_var.set("处理完成")
    filename_var.set("")


def select_source_folder():
    folder_path = filedialog.askdirectory()
    source_entry.delete(0, tk.END)
    source_entry.insert(tk.END, folder_path)


def select_destination_folder():
    folder_path = filedialog.askdirectory()
    destination_entry.delete(0, tk.END)
    destination_entry.insert(tk.END, folder_path)


def start_processing():
    source_folder = source_entry.get()
    destination_folder = destination_entry.get()

    progress_var.set("正在处理...")
    pause_var.clear()

    processing_thread = threading.Thread(target=copy_low_saturation_images,
                                         args=(source_folder, destination_folder, progress_var, filename_var, pause_var))
    processing_thread.start()


def pause_processing():
    if pause_button["text"] == "暂停":
        pause_button["text"] = "继续"
        pause_var.set()
    else:
        pause_button["text"] = "暂停"
        pause_var.clear()


# 创建主窗口
window = tk.Tk()
window.title("低饱和黑白图片处理")
window.geometry("400x300")

# 源文件夹选择部分
source_frame = tk.Frame(window)
source_frame.pack(pady=10)

source_label = tk.Label(source_frame, text="源文件夹:")

source_label.pack(side=tk.LEFT)
source_entry = tk.Entry(source_frame)
source_entry.pack(side=tk.LEFT)
source_button = tk.Button(source_frame, text="选择文件夹", command=select_source_folder)
source_button.pack(side=tk.LEFT)

# 目标文件夹选择部分
destination_frame = tk.Frame(window)
destination_frame.pack(pady=10)

destination_label = tk.Label(destination_frame, text="目标文件夹:")
destination_label.pack(side=tk.LEFT)
destination_entry = tk.Entry(destination_frame)
destination_entry.pack(side=tk.LEFT)
destination_button = tk.Button(destination_frame, text="选择文件夹", command=select_destination_folder)
destination_button.pack(side=tk.LEFT)

# 开始和暂停按钮
button_frame = tk.Frame(window)
button_frame.pack(pady=10)

start_button = tk.Button(button_frame, text="开始处理", command=start_processing)
start_button.pack(side=tk.LEFT, padx=5)

pause_button = tk.Button(button_frame, text="暂停", command=pause_processing)
pause_button.pack(side=tk.LEFT, padx=5)

# 进度标签和文件名标签
progress_var = tk.StringVar()
progress_label = tk.Label(window, textvariable=progress_var)
progress_label.pack()

filename_var = tk.StringVar()
filename_label = tk.Label(window, textvariable=filename_var)
filename_label.pack()

# 暂停变量
pause_var = threading.Event()

window.mainloop()

