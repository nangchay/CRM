import streamlit as st
from streamlit_navigation_bar import st_navbar
from pages import login_page,  help_page, note
from main_page import main_page




# Khởi tạo session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Thiết lập các trang
pages = ["Đăng nhập","Hướng dẫn sử dụng", "Ghi chú"]

# Kiểm tra trạng thái đăng nhập
if not st.session_state.logged_in:
    page = st_navbar(pages)
    if page == "Đăng nhập":
        login_page()
    elif page == "Hướng dẫn sử dụng":
        help_page()
    elif page == "Ghi chú":
        note()
else:
    pages = ["Trang chính", "Hướng dẫn sử dụng", "Ghi chú"]
    page = st_navbar(pages)
    if page == "Trang chính":
        main_page() 
    elif page == "Hướng dẫn sử dụng":
        help_page()
    elif page == "Ghi chú":
        note()