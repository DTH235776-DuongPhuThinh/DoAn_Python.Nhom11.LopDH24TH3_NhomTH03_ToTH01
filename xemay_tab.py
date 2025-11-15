import tkinter as tk
from tkinter import ttk, messagebox
from db_connect import connect_db  # Hàm trả về kết nối MySQL

def create_view(parent_tab, xemay_data):
    """
    Tạo giao diện quản lý Xe máy.
    """
    # --- Biến nội bộ ---
    current_mode = None
    selected_item_id = None

    # ==========================
    # 1. FORM NHẬP LIỆU
    # ==========================
    form_frame = ttk.LabelFrame(parent_tab, text="Thông tin Xe máy")
    form_frame.pack(fill="x", padx=10, pady=10)

    labels = ["Mã Xe:", "Tên Xe:", "Hãng SX:", "Giá:", "Số lượng:"]
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
        columns=("maxe", "tenxe", "hangsx", "gia", "soluong"),
        show="headings",
        yscrollcommand=tree_scroll_y.set,
        xscrollcommand=tree_scroll_x.set
    )
    tree_scroll_y.config(command=tree.yview)
    tree_scroll_x.config(command=tree.xview)

    tree.heading("maxe", text="Mã Xe")
    tree.heading("tenxe", text="Tên Xe")
    tree.heading("hangsx", text="Hãng SX")
    tree.heading("gia", text="Giá")
    tree.heading("soluong", text="Số lượng")

    tree.column("maxe", width=80, anchor="w")
    tree.column("tenxe", width=150, anchor="w")
    tree.column("hangsx", width=100, anchor="w")
    tree.column("gia", width=100, anchor="e")
    tree.column("soluong", width=80, anchor="c")
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
        for xe in xemay_data:
            tree.insert("", tk.END, iid=xe['maxemay'], values=(
                xe['maxemay'], xe['tenxemay'], xe['hangsx'], xe['gia'], xe['soluong']
            ))

    def on_add():
        nonlocal current_mode
        clear_entries()
        current_mode = 'add'
        set_form_state('normal')
        entry_vars["Mã Xe:"].focus()

    def on_edit():
        nonlocal current_mode, selected_item_id
        if not selected_item_id:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn xe để sửa.")
            return
        current_mode = 'edit'
        set_form_state('normal')
        entry_vars["Mã Xe:"].config(state='disabled')  # không được sửa mã
        entry_vars["Tên Xe:"].focus()

    def on_save():
        nonlocal current_mode, selected_item_id
        maxe = entry_vars["Mã Xe:"].get().strip()
        tenxe = entry_vars["Tên Xe:"].get().strip()
        hangsx = entry_vars["Hãng SX:"].get().strip() or None
        try:
            gia = float(entry_vars["Giá:"].get().strip()) if entry_vars["Giá:"].get().strip() else None
        except ValueError:
            messagebox.showerror("Lỗi nhập liệu", "Giá phải là số hợp lệ!")
            return
        try:
            soluong = int(entry_vars["Số lượng:"].get().strip()) if entry_vars["Số lượng:"].get().strip() else 0
        except ValueError:
            messagebox.showerror("Lỗi nhập liệu", "Số lượng phải là số nguyên!")
            return

        new_data_dict = {'maxemay': maxe, 'tenxemay': tenxe, 'hangsx': hangsx, 'gia': gia, 'soluong': soluong}

        try:
            conn = connect_db()
            cursor = conn.cursor(dictionary=True)

            if current_mode == 'add':
                if any(xe['maxemay'] == maxe for xe in xemay_data):
                    messagebox.showerror("Lỗi", "Mã Xe đã tồn tại!")
                    return
                sql = "INSERT INTO quanlyxemay (maxemay, tenxemay, hangsx, gia, soluong) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (maxe, tenxe, hangsx, gia, soluong))
                xemay_data.append(new_data_dict)
                messagebox.showinfo("Thành công", f"Đã thêm xe {maxe}")

            elif current_mode == 'edit':
                sql = "UPDATE quanlyxemay SET tenxemay=%s, hangsx=%s, gia=%s, soluong=%s WHERE maxemay=%s"
                cursor.execute(sql, (tenxe, hangsx, gia, soluong, maxe))
                for i, xe in enumerate(xemay_data):
                    if xe['maxemay'] == selected_item_id:
                        xemay_data[i] = new_data_dict
                        break
                messagebox.showinfo("Thành công", f"Đã cập nhật xe {maxe}")

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
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn xe để xóa.")
            return
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa xe {selected_item_id}?"):
            return
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM quanlyxemay WHERE maxemay=%s", (selected_item_id,))
            conn.commit()
            xemay_data[:] = [xe for xe in xemay_data if xe['maxemay'] != selected_item_id]
            messagebox.showinfo("Thành công", "Đã xóa xe!")
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
        xe = next((x for x in xemay_data if x['maxemay'] == selected_item_id), None)
        if not xe: return
        set_form_state('normal')
        entry_vars["Mã Xe:"].delete(0, tk.END)
        entry_vars["Mã Xe:"].insert(0, xe['maxemay'])
        entry_vars["Tên Xe:"].delete(0, tk.END)
        entry_vars["Tên Xe:"].insert(0, xe['tenxemay'])
        entry_vars["Hãng SX:"].delete(0, tk.END)
        entry_vars["Hãng SX:"].insert(0, xe['hangsx'] or "")
        entry_vars["Giá:"].delete(0, tk.END)
        entry_vars["Giá:"].insert(0, xe['gia'] if xe['gia'] is not None else "")
        entry_vars["Số lượng:"].delete(0, tk.END)
        entry_vars["Số lượng:"].insert(0, xe['soluong'])
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
            cursor.execute("SELECT * FROM quanlyxemay")
            xemay_data.clear()
            xemay_data.extend(cursor.fetchall())
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
        refresh_tree()
        clear_entries()

    load_data()
