import tkinter as tk
from tkinter import ttk
import xemay_tab
import nhanvien_tab
import khachhang_tab

def main():
    root = tk.Tk()
    root.title("HỆ THỐNG QUẢN LÝ XE MÁY")
    root.geometry("1000x600")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    xemay_tab.create_tab(notebook)
    nhanvien_tab.create_tab(notebook)
    khachhang_tab.create_tab(notebook)

    root.mainloop()

if __name__ == "__main__":
    main()