import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from main import open_main_window     # Mở giao diện chính quản lý xe máy
from db_connect import center_window  # Hàm căn giữa cửa sổ


def check_login():
    username = entry_user.get()
    password = entry_pass.get()

    if username == "thinhlegend" and password == "248569":
        login_window.destroy()
        open_main_window()
    else:
        messagebox.showerror("Lỗi đăng nhập", "Sai tên đăng nhập hoặc mật khẩu!")


# ---------------- CỬA SỔ ĐĂNG NHẬP ----------------
login_window = tk.Tk()
login_window.title("Đăng Nhập - Hệ thống Quản Lý Xe Máy")
login_window.geometry("800x600")
center_window(login_window, 800, 600)
login_window.resizable(False, False)

# ---------------- ẢNH NỀN ----------------
try:
    bg_image = Image.open("anh/Background.jpg")  # đổi hình xe máy
    bg_image = bg_image.resize((800, 600), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)

    bg_label = tk.Label(login_window, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except Exception as e:
    print(f"Lỗi tải ảnh nền: {e}. Dùng nền mặc định.")
    login_window.config(bg="#F0F0F0")

# ---------------- KHUNG ĐĂNG NHẬP ----------------
login_frame = tk.Frame(login_window, bg="white", relief="solid", bd=1)
login_frame.place(relx=0.5, rely=0.5, anchor="center", width=350, height=400)

# ---------------- LOGO ----------------
try:
    logo_image = Image.open("anh/logo.jpg")  # đổi logo cửa hàng xe máy
    logo_image = logo_image.resize((100, 100), Image.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_image)

    logo_label = tk.Label(login_frame, image=logo_photo, bg="white")
    logo_label.pack(pady=(20, 10))
except Exception as e:
    print(f"Lỗi tải logo: {e}")
    logo_label = tk.Label(login_frame, text="LOGO", bg="white")
    logo_label.pack(pady=(20, 10))

# ---------------- TIÊU ĐỀ ----------------
title_label = tk.Label(
    login_frame,
    text="HỆ THỐNG QUẢN LÝ XE MÁY",
    font=("Times New Roman", 16, "bold"),
    bg="white"
)
title_label.pack(pady=10)

# ---------------- USERNAME ----------------
user_label = tk.Label(login_frame, text="Tên đăng nhập", font=("Times New Roman", 12), bg="white")
user_label.pack(pady=(10, 5))

entry_user = tk.Entry(login_frame, font=("Times New Roman", 12), width=30)
entry_user.pack()

# ---------------- PASSWORD ----------------
pass_label = tk.Label(login_frame, text="Mật khẩu", font=("Times New Roman", 12), bg="white")
pass_label.pack(pady=(10, 5))

entry_pass = tk.Entry(login_frame, font=("Times New Roman", 12), width=30, show="*")
entry_pass.pack()

# ---------------- BUTTON LOGIN ----------------
login_button = tk.Button(
    login_frame, text="Đăng nhập",
    font=("Times New Roman", 12, "bold"),
    width=28,
    command=check_login,
    bg="#000000",
    fg="white"
)
login_button.pack(pady=20)

login_window.mainloop()
