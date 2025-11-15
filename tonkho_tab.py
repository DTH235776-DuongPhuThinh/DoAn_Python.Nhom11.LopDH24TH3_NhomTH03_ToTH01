import tkinter as tk
from tkinter import ttk, messagebox
from db_connect import connect_db 

def create_view(parent_tab, xemay_data, nhanvien_data, khachhang_data):
    """
    Tạo giao diện quản lý Tồn kho với 4 nút chức năng: Thêm, Lưu, Bỏ qua, Thoát.
    Nút Lưu kiêm nhiệm cả Thêm mới và Sửa.
    """
    
    # Biến trạng thái
    current_mode = None       # 'add' (Thêm mới), 'edit' (Sửa dòng đã chọn)
    selected_maxemay = None   # Mã xe máy của dòng đang được chọn (chỉ dùng khi mode='edit')

    # Dữ liệu combobox (Mã - Tên)
    xe_may_values = [f"{x['maxemay']} - {x['tenxemay']}" for x in xemay_data]
    
    # ==========================
    # 1. FORM NHẬP LIỆU
    # ==========================
    form_frame = ttk.LabelFrame(parent_tab, text="Thông tin Tồn kho")
    form_frame.pack(fill="x", padx=10, pady=10)

    # Khai báo biến
    cb_xemay = ttk.Combobox(form_frame, width=37, state="readonly")
    entry_soluong = ttk.Entry(form_frame, width=40)
    
    # Grid các widget
    ttk.Label(form_frame, text="Xe máy:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    cb_xemay['values'] = xe_may_values
    cb_xemay.grid(row=0, column=1, padx=5, pady=5)
    
    ttk.Label(form_frame, text="Số lượng tồn:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    entry_soluong.grid(row=1, column=1, padx=5, pady=5)
    
    # ==========================
    # 2. TREEVIEW HIỂN THỊ
    # ==========================
    tree_frame = ttk.Frame(parent_tab)
    tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

    tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
    tree_scroll_y.pack(side="right", fill="y")
    
    tree = ttk.Treeview(
        tree_frame,
        columns=("maxemay","soluongton","ngaycapnhat"),
        show="headings",
        yscrollcommand=tree_scroll_y.set
    )
    tree_scroll_y.config(command=tree.yview)

    headings = ["Mã Xe máy", "Số lượng Tồn", "Ngày Cập nhật"]
    col_widths = [150, 150, 200]
    for col, text, width in zip(tree['columns'], headings, col_widths):
        tree.heading(col, text=text)
        tree.column(col, width=width, anchor="w")
    tree.pack(fill="both", expand=True)

    # ==========================
    # 3. HÀM NỘI BỘ VÀ LOGIC
    # ==========================
    
    def update_control_state():
        """Cập nhật trạng thái của Combobox và nút Lưu dựa trên current_mode."""
        if current_mode == 'add':
            cb_xemay.config(state="readonly")
            btn_luu.config(state="normal", text="Lưu (Thêm)")
        elif current_mode == 'edit':
            cb_xemay.config(state="disabled") # KHÔNG cho phép sửa Mã xe khi cập nhật
            btn_luu.config(state="normal", text="Lưu (Sửa)")
        else: # Chế độ rảnh (None)
            cb_xemay.config(state="readonly")
            btn_luu.config(state="disabled", text="Lưu")

    def clear_entries():
        """Xóa dữ liệu trên form và reset chế độ."""
        nonlocal current_mode, selected_maxemay
        current_mode = None
        selected_maxemay = None
        cb_xemay.set('')
        entry_soluong.delete(0, tk.END)
        if tree.selection():
            tree.selection_remove(tree.selection())
        update_control_state()

    def refresh_tree(records):
        """Đổ dữ liệu từ CSDL vào Treeview."""
        tree.delete(*tree.get_children())
        xemay_map = {x['maxemay']: f"{x['maxemay']} - {x['tenxemay']}" for x in xemay_data}
        
        for tk_data in records:
            maxemay_display = xemay_map.get(tk_data['maxemay'], tk_data['maxemay'])
            
            tree.insert("", tk.END, iid=tk_data['maxemay'], values=(
                maxemay_display, 
                tk_data['soluongton'], 
                tk_data['ngaycapnhat']
            ))

    def load_data():
        """Tải dữ liệu tồn kho từ CSDL và hiển thị."""
        records = []
        try:
            conn = connect_db()
            cursor = conn.cursor(dictionary=True) 
            sql_select = "SELECT maxemay, soluongton, ngaycapnhat FROM tonkho ORDER BY maxemay DESC"
            cursor.execute(sql_select)
            records = cursor.fetchall()
            refresh_tree(records) 
        except Exception as e:
            messagebox.showerror("Lỗi CSDL", f"Lỗi khi tải dữ liệu tồn kho: {e}")
        finally:
            if 'conn' in locals() and conn and conn.is_connected():
                cursor.close()
                conn.close()
                
    def on_tree_select(event):
        """Xử lý khi click vào một dòng để chuyển sang chế độ Sửa."""
        nonlocal current_mode, selected_maxemay
        selected_items = tree.selection()
        
        if not selected_items:
            clear_entries()
            return
            
        item = selected_items[0]
        values = tree.item(item, 'values')
        
        # Thiết lập chế độ Sửa
        selected_maxemay = values[0].split(" - ")[0] 
        current_mode = 'edit' 
        
        # Xóa dữ liệu cũ trên form và điền dữ liệu mới
        clear_entries()
        tree.selection_set(item)
        
        # Điền dữ liệu hiển thị 
        cb_xemay.set(values[0]) # Mã - Tên
        entry_soluong.insert(0, values[1]) # Số lượng tồn
        
        update_control_state() # Kích hoạt nút Lưu (Sửa)

    # Gắn sự kiện click vào Treeview
    tree.bind('<<TreeviewSelect>>', on_tree_select)


    # ==========================
    # 4. HÀM XỬ LÝ SỰ KIỆN NÚT
    # ==========================

    def on_add():
        """Chuyển sang chế độ Thêm mới."""
        nonlocal current_mode
        clear_entries()
        current_mode = 'add'
        cb_xemay.set("") # Bắt buộc người dùng chọn lại xe
        update_control_state()
        messagebox.showinfo("Chế độ", "Đã chuyển sang chế độ **Thêm mới**. Vui lòng chọn xe và nhập số lượng tồn ban đầu.")

    def on_save():
        """Thực hiện Lưu (Thêm mới/Cập nhật) dữ liệu vào CSDL."""
        nonlocal current_mode, selected_maxemay
        
        # 1. Kiểm tra chế độ và lấy Mã xe
        if current_mode not in ['add', 'edit']:
            messagebox.showwarning("Cảnh báo", "Vui lòng bấm **'Thêm'** hoặc **click chọn một dòng** để Sửa.")
            return

        # Lấy Mã xe dựa trên chế độ
        if current_mode == 'add':
            maxemay_key = cb_xemay.get().split(" - ")[0] if cb_xemay.get() else None
        else: # current_mode == 'edit'
            maxemay_key = selected_maxemay
        
        # 2. Kiểm tra dữ liệu
        try:
            soluongton = int(entry_soluong.get())
            if soluongton < 0: raise ValueError
        except ValueError:
            messagebox.showerror("Lỗi", "Số lượng tồn phải là số nguyên không âm!")
            return
            
        if not maxemay_key:
            messagebox.showerror("Lỗi", "Vui lòng chọn Xe máy.")
            return

        # 3. Thực hiện CSDL
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            if current_mode == 'add':
                # THÊM MỚI
                sql = "INSERT INTO tonkho (maxemay, soluongton) VALUES (%s,%s)"
                data = (maxemay_key, soluongton)
                cursor.execute(sql, data)
                messagebox.showinfo("Thành công", f"Đã thêm dữ liệu tồn kho ban đầu cho {maxemay_key}!")
                
            elif current_mode == 'edit':
                # CẬP NHẬT
                sql = "UPDATE tonkho SET soluongton=%s, ngaycapnhat=CURRENT_TIMESTAMP WHERE maxemay=%s"
                data = (soluongton, selected_maxemay) 
                cursor.execute(sql, data)
                messagebox.showinfo("Thành công", f"Đã cập nhật số lượng tồn kho cho {selected_maxemay}!")
                
            conn.commit() 
            load_data() # Tải lại dữ liệu
            
        except Exception as e:
            # Xử lý lỗi trùng khóa khi cố gắng thêm mới
            if "1062" in str(e) and current_mode == 'add':
                messagebox.showerror("Lỗi", "Mã Xe Máy này đã có trong danh sách Tồn Kho. Vui lòng **click vào dòng đó** để Sửa.")
            else:
                messagebox.showerror("Lỗi CSDL", f"Lỗi khi lưu dữ liệu: {e}")
        finally:
            if 'conn' in locals() and conn and conn.is_connected():
                cursor.close()
                conn.close()
            
        clear_entries() 

    def on_exit():
        """Hàm Thoát không đóng tab mà chỉ thông báo."""
        messagebox.showinfo("Thông báo", "Chức năng Thoát sẽ được xử lý bởi cửa sổ chính.")


    # ==========================
    # 5. NÚT VÀ KHỞI TẠO
    # ==========================
    button_frame = tk.Frame(parent_tab)
    button_frame.pack(pady=10, fill="x")

    # Chỉ hiển thị 4 nút: Thêm, Lưu, Bỏ qua, Thoát
    btn_them = ttk.Button(button_frame, text="Thêm", command=on_add)
    btn_luu = ttk.Button(button_frame, text="Lưu", command=on_save)
    btn_boqua = ttk.Button(button_frame, text="Bỏ qua", command=clear_entries)
    btn_thoat = ttk.Button(button_frame, text="Thoát", command=on_exit)

    for btn in [btn_them, btn_luu, btn_boqua, btn_thoat]:
        btn.pack(side=tk.LEFT, padx=5, expand=True)
    
    # Khởi tạo: Tải dữ liệu lần đầu khi tab được mở
    load_data()
    clear_entries()