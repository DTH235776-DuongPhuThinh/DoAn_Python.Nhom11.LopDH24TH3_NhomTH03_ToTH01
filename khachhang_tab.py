import tkinter as tk
from tkinter import ttk, messagebox
from db_connect import connect_db

def create_tab(notebook):
    tab = ttk.Frame(notebook)
    notebook.add(tab, text="Quản lý khách hàng")

    form_frame = tk.Frame(tab, pady=10)
    form_frame.pack()

    labels = ["Mã KH:", "Tên KH:", "Địa chỉ:", "SĐT:"]
    entries = []
    for i, text in enumerate(labels):
        tk.Label(form_frame, text=text).grid(row=i, column=0)
        e = tk.Entry(form_frame)
        e.grid(row=i, column=1)
        entries.append(e)

    columns = ("Mã khách hàng", "Tên khách hàng", "Địa chỉ khách hàng", "Số điện thoại khách hàng")
    tree = ttk.Treeview(tab, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True)

    def load_data():
        tree.delete(*tree.get_children())
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quanlykhachhang")
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)
        conn.close()

    def them():
        conn = connect_db()
        cursor = conn.cursor()
        sql = "INSERT INTO quanlykhachhang VALUES (%s, %s, %s, %s)"
        val = tuple(e.get() for e in entries)
        cursor.execute(sql, val)
        conn.commit()
        conn.close()
        load_data()
        messagebox.showinfo("Thành công", "Đã thêm khách hàng!")

    def xoa():
        selected = tree.selection()
        if not selected:
            return
        makh = tree.item(selected[0])["values"][0]
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM quanlykhachhang WHERE makhachhang=%s", (makh,))
        conn.commit()
        conn.close()
        load_data()

    btn_frame = tk.Frame(tab, pady=10)
    btn_frame.pack()
    tk.Button(btn_frame, text="Thêm", command=them).grid(row=0, column=0, padx=10)
    tk.Button(btn_frame, text="Xoá", command=xoa).grid(row=0, column=1, padx=10)
    tk.Button(btn_frame, text="Tải lại", command=load_data).grid(row=0, column=2, padx=10)

    load_data()