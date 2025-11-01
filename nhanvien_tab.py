import tkinter as tk
from tkinter import ttk, messagebox
from db_connect import connect_db

def create_tab(notebook):
    tab = ttk.Frame(notebook)
    notebook.add(tab, text="Quản lý nhân viên")

    form_frame = tk.Frame(tab, pady=10)
    form_frame.pack()

    labels = ["Mã NV:", "Tên NV:", "Địa chỉ:", "Chức vụ:", "Lương:"]
    entries = []
    for i, text in enumerate(labels):
        tk.Label(form_frame, text=text).grid(row=i, column=0)
        e = tk.Entry(form_frame)
        e.grid(row=i, column=1)
        entries.append(e)

    columns = ("manhanvien", "tennhanvien", "diachi", "chucvu", "luong")
    tree = ttk.Treeview(tab, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True)

    def load_data():
        tree.delete(*tree.get_children())
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quanlynhanvien")
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)
        conn.close()

    def them():
        conn = connect_db()
        cursor = conn.cursor()
        sql = "INSERT INTO quanlynhanvien VALUES (%s, %s, %s, %s, %s)"
        val = tuple(e.get() for e in entries)
        cursor.execute(sql, val)
        conn.commit()
        conn.close()
        load_data()
        messagebox.showinfo("Thành công", "Đã thêm nhân viên!")

    def xoa():
        selected = tree.selection()
        if not selected:
            return
        manv = tree.item(selected[0])["values"][0]
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM quanlynhanvien WHERE manhanvien=%s", (manv,))
        conn.commit()
        conn.close()
        load_data()

    btn_frame = tk.Frame(tab, pady=10)
    btn_frame.pack()
    tk.Button(btn_frame, text="Thêm", command=them).grid(row=0, column=0, padx=10)
    tk.Button(btn_frame, text="Xoá", command=xoa).grid(row=0, column=1, padx=10)
    tk.Button(btn_frame, text="Tải lại", command=load_data).grid(row=0, column=2, padx=10)

    load_data()