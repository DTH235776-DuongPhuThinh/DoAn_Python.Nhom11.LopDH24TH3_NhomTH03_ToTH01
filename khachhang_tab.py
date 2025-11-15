import tkinter as tk
from tkinter import ttk, messagebox
from db_connect import connect_db  # Hàm trả về kết nối MySQL

def create_view(parent_tab, khachhang_data):
    """
    Tạo giao diện quản lý Khách hàng hoàn chỉnh.
    """
    # --- Biến nội bộ ---
    current_mode = None
    selected_item_id = None

    # ==========================
    # 1. FORM NHẬP LIỆU
    # ==========================
    form_frame = ttk.LabelFrame(parent_tab, text="Thông tin Khách hàng")
    form_frame.pack(fill="x", padx=10, pady=10)

    labels = ["Mã KH:", "Tên KH:", "Địa chỉ:"]
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
        columns=("makh", "tenkh", "diachi"),
        show="headings",
        yscrollcommand=tree_scroll_y.set,
        xscrollcommand=tree_scroll_x.set
    )
    tree_scroll_y.config(command=tree.yview)
    tree_scroll_x.config(command=tree.xview)

    tree.heading("makh", text="Mã KH")
    tree.heading("tenkh", text="Tên KH")
    tree.heading("diachi", text="Địa chỉ")

    tree.column("makh", width=100, anchor="w")
    tree.column("tenkh", width=150, anchor="w")
    tree.column("diachi", width=200, anchor="w")
    tree.pack(fill="both", expand=True)

    # ==========================
    # 3. HÀM NỘI BỘ
    # ==========================
    def set_form_state(state):
        """state: 'normal' hoặc 'disabled'"""
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
        for kh in khachhang_data:
            tree.insert("", tk.END, iid=kh['makhachhang'], values=(
                kh['makhachhang'], kh['tenkhachhang'], kh['diachikhachhang']
            ))

    def on_add():
        nonlocal current_mode
        clear_entries()
        current_mode = 'add'
        set_form_state('normal')
        entry_vars["Mã KH:"].focus()

    def on_edit():
        nonlocal current_mode, selected_item_id
        if not selected_item_id:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn khách hàng để sửa.")
            return
        current_mode = 'edit'
        set_form_state('normal')
        entry_vars["Mã KH:"].config(state='disabled')  # không được sửa mã KH
        entry_vars["Tên KH:"].focus()

    def on_save():
        nonlocal current_mode, selected_item_id
        makh = entry_vars["Mã KH:"].get().strip()
        tenkh = entry_vars["Tên KH:"].get().strip()
        diachi = entry_vars["Địa chỉ:"].get().strip() or None

        if not makh or not tenkh:
            messagebox.showwarning("Thiếu thông tin", "Mã KH và Tên KH là bắt buộc!")
            return

        new_data_dict = {'makhachhang': makh, 'tenkhachhang': tenkh, 'diachikhachhang': diachi}

        try:
            conn = connect_db()
            cursor = conn.cursor(dictionary=True)

            if current_mode == 'add':
                if any(kh['makhachhang'] == makh for kh in khachhang_data):
                    messagebox.showerror("Lỗi", "Mã KH đã tồn tại!")
                    return
                sql = "INSERT INTO quanlykhachhang (makhachhang, tenkhachhang, diachikhachhang) VALUES (%s, %s, %s)"
                cursor.execute(sql, (makh, tenkh, diachi))
                khachhang_data.append(new_data_dict)
                messagebox.showinfo("Thành công", f"Đã thêm khách hàng {makh}")

            elif current_mode == 'edit':
                sql = "UPDATE quanlykhachhang SET tenkhachhang=%s, diachikhachhang=%s WHERE makhachhang=%s"
                cursor.execute(sql, (tenkh, diachi, makh))
                for i, kh in enumerate(khachhang_data):
                    if kh['makhachhang'] == selected_item_id:
                        khachhang_data[i] = new_data_dict
                        break
                messagebox.showinfo("Thành công", f"Đã cập nhật khách hàng {makh}")

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
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn khách hàng để xóa.")
            return
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa khách hàng {selected_item_id}?"):
            return
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM quanlykhachhang WHERE makhachhang=%s", (selected_item_id,))
            conn.commit()
            khachhang_data[:] = [kh for kh in khachhang_data if kh['makhachhang'] != selected_item_id]
            messagebox.showinfo("Thành công", "Đã xóa khách hàng!")
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
        kh = next((k for k in khachhang_data if k['makhachhang'] == selected_item_id), None)
        if not kh: return
        set_form_state('normal')
        entry_vars["Mã KH:"].delete(0, tk.END)
        entry_vars["Mã KH:"].insert(0, kh['makhachhang'])
        entry_vars["Tên KH:"].delete(0, tk.END)
        entry_vars["Tên KH:"].insert(0, kh['tenkhachhang'])
        entry_vars["Địa chỉ:"].delete(0, tk.END)
        entry_vars["Địa chỉ:"].insert(0, kh['diachikhachhang'] or "")
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
            cursor.execute("SELECT * FROM quanlykhachhang")
            khachhang_data.clear()
            khachhang_data.extend(cursor.fetchall())
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
        refresh_tree()
        clear_entries()

    load_data()
