import tkinter as tk
from tkinter import ttk, messagebox
from db_connect import connect_db  # Hàm trả về kết nối MySQL

def create_view(parent_tab, nhanvien_data):
    """
    Tạo giao diện quản lý Nhân viên.
    """
    current_mode = None
    selected_item_id = None

    # ==========================
    # 1. FORM NHẬP LIỆU
    # ==========================
    form_frame = ttk.LabelFrame(parent_tab, text="Thông tin Nhân viên")
    form_frame.pack(fill="x", padx=10, pady=10)

    labels = ["Mã NV:", "Tên NV:", "Địa chỉ:", "Chức vụ:", "Lương:"]
    entry_vars = {}
    for i, text in enumerate(labels):
        ttk.Label(form_frame, text=text).grid(row=i, column=0, sticky="w", padx=5, pady=5)
        entry = ttk.Entry(form_frame, width=40)
        entry.grid(row=i, column=1, padx=5, pady=5)
        entry_vars[text] = entry

    # ==========================
    # 2. TREEVIEW HIỂN THỊ DỮ LIỆU
    # ==========================
    tree_frame = ttk.Frame(parent_tab)
    tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

    tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
    tree_scroll_y.pack(side="right", fill="y")
    tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
    tree_scroll_x.pack(side="bottom", fill="x")

    tree = ttk.Treeview(
        tree_frame,
        columns=("manv", "tennv", "diachi", "chucvu", "luong"),
        show="headings",
        yscrollcommand=tree_scroll_y.set,
        xscrollcommand=tree_scroll_x.set
    )
    tree_scroll_y.config(command=tree.yview)
    tree_scroll_x.config(command=tree.xview)

    tree.heading("manv", text="Mã NV")
    tree.heading("tennv", text="Tên NV")
    tree.heading("diachi", text="Địa chỉ")
    tree.heading("chucvu", text="Chức vụ")
    tree.heading("luong", text="Lương")

    tree.column("manv", width=80, anchor="w")
    tree.column("tennv", width=150, anchor="w")
    tree.column("diachi", width=200, anchor="w")
    tree.column("chucvu", width=100, anchor="w")
    tree.column("luong", width=100, anchor="e")
    tree.pack(fill="both", expand=True)

    # ==========================
    # 3. HÀM NỘI BỘ
    # ==========================
    def set_form_state(state):
        for e in entry_vars.values():
            e.config(state=state)

    def clear_entries():
        nonlocal current_mode, selected_item_id
        current_mode = None
        selected_item_id = None
        set_form_state('normal')
        for e in entry_vars.values():
            e.delete(0, tk.END)
        set_form_state('disabled')
        if tree.selection():
            tree.selection_remove(tree.selection())

    def refresh_tree():
        tree.delete(*tree.get_children())
        for nv in nhanvien_data:
            tree.insert("", tk.END, iid=nv['manhanvien'], values=(
                nv['manhanvien'], nv['tennhanvien'], nv['diachi'], nv['chucvu'], nv['luong']
            ))

    def on_add():
        nonlocal current_mode
        clear_entries()
        current_mode = 'add'
        set_form_state('normal')
        entry_vars["Mã NV:"].focus()

    def on_edit():
        nonlocal current_mode, selected_item_id
        if not selected_item_id:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn nhân viên để sửa.")
            return
        current_mode = 'edit'
        set_form_state('normal')
        entry_vars["Mã NV:"].config(state='disabled')  # không được sửa mã NV
        entry_vars["Tên NV:"].focus()

    def on_save():
        nonlocal current_mode, selected_item_id
        manv = entry_vars["Mã NV:"].get().strip()
        tennv = entry_vars["Tên NV:"].get().strip()
        diachi = entry_vars["Địa chỉ:"].get().strip() or None
        chucvu = entry_vars["Chức vụ:"].get().strip() or None
        try:
            luong = float(entry_vars["Lương:"].get().strip()) if entry_vars["Lương:"].get().strip() else None
        except ValueError:
            messagebox.showerror("Lỗi nhập liệu", "Lương phải là số hợp lệ!")
            return

        if not manv or not tennv:
            messagebox.showwarning("Thiếu thông tin", "Mã NV và Tên NV là bắt buộc!")
            return

        new_data_dict = {'manhanvien': manv, 'tennhanvien': tennv, 'diachi': diachi, 'chucvu': chucvu, 'luong': luong}

        try:
            conn = connect_db()
            cursor = conn.cursor(dictionary=True)

            if current_mode == 'add':
                if any(nv['manhanvien'] == manv for nv in nhanvien_data):
                    messagebox.showerror("Lỗi", "Mã NV đã tồn tại!")
                    return
                sql = "INSERT INTO quanlynhanvien (manhanvien, tennhanvien, diachi, chucvu, luong) VALUES (%s,%s,%s,%s,%s)"
                cursor.execute(sql, (manv, tennv, diachi, chucvu, luong))
                nhanvien_data.append(new_data_dict)
                messagebox.showinfo("Thành công", f"Đã thêm nhân viên {manv}")

            elif current_mode == 'edit':
                sql = "UPDATE quanlynhanvien SET tennhanvien=%s, diachi=%s, chucvu=%s, luong=%s WHERE manhanvien=%s"
                cursor.execute(sql, (tennv, diachi, chucvu, luong, manv))
                for i, nv in enumerate(nhanvien_data):
                    if nv['manhanvien'] == selected_item_id:
                        nhanvien_data[i] = new_data_dict
                        break
                messagebox.showinfo("Thành công", f"Đã cập nhật nhân viên {manv}")

            conn.commit()
        except Exception as e:
            messagebox.showerror("Lỗi CSDL", f"Lỗi khi lưu dữ liệu:\n{e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

        refresh_tree()
        clear_entries()

    def on_delete():
        nonlocal selected_item_id
        if not selected_item_id:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn nhân viên để xóa.")
            return
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa nhân viên {selected_item_id}?"):
            return
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM quanlynhanvien WHERE manhanvien=%s", (selected_item_id,))
            conn.commit()
            nhanvien_data[:] = [nv for nv in nhanvien_data if nv['manhanvien'] != selected_item_id]
            messagebox.showinfo("Thành công", "Đã xóa nhân viên!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi xóa dữ liệu:\n{e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

        refresh_tree()
        clear_entries()

    def on_tree_select(event):
        nonlocal selected_item_id
        selected_items = tree.selection()
        if not selected_items:
            clear_entries()
            return
        selected_item_id = selected_items[0]
        nv = next((n for n in nhanvien_data if n['manhanvien'] == selected_item_id), None)
        if not nv: return
        set_form_state('normal')
        entry_vars["Mã NV:"].delete(0, tk.END)
        entry_vars["Mã NV:"].insert(0, nv['manhanvien'])
        entry_vars["Tên NV:"].delete(0, tk.END)
        entry_vars["Tên NV:"].insert(0, nv['tennhanvien'])
        entry_vars["Địa chỉ:"].delete(0, tk.END)
        entry_vars["Địa chỉ:"].insert(0, nv['diachi'] or "")
        entry_vars["Chức vụ:"].delete(0, tk.END)
        entry_vars["Chức vụ:"].insert(0, nv['chucvu'] or "")
        entry_vars["Lương:"].delete(0, tk.END)
        entry_vars["Lương:"].insert(0, nv['luong'] if nv['luong'] is not None else "")
        set_form_state('disabled')

    tree.bind("<<TreeviewSelect>>", on_tree_select)

    # ==========================
    # 4. NÚT CHỨC NĂNG
    # ==========================
    button_frame = tk.Frame(parent_tab)
    button_frame.pack(pady=10, fill="x")

    btn_them = ttk.Button(button_frame, text="Thêm", command=on_add)
    btn_sua = ttk.Button(button_frame, text="Sửa", command=on_edit)
    btn_luu = ttk.Button(button_frame, text="Lưu", command=on_save)
    btn_xoa = ttk.Button(button_frame, text="Xóa", command=on_delete)
    btn_boqua = ttk.Button(button_frame, text="Bỏ qua", command=clear_entries)
    btn_thoat = ttk.Button(button_frame, text="Thoát", command=parent_tab.winfo_toplevel().destroy)

    for i, btn in enumerate([btn_them, btn_sua, btn_luu, btn_xoa, btn_boqua, btn_thoat]):
        btn.pack(side=tk.LEFT, padx=5, expand=True)

    # ==========================
    # 5. Khởi tạo dữ liệu
    # ==========================
    def load_data():
        try:
            conn = connect_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM quanlynhanvien")
            nhanvien_data.clear()
            nhanvien_data.extend(cursor.fetchall())
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
        refresh_tree()
        clear_entries()

    load_data()
