import tkinter as tk
from tkinter import messagebox
from db_connect import connect_db, center_window
import xemay_tab
import nhanvien_tab
import khachhang_tab
import tonkho_tab

def open_main_window():

    # ===== 1. CỬA SỔ CHÍNH =====
    root = tk.Tk()
    root.title("Hệ Thống Quản Lý Xe Máy")
    center_window(root, 1000, 600)
    root.resizable(False, False)

    main_bg = "white"
    sidebar_bg = "#D6EAF8"
    root.config(bg=main_bg)

    # ===== 2. LOAD DỮ LIỆU TỪ MYSQL (LOAD dữ liệu liên quan cho combobox) =====
    # Chúng ta vẫn cần load các bảng liên quan (Xe máy, NV, KH) một lần
    # để truyền cho Combobox trong tab Tồn Kho.
    xemay_data, nhanvien_data, khachhang_data = [], [], []

    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM quanlyxemay")
        xemay_data.extend(cursor.fetchall())

        cursor.execute("SELECT * FROM quanlynhanvien")
        nhanvien_data.extend(cursor.fetchall())

        cursor.execute("SELECT * FROM quanlykhachhang")
        khachhang_data.extend(cursor.fetchall())
        
        # Không cần load tonkho_data ở đây, vì nó sẽ được load trong tonkho_tab

        conn.close()
    except Exception as e:
        messagebox.showerror("Lỗi CSDL", f"Không đọc được dữ liệu khởi tạo.\n{e}")
        root.destroy()
        return

    # ===== 3. FRAME SIDEBAR =====
    frame_sidebar = tk.Frame(root, bg=sidebar_bg, padx=10, pady=10)
    frame_sidebar.pack(side=tk.LEFT, fill=tk.Y)
    frame_sidebar.config(width=220)
    frame_sidebar.pack_propagate(False)

    # ===== 4. FRAME CHÍNH =====
    main_frame = tk.Frame(root, bg=main_bg)
    main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    # ===== 5. HÀM XÓA VIEW =====
    def clear_main_frame():
        for widget in main_frame.winfo_children():
            widget.destroy()

    # ===== 6. HÀM HIỂN THỊ VIEW (CHỈNH SỬA) =====
    def show_trangchu_view():
        clear_main_frame()
        tk.Label(main_frame, text="TRANG CHỦ HỆ THỐNG",
                 font=("Arial", 28, "bold"), bg=main_bg).pack(pady=50)
        tk.Label(main_frame, text="Hệ thống Quản lý Xe Máy",
                 font=("Arial", 20), bg=main_bg).pack()

    def show_xemay_view():
        clear_main_frame()
        xemay_tab.create_view(main_frame, xemay_data)

    def show_nhanvien_view():
        clear_main_frame()
        nhanvien_tab.create_view(main_frame, nhanvien_data)

    def show_khachhang_view():
        clear_main_frame()
        khachhang_tab.create_view(main_frame, khachhang_data)

    def show_tonkho_view():
        clear_main_frame()
        tonkho_tab.create_view(main_frame, xemay_data, nhanvien_data, khachhang_data)

    # ===== 7. NÚT SIDEBAR =====
    # Màu xanh lá cây cho các nút quản lý
    green_button_bg = "#4CAF50"  # Một mã màu xanh lá cây phổ biến (Material Design Green 500)
    button_fg = "white"          # Màu chữ trắng
    
    buttons_info = [
        ("Trang chủ", show_trangchu_view),
        ("Quản lý Xe Máy", show_xemay_view),
        ("Quản lý Nhân Viên", show_nhanvien_view),
        ("Quản lý Khách Hàng", show_khachhang_view),
        ("Quản lý Tồn Kho", show_tonkho_view),
    ]

    for text, func in buttons_info:
        tk.Button(frame_sidebar, text=text, width=22, height=2, 
                  bg=green_button_bg, fg=button_fg, # Đã thay đổi màu nền và màu chữ
                  font=("Arial", 11, "bold"), command=func).pack(pady=6)

    # Nút thoát (giữ nguyên màu đỏ để dễ phân biệt)
    tk.Button(frame_sidebar, text="Thoát", width=22, height=2, bg="red", fg="white",
              font=("Arial", 11, "bold"), command=root.destroy).pack(side="bottom", pady=10)

    # ===== 8. HIỂN THỊ TRANG CHỦ LÚC MỚI MỞ =====
    show_trangchu_view()
    root.mainloop()


# ===== 9. CHẠY CHƯƠNG TRÌNH =====
if __name__ == "__main__":
    open_main_window()