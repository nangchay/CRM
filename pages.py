import streamlit as st
from auth import login, logout
from streamlit_navigation_bar import st_navbar

def login_page():
    st.title("Đăng nhập")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Mật khẩu", type="password", key="login_password")
    
    if st.button("Đăng nhập"):
        if login(email, password):
            st.success("Đăng nhập thành công!")
            st.rerun()




def main_page():
    st.title("Trang chính")
    st.write("Chào mừng đến với ứng dụng CRM LỤC THỦY!")
    st.info("Dev @nguyenngothuong")
    
    st.text_area("Nhập suy nghĩ của bạn!")
    
    
    with st.popover("Đăng xuất"):
        if st.button("Xác nhận"):
            logout()
            st.success("Đăng xuất thành công!")
            login_page()
            st.rerun()
def note():
    st.title("Ghi chú")
    
    st.header("1. Nội dung cập nhật")
    st.info("Cập nhật: 07/08/2024")
    st.write("1. Thêm tính năng bắt buộc chọn người lập đơn hàng")
    st.write("2. Yêu cầu điền đầy đủ thông tin địa chỉ trước khi lưu đơn hàng")
    st.write("---")

    st.info("Cập nhật: 04/08/2024.")
    st.write("1. Làm sạch dữ liệu đầu vào - khi thêm thông tin khách hàng mới")
    st.write("2. Thêm check trùng số điện thoại trước khi nhập vào -> hiển thị thông báo")
    st.write("3. Tối ưu hệ thống!")
    st.write("---")
    
    st.info("Cập nhật: 29/06/2024.")
    st.write("1. Thêm thanh navigation bar cho dễ theo dõi tab")
    st.write("2. Thêm tài khoản và mật khẩu cho từng user, log lại lịch sử đăng nhập và thao tác của user")
    st.write("---")
    
    st.info("Cập nhật: 19/06/2024.")
    st.write("1. Fix bug: không thể kết nối đến dữ liệu (lỗi hết hạn token)")
    st.write("2. Hoàn thiện tính năng login nhiều user - ghi lại user khi gửi dữ liệu (liên hệ admin để được cấp tài khoản)")
    st.write("---")
    
    st.info("Cập nhật: 16/06/2024.")
    st.write("1. Sửa các lỗi nhỏ")
    st.write("2. Thêm video hướng dẫn - sắp ra mắt")
    st.write("3. Thêm tính năng login nhiều user - ghi lại user khi gửi dữ liệu")
    st.write("---")

    st.info("Cập nhật: 10/06/2024.")
    st.write("1. Thêm form giống như form ở Larkbase")
    st.write("2. Chỉ hiển thị ra danh sách khách hàng đã 'chốt'")
    st.write("---")

    
    st.write("---")
    st.header("2. Kế hoạch cập nhật")
    st.write("Load dữ liệu nhanh hơn...")
    st.write("doing - fix lỗi ấn dấu + - tăng giảm số tiền.")

def help_page():
    st.title("Hướng dẫn sử dụng")
    st.write("Chào mừng đến với hướng dẫn sử dụng ứng dụng Quản lý Đơn hàng! Dưới đây là các bước chi tiết để sử dụng ứng dụng hiệu quả.")

    st.header("1. Đăng nhập")
    st.write("- Nhập email và mật khẩu của bạn vào các trường tương ứng.")
    st.write("- Nhấn nút 'Đăng nhập' để truy cập vào hệ thống.")
    st.write("- Nếu bạn quên mật khẩu, vui lòng liên hệ với quản trị viên để được hỗ trợ.")

    st.header("2. Quản lý Thông tin Khách hàng")
    st.write("- Bạn có thể chọn 'Thêm mới' hoặc 'Chọn từ danh sách' để nhập thông tin khách hàng.")
    st.write("- Khi thêm mới, điền đầy đủ thông tin như tên, số điện thoại, nguồn khách hàng.")
    st.write("- Khi chọn từ danh sách, hệ thống sẽ tự động điền thông tin khách hàng đã có.")

    st.header("3. Tạo Đơn hàng")
    st.write("- Chọn 'Hình thức đơn hàng', 'Hình thức thanh toán', và 'Tình trạng cọc'.")
    st.write("- Nhấn 'Thêm sản phẩm' để bắt đầu thêm các mặt hàng vào đơn.")
    st.write("- Với mỗi sản phẩm:")
    st.write("  + Chọn 'Mã vật tư' từ danh sách.")
    st.write("  + Nhập số lượng và điều chỉnh đơn giá nếu cần.")
    st.write("  + Thêm ghi chú cho sản phẩm nếu có.")
    st.write("- Hệ thống sẽ tự động tính toán tổng tiền cho mỗi sản phẩm và toàn bộ đơn hàng.")

    st.header("4. Thông tin Bổ sung")
    st.write("- Nhập số tiền cọc, phí vận chuyển, phí công thợ và phụ thu (nếu có).")
    st.write("- Chọn thời gian yêu cầu thực hiện đơn hàng.")
    st.write("- Nhập số lượng m2 yêu cầu giữ và các yêu cầu khác từ khách hàng.")
    st.write("- Tải lên sơ đồ nhà khách và hình ảnh mặt bằng (nếu có).")
    st.write("- Điền địa chỉ đơn hàng và ghi chú bổ sung.")

    st.header("5. Lưu Đơn hàng")
    st.write("- Kiểm tra lại tất cả thông tin đã nhập.")
    st.write("- Nhấn nút 'Lưu đơn hàng' để hoàn tất.")
    st.write("- Hệ thống sẽ xác nhận việc lưu đơn hàng thành công và cung cấp link để xem chi tiết.")

    st.header("6. Xem và Quản lý Đơn hàng")
    st.write("- Sau khi lưu, bạn có thể xem lại đơn hàng trong phần quản lý đơn hàng.")
    st.write("- Tại đây, bạn có thể theo dõi trạng thái, chỉnh sửa hoặc hủy đơn hàng nếu cần.")

    st.header("7. Đăng xuất")
    st.write("- Để đăng xuất, nhấn vào nút 'Đăng xuất' ở góc trên cùng bên phải.")
    st.write("- Xác nhận đăng xuất bằng cách nhấn nút 'Xác nhận' trong cửa sổ pop-up.")

    st.header("Lưu ý quan trọng")
    st.warning("Để đảm bảo ứng dụng hoạt động ổn định và tránh lỗi, vui lòng không tự ý chỉnh sửa tên cột trong Larkbase. Các tên cột cần được giữ nguyên theo cấu trúc hiện tại.")

    st.header("Báo lỗi và Hỗ trợ")
    st.write("Nếu bạn gặp bất kỳ lỗi nào trong quá trình sử dụng ứng dụng, vui lòng thực hiện các bước sau:")
    st.write("1. Chụp ảnh màn hình lỗi (nếu có).")
    st.write("2. Ghi lại các bước đã thực hiện dẫn đến lỗi.")
    st.write("3. Gửi email báo lỗi đến địa chỉ:")
    st.code("report@nguyenngothuong.com")
    st.write("4. Trong email, hãy mô tả chi tiết lỗi bạn gặp phải và đính kèm ảnh chụp màn hình.")
    
    st.write("Đội ngũ hỗ trợ kỹ thuật sẽ phản hồi trong thời gian sớm nhất để giúp bạn giải quyết vấn đề.")

    st.header("Video hướng dẫn")
    st.write("Để hiểu rõ hơn về cách sử dụng ứng dụng, vui lòng xem video hướng dẫn sau:")
    st.video("https://youtu.be/xXZqcCmn17M?si=xsONGd9kyyGAwQcT")