import streamlit as st
from supabase import create_client

# Khởi tạo Supabase client
@st.cache_resource
def init_connection():
    url = st.secrets["supabase"]["SUPABASE_URL"]
    key = st.secrets["supabase"]["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

def check_logged_in():
    return st.session_state.logged_in

def login(email, password):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if res:
            st.session_state.logged_in = True
            st.session_state.user = email
            st.write(res)
            return True
    except Exception as e:
        st.error(f"Đăng nhập thất bại: {e}")
    return False


def signup(email, password):
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        st.write(res)
        if res:
            user = res.get("user")
            if user:
                st.success("Đăng ký thành công! Vui lòng kiểm tra email để xác minh tài khoản.")
                return True
            else:
                st.error("Đăng ký thất bại. Vui lòng thử lại sau.")
        else:
            error_message = res.get("error_description")
            if error_message:
                if "already registered" in error_message:
                    st.error("Email đã được sử dụng. Vui lòng sử dụng một email khác.")
                elif "password is too weak" in error_message:
                    st.error("Mật khẩu quá yếu. Vui lòng sử dụng mật khẩu mạnh hơn.")
                else:
                    st.error(f"Đăng ký thất bại: {error_message}")
            else:
                st.error("Đăng ký thất bại. Vui lòng thử lại sau.")
    except Exception as e:
        st.error(f"Đăng ký thất bại: {e}")



def logout():
    try:
        res = supabase.auth.sign_out()
        if res:
            st.session_state.logged_in = False
            st.write("st.session_state.logged_in: ", st.session_state.logged_in)
        else:
            st.session_state.logged_in = False
            
    except Exception as e:
        st.error(f"Lỗi: {e}")