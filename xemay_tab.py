import tkinter as tk
from tkinter import ttk, messagebox
from db_connect import connect_db

def create_tab(notebook):
    tab = ttk.Frame(notebook)
    notebook.add(tab, text="Quản lý xe máy")

    form_frame = tk.Frame(tab, pady=10)
    form_frame.pack()

    tk.Label(form_frame, text="Mã xe máy:").grid(row=0, column=0)
    tk.Label(form_frame, text="Tên xe máy:").grid(row=1, column=0)
    tk.Label(form_frame, text="Hãng SX:").grid(row=2, column=0)
    tk.Label(form_frame, text="Giá:").grid(row=3, column=0)
    tk.Label(form_frame, text="Số lượng:").grid(row=4, column=0)

    entry_ma = tk.Entry(form_frame)
    entry_ten = tk.Entry(form_frame)
    entry_hang = tk.Entry(form_frame)
    entry_gia = tk.Entry(form_frame)
    entry_sl = tk.Entry(form_frame)

    entry_ma.grid(row=0, column=1)
    entry_ten.grid(row=1, column=1)
    entry_hang.grid(row=2, column=1)
    entry_gia.grid(row=3, column=1)
    entry_sl.grid(row=4, column=1)

    columns = ("maxemay", "tenxemay", "hangsx", "gia", "soluong")
    tree = ttk.Treeview(tab, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True)

    def load_data():
        tree.delete(*tree.get_children())
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quanlyxemay")
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)
        conn.close()

    def them():
        conn = connect_db()
        cursor = conn.cursor()
        sql = "INSERT INTO quanlyxemay VALUES (%s, %s, %s, %s, %s)"
        val = (entry_ma.get(), entry_ten.get(), entry_hang.get(),
               entry_gia.get(), entry_sl.get())
        try:
            cursor.execute(sql, val)
            conn.commit()
            messagebox.showinfo("Thành công", "Đã thêm xe máy!")
            load_data()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
        conn.close()

    def xoa():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Chọn 1 dòng để xoá")
            return
        item = tree.item(selected[0])["values"][0]
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM quanlyxemay WHERE maxemay=%s", (item,))
        conn.commit()
        conn.close()
        load_data()
        messagebox.showinfo("Xoá", "Đã xoá xe máy!")

    def sua():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Chọn 1 dòng để sửa")
            return
        item = tree.item(selected[0])["values"][0]
        conn = connect_db()
        cursor = conn.cursor()
        sql = """UPDATE quanlyxemay 
                 SET tenxemay=%s, hangsx=%s, gia=%s, soluong=%s 
                 WHERE maxemay=%s"""
        val = (entry_ten.get(), entry_hang.get(),
entry_gia.get(), entry_sl.get(), item)
        cursor.execute(sql, val)
        conn.commit()
        conn.close()
        load_data()
        messagebox.showinfo("Cập nhật", "Sửa thông tin thành công!")

    btn_frame = tk.Frame(tab, pady=10)
    btn_frame.pack()
    tk.Button(btn_frame, text="Thêm", command=them).grid(row=0, column=0, padx=10)
    tk.Button(btn_frame, text="Sửa", command=sua).grid(row=0, column=1, padx=10)
    tk.Button(btn_frame, text="Xoá", command=xoa).grid(row=0, column=2, padx=10)
    tk.Button(btn_frame, text="Tải lại", command=load_data).grid(row=0, column=3, padx=10)

    load_data()