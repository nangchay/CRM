# 1. Imports
import streamlit as st
import pandas as pd
import uuid
import json
import datetime
from lark_connector import connect_to_larkbase, get_larkbase_data_v4, get_tenant_access_token, get_list_table, get_list_view, create_a_record, create_records
import unidecode
import json
import requests
from requests.auth import HTTPBasicAuth
import base64
import os
from auth import login,  logout, check_logged_in 
from pages import login_page, help_page, note
import re
from address_selector import address_selector


# 2. Constants (nếu có)
# Ví dụ: URL_WEBHOOK = "https://your-webhook-url.com"

# 3. Các hàm tiện ích và hàm phụ trợ
def format_name(name):
    # Xóa dấu cách thừa và viết hoa chữ cái đầu của mỗi từ
    formatted_name = ' '.join(word.capitalize() for word in name.split())
    return formatted_name

def format_phone(phone):
    # Xóa tất cả các ký tự không phải số
    phone = re.sub(r'\D', '', phone)
    # Kiểm tra độ dài số điện thoại
    if len(phone) == 10 and phone.startswith('0'):
        return phone
    elif len(phone) == 11 and phone.startswith('84'):
        return '0' + phone[2:]
    else:
        return None






if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None



def main_page():   
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user = None

    if not st.session_state.logged_in:
        st.write("Vui lòng đăng nhập để tiếp tục")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Đăng nhập", type="login_primary"):
            if login(email, password):
                st.success("Đăng nhập thành công!")
                # st.rerun()
                
            else:
                st.error("Sai tài khoản hoặc mật khẩu")
    else:
        lark_app_id = st.secrets["streamlit"]["lark_app_id"]
        lark_app_secret = st.secrets["streamlit"]["lark_app_secret"]
        lark_app_token = st.secrets["streamlit"]["lark_app_token"]

        table_customer_id = st.secrets["streamlit"]["table_customer_id"]
        table_product_id = st.secrets["streamlit"]["table_product_id"]
        table_sale_id = st.secrets["streamlit"]["table_sale"]
        
        def get_larkbase_table_data(table_id, payload=None):
            return get_larkbase_data_v4(lark_app_token, table_id, payload=payload,  app_id=lark_app_id, app_secret=lark_app_secret)

        def save_df_to_json(df, file_name):
            with open(file_name, "w", encoding="utf-8") as file:
                json.dump(df.to_dict(orient="records"), file, ensure_ascii=False, indent=4)
                
        table_ids = [table_customer_id, table_product_id, table_sale_id]
        table_names = ["table_customer", "table_product","table_sale"]
        dfs = {}
        
        # Tạo một phần tử empty để hiển thị thông báo
        info_placeholder = st.empty()

        # Hiển thị thông báo
        info_placeholder.info("Đang kết nối dữ liệu, vui lòng chờ xíu nhen 😉")

        try:
            for table_id, table_name in zip(table_ids, table_names):
                if table_name == "table_customer":
                    payload = {
                        "filter": {
                            "conditions": [
                                {
                                    "field_name": "Tình trạng",
                                    "operator": "is",
                                    "value": [
                                        "Chốt"
                                    ]
                                }
                            ],
                            "conjunction": "and"
                        }
                    }
                    data = get_larkbase_table_data(table_id, payload)
                elif table_name == "table_sale":
                    payload = {
                        "filter": {
                            "conditions": [
                                {
                                    "field_name": "Trạng thái làm việc",
                                    "operator": "is",
                                    "value": [
                                        "Đang làm việc"
                                    ]
                                }
                            ],
                            "conjunction": "and"
                        }
                    }
                    data = get_larkbase_table_data(table_id, payload)
                else:
                    data = get_larkbase_table_data(table_id)
                
                if data is not None:
                    dfs[table_name] = pd.DataFrame(data)
                else:
                    raise Exception(f"Kết nối đến bảng {table_name} thất bại 😥")

            if len(dfs) == len(table_names):
                # Xóa thông báo "Đang kết nối dữ liệu"
                info_placeholder.empty()
                st.success("Kết nối và lấy dữ liệu từ Larkbase thành công 🤗")
            else:
                raise Exception("Kết nối và lấy dữ liệu từ Larkbase thất bại 😥")

        except Exception as e:
            # Xóa thông báo "Đang kết nối dữ liệu"
            info_placeholder.empty()
            st.error(str(e))
            st.info("Vui lòng F5 lại trang/xóa cache và thử lại 🤗")
            return


        # Đọc dữ liệu khách hàng từ DataFrame
        customer_data = dfs["table_customer"].to_dict('records')
        product_data = dfs["table_product"].to_dict('records')
        sale_data = dfs["table_sale"].to_dict('records')
        
        usernames = [""] + [sale['fields'].get('Tên đăng nhập', [{'text': ''}])[0]['text'] for sale in sale_data]
        
        # Trong phần form nhập liệu
        st.subheader("Thông tin người lập đơn")
        selected_username = st.selectbox("Chọn tên đăng nhập", usernames, index=0)
        if selected_username:
            selected_sale = next((sale for sale in sale_data if sale['fields'].get('Tên đăng nhập', [{'text': ''}])[0]['text'] == selected_username), None)
            if selected_sale:
                lark_account = selected_sale['fields'].get('Tài khoản lark', [{}])[0]
                st.write(f"Xin chào {lark_account.get('name', '')}")
        else:
            st.warning("Vui lòng chọn tên đăng nhập")


        # Tạo danh sách Nguồn khách hàng
        customer_source_list = list(set([customer['fields'].get('Nguồn khách hàng', '') for customer in customer_data if customer['fields'].get('Nguồn khách hàng', '')]))



        # Sắp xếp danh sách khách hàng theo ngày tạo (mới nhất lên trên)
        sorted_customer_data = sorted(customer_data, key=lambda x: x['fields'].get('Thời gian tạo', 0), reverse=True)
        # Tạo danh sách khách hàng để hiển thị trong dropdown
        # customer_list2 = [customer['fields'].get('ID khách hàng', {'value': [{'text': ''}]})['value'][0]['text'] for customer in sorted_customer_data]
        # st.write(customer_list)
        
        # Modify the customer_list creation
        st.session_state.customer_list = []
        for customer in sorted_customer_data:
            customer_id = customer['fields'].get('ID khách hàng', {'value': [{'text': ''}]})['value'][0]['text']
            parts = customer_id.split('-')
            if len(parts) >= 2:
                name = parts[0].strip()
                phone = parts[-1].strip()
                if len(phone) >= 6:
                    masked_phone = f"{phone[:3]}{'*' * (len(phone) - 6)}{phone[-3:]}"
                else:
                    masked_phone = '*' * len(phone)
                st.session_state.customer_list.append(f"{name} - {masked_phone}")
            else:
                st.session_state.customer_list.append(customer_id)
        
                
            
        def check_existing_phone(formatted_phone, table_customer_id):
            payload_phone = {
                "field_names": ["Số điện thoại"],
                "filter": {
                    "conjunction": "and",
                    "conditions": [
                        {
                            "field_name": "Số điện thoại",
                            "operator": "is",
                            "value": [str(formatted_phone)]
                        }
                    ]
                }
            }
            data_list_phone = get_larkbase_table_data(table_customer_id, payload_phone)
            df_list_phone = pd.DataFrame(data_list_phone)
            customer_phone_data = df_list_phone.to_dict('records')
            
            existing_phone_numbers = [customer['fields'].get('Số điện thoại', '') for customer in customer_phone_data if customer['fields'].get('Số điện thoại')]
            
            return existing_phone_numbers, customer_phone_data
            
        
        

        
        # Form nhập thông tin khách hàng
        st.header("Thông tin khách hàng")
        

        # Tùy chọn thêm mới hoặc chọn khách hàng có5 sẵn
        customer_option = st.radio("Lựa chọn khách hàng", ("Thêm mới", "Chọn từ danh sách"))
        if customer_option == "Thêm mới":
            col1, col2, col3 = st.columns(3)
            
            with col1:
                customer_name = st.text_input("Tên khách hàng", placeholder="Nhập tên khách hàng...")
                if customer_name:
                    customer_name = format_name(customer_name)
                    st.write(f"Tên khách hàng: {customer_name}")
            
            with col2:
                customer_phone = st.text_input("Số điện thoại", placeholder="Nhập số điện thoại (VD: 0816226086)")
                if customer_phone:
                    formatted_phone = format_phone(customer_phone)
                    if formatted_phone:
                        st.write(f"Số điện thoại: {formatted_phone}")
                        info_placeholder = st.empty()
                        info_placeholder.info("Đang kiểm tra số điện thoại")
                        st.session_state.existing_phone_numbers, st.session_state.customer_phone_data = check_existing_phone(formatted_phone, table_customer_id)
                        # Kiểm tra xem số điện thoại đã tồn tại chưa
                        if formatted_phone in st.session_state.existing_phone_numbers:
                            info_placeholder.empty()
                            st.warning(f"Số điện thoại {formatted_phone} đã có trong thông tin khách hàng. Vui lòng kiểm tra lại.")
                        else:
                            info_placeholder.empty()
                            
                            st.success("Số điện thoại hợp lệ và chưa tồn tại trong hệ thống.")
                    else:
                        st.error("Số điện thoại không hợp lệ. Vui lòng nhập lại.")
                        
                        
                        
            with col3:
                customer_ad_channel = st.selectbox("Nguồn khách hàng", customer_source_list, index=customer_source_list.index("FB Mới"))
            
            customer_notes = st.text_area("Ghi chú", placeholder="Nhập ghi chú nếu có (ghi chú về khách hàng)")
            is_new = "yes"
            customer_record_id = ""
            st.info("Thông tin khách hàng sẽ được thêm mới khi bạn lưu đơn hàng!")
            
        else:
            # Chọn khách hàng từ danh sách
            st.info("Dưới đây là danh sách khách hàng đã chốt!")
            selected_customer = st.selectbox("Chọn khách hàng", st.session_state.customer_list)
            is_new = "no"
            
            # Lấy thông tin khách hàng đã chọn
            selected_customer_name = selected_customer.split(' - ')[0].strip()
            selected_customer_data = next(
                (customer for customer in customer_data 
                if customer['fields'].get('ID khách hàng', {'value': [{'text': ''}]})['value'][0]['text'].split('-')[0].strip() == selected_customer_name),
                None
            )

            if selected_customer_data:
                customer_id_value = selected_customer_data['fields'].get('ID khách hàng', {'value': [{'text': ''}]})['value'][0]['text']
                parts = customer_id_value.split('-')
                customer_name = parts[0].strip()
                customer_phone = parts[-1].strip() if len(parts) > 1 else ''
                customer_email = selected_customer_data['fields'].get('Email', [{'text': ''}])[0]['text']
                customer_ad_channel = selected_customer_data['fields'].get('Nguồn khách hàng', '')
                customer_notes = selected_customer_data['fields'].get('Ghi chú', [{'text': ''}])[0]['text']
                customer_record_id = selected_customer_data.get('record_id', '')

                # Ẩn số điện thoại
                if len(customer_phone) >= 6:
                    masked_phone = f"{customer_phone[:3]}{'*' * (len(customer_phone) - 6)}{customer_phone[-3:]}"
                else:
                    masked_phone = '*' * len(customer_phone)

                # Hiển thị thông tin khách hàng đã chọn
                st.subheader("Thông tin khách hàng")
                st.write(f"Tên khách hàng: {customer_name}")
                st.write(f"Số điện thoại: {masked_phone}")
                st.write(f"Nguồn khách hàng: {customer_ad_channel}")
                st.write(f"Ghi chú: {customer_notes}")
                    
            




        def remove_item(index):
            st.session_state.order_items.pop(index)


        # Đọc thông tin sản phẩm từ DataFrame
        product_data = dfs["table_product"].to_dict('records')

        # Khởi tạo session state
        if 'order_items' not in st.session_state:
            st.session_state.order_items = []

        # Chọn sản phẩm và số lượng
        st.header("Thông tin đơn hàng")
        
        

        col1, col2, col3 = st.columns(3)

        with col1:
            hinh_thuc_don_hang_list = ["Vật tư", "Hoàn thiện", "Đơn keo"]
            hinh_thuc_don_hang = st.selectbox("Hình thức đơn hàng", hinh_thuc_don_hang_list, index=hinh_thuc_don_hang_list.index("Vật tư"))

        with col2:
            hinh_thuc_thanh_toan_list = ["Thanh toán trước", "Thanh toán khi nhận hàng"]
            hinh_thuc_thanh_toan = st.selectbox("Hình thức thanh toán", hinh_thuc_thanh_toan_list)

        with col3:
            tinh_trang_chot_list = ["Chưa cọc", "Đã cọc"]
            tinh_trang_chot = st.selectbox("Tình trạng cọc", tinh_trang_chot_list)

        st.write("")
        if st.button("Thêm sản phẩm"):
            st.session_state.order_items.append({
                'product_id': '',
                'product_name': '',
                'quantity': 1,
                'price': 0,
                'unit': '',
                'category': '',
                'type': '',
                'note': '',
                'subtotal': 0
            })
        product_ids = sorted(list(set(product['fields']['Mã vật tư'] for product in product_data if product['fields'].get('Mã vật tư'))))
        order_items_df = pd.DataFrame(st.session_state.order_items)
        for index, order_item in order_items_df.iterrows():
            col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([0.5, 3, 1, 2, 1, 1, 1, 2, 2])
            
            with col1:
                st.write(f"#{index + 1}")
            
            with col2:
                product_id = st.selectbox("Mã vật tư", [''] + product_ids, key=f'product_{index}')
                if product_id != '':
                    product = next((p for p in product_data if p['fields']['Mã vật tư'] == product_id), None)
                    order_items_df.at[index, 'product_id'] = product_id
                else:
                    product = None
                    order_items_df.at[index, 'product_id'] = ''
            
            with col3:
                quantity = st.number_input("SL", min_value=1, value=order_item['quantity'], key=f'quantity_{index}')
                order_items_df.at[index, 'quantity'] = quantity
            
            with col4:
                default_price = product['fields'].get('Đơn giá', 0) if product else 0
                price = st.number_input("Đơn giá", value=float(default_price), key=f'price_{index}', format="%.0f")
                order_items_df.at[index, 'price'] = price
                
            with col5:
                unit = product['fields'].get('Đơn vị tính (khi lên đơn)', '') if product else ''
                st.write(f"ĐVT: {unit}")
                order_items_df.at[index, 'unit'] = unit
            
            with col6:
                category = product['fields'].get('Nhóm', '') if product else ''
                st.write(f"Nhóm: {category}")
                order_items_df.at[index, 'category'] = category
            
            with col7:
                product_type = product['fields'].get('Loại', '') if product else ''
                st.write(f"Loại: {product_type}")
                order_items_df.at[index, 'type'] = product_type
            
            with col8:
                note = st.text_input("Ghi chú", key=f'note_{index}')
                order_items_df.at[index, 'note'] = note
                
            with col9:
                subtotal = quantity * price
                order_items_df.at[index, 'subtotal'] = subtotal
                st.write(f"Thành tiền: {subtotal:,.0f} VNĐ")

        st.session_state.order_items = order_items_df.to_dict('records')

        st.info("Chỗ tính tổng thành tiền chưa hoàn thiện, do có sản phẩm tính theo m2 *1,03 chỗ này cần phải thảo luận lại!!!")
        st.info("Nhưng yên tâm, khi dữ liệu lưu ở table 4. Quản lý hợp đồng chi tiết sẽ chuẩn không lệch số nhé.")

        # Thêm nút xóa toàn bộ sản phẩm trong đơn hàng
        remove_all_button = st.button("Xóa toàn bộ sản phẩm")
        if remove_all_button:
            st.session_state.order_items = []
            st.rerun()

        if len(st.session_state.order_items) == 0:
            st.warning("Đơn hàng trống. Vui lòng thêm sản phẩm.")

        st.write("---")

        # Tính tổng tiền đơn hàng        
        total_amount = order_items_df['subtotal'].sum() if len(order_items_df) > 0 else 0
        st.subheader(f"Tổng tiền: {total_amount:,} VNĐ")

        col1, col2 = st.columns(2)

        with col1:
            st.session_state.tien_coc = st.number_input("Tiền cọc", min_value=0, value=0, step=100000, format="%d")
            st.session_state.phi_van_chuyen = st.number_input("Phí vận chuyển", min_value=0, value=0, step=10000, format="%d")

        with col2:
            st.session_state.phi_cong_tho = st.number_input("Phí công thợ", min_value=0, value=0, step=100000, format="%d")
            st.session_state.phu_thu = st.number_input("Phụ thu", min_value=0, value=0, step=100000, format="%d")
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.session_state.thoi_gian_thuc_hien_don_hang = st.date_input("Thời gian yêu cầu thực hiện đơn hàng", format="DD/MM/YYYY", value=None)  
            if st.session_state.thoi_gian_thuc_hien_don_hang:
                # Chuyển đổi thành đối tượng datetime với thời gian mặc định là 00:00:00
                thoi_gian_datetime = datetime.datetime.combine(st.session_state.thoi_gian_thuc_hien_don_hang, datetime.time.min)
                # Chuyển đổi thành timestamp
                thoi_gian_thuc_hien_don_hang_timestamp = int(thoi_gian_datetime.timestamp())
                # Chuyển đổi thành chuỗi dạng "dd/mm/yyyy"
                thoi_gian_dd_mm_yyyy = st.session_state.thoi_gian_thuc_hien_don_hang.strftime("%d/%m/%Y")
            else:
                thoi_gian_thuc_hien_don_hang_timestamp = None
                thoi_gian_dd_mm_yyyy = None   

        with col4:
            so_luong_m2_yeu_cau_giu = st.text_input("Số m2 yêu cầu giữ & Yêu cầu khác từ khách", placeholder="Nhập dạng số vd: 26")
        
        uploaded_files = st.file_uploader("Upload SƠ ĐỒ NHÀ KHÁCH & hình ảnh mặt bằng (nếu đơn hoàn thiện)", accept_multiple_files=True)
        
        
        # Thêm phần chọn địa chỉ
        st.subheader("Địa chỉ đơn hàng")
        selected_province, selected_district, selected_ward = address_selector()
        
        # Hiển thị địa chỉ đã chọn
        full_address_parts = [selected_ward, selected_district, selected_province]
        full_address_parts = [str(part) for part in full_address_parts if part not in [None, '', "nan"]]  # Chuyển đổi thành chuỗi và loại bỏ các giá trị không hợp lệ
        
        full_address = ", ".join(full_address_parts) if full_address_parts else ""
        dia_chi_chi_tiet = st.text_input("Địa chỉ chi tiết", placeholder="Nhập số nhà, tên đường...")
        
        if dia_chi_chi_tiet:
            st.write(f"Địa chỉ đầy đủ: {dia_chi_chi_tiet}, {full_address}")
        else:
            st.info("Vui lòng nhập chi tiết địa chỉ của khách!")
            
        ghi_chu_don_hang = st.text_area("Ghi chú", placeholder="Yêu cầu thêm của khách hàng, ghi chú,.... nhập vào đây!")


        # Thêm nút "Lưu đơn hàng"
        if st.button("Lưu đơn hàng"):
            # Kiểm tra xem tất cả các trường địa chỉ đã được điền đầy đủ chưa
            if not (selected_province and selected_district and selected_ward and dia_chi_chi_tiet):
                st.error("Vui lòng điền đầy đủ thông tin địa chỉ (Tỉnh/Thành phố, Quận/Huyện, Phường/Xã, và Địa chỉ chi tiết) trước khi lưu đơn hàng.")
            elif not selected_username or selected_username == "":
                st.error("Vui lòng chọn tên đăng nhập trước khi lưu đơn hàng.")
            else:
                # Tạo một phần tử empty để hiển thị thông báo
                info_placeholder = st.empty()   
                # Hiển thị thông báo
                info_placeholder.info("Đang lưu dữ liệu về larkbase, vui lòng chờ xíu nhen 🏃🏃🏃...")
                
                # Tạo danh sách sản phẩm trong đơn hàng
                order_items = []
                for index, row in order_items_df.iterrows():
                    product_id = row['product_id']
                    quantity = int(row['quantity'])
                    price = float(row['price'])
                    note = unidecode.unidecode(row['note'])
                    
                    order_item = {
                        "fields": {
                            'Mã vật tư': product_id,
                            'Số lượng': quantity,
                            'Đơn giá': price,
                            'Ghi chú': note,
                        }
                    }
                    order_items.append(order_item)
                
                # Lấy thông tin khách hàng
                customer_name = unidecode.unidecode(customer_name)
                customer_phone = unidecode.unidecode(customer_phone)
                customer_ad_channel = unidecode.unidecode(customer_ad_channel)
                
                # Mã hóa các file về base64 và lưu vào mảng
                uploaded_files_data = []
                for uploaded_file in uploaded_files:
                    file_content = uploaded_file.read() #đọc convert qua binary
                    file_size = uploaded_file.size
                    file_base64 = base64.b64encode(file_content).decode('utf-8')
                    uploaded_files_data.append({
                        'file_name': uploaded_file.name,
                        'file_size': file_size,
                        'file_binary_content': file_base64
                    })
                    
                # Tạo payload để gửi đi
                payload = {
                    'order': {
                        'Thêm mới khách hàng?': is_new,
                        'customer_record_id': customer_record_id,
                        'customer_notes': customer_notes,
                        'Tên khách hàng': customer_name,
                        'Số điện thoại': customer_phone,
                        'ID khách hàng': str(customer_name) + " - " + str(customer_phone),
                        'Nguồn khách hàng': customer_ad_channel,
                        'Ghi chú': unidecode.unidecode(ghi_chu_don_hang),
                        'Tiền cọc': st.session_state.tien_coc,
                        'Phụ thu': st.session_state.phu_thu,
                        'Phí vận chuyển': st.session_state.phi_van_chuyen,
                        'Phí công thợ': st.session_state.phi_cong_tho,
                        'Hình thức đơn hàng': hinh_thuc_don_hang,
                        'Địa chỉ': dia_chi_chi_tiet,
                        'so_luong_m2_yeu_cau_giu': so_luong_m2_yeu_cau_giu,
                        'thoi_gian_thuc_hien_don_hang_timestamp': thoi_gian_thuc_hien_don_hang_timestamp,
                        'thoi_gian_thuc_hien_don_hang_date': thoi_gian_dd_mm_yyyy,
                        'hinh_thuc_thanh_toan': hinh_thuc_thanh_toan,
                        'tinh_trang_chot': tinh_trang_chot,
                        'attachments': uploaded_files_data,
                        'user_name': selected_username,
                        'account_lark': [selected_sale['fields'].get('Tài khoản lark', [{}])[0]] if selected_sale else [],
                        'Tỉnh/Thành phố': selected_province,
                        'Quận/Huyện': selected_district,
                        'Phường/Xã': selected_ward,
                        'Địa chỉ chi tiết': dia_chi_chi_tiet,
                        'Địa chỉ đầy đủ': f"{dia_chi_chi_tiet}, {full_address}"
                    },
                    'order_items': order_items,
                    'flow_key': str(uuid.uuid4())  # Tạo flow_key duy nhất
                }
                
                st.write(payload)
                # URL của API endpoint
                url = st.secrets["webhook"]["url"]
                
                # Gửi yêu cầu POST đến API endpoint với xác thực HTTP Basic Auth (nếu cần)
                user = st.secrets["webhook"]["user"]
                password = st.secrets["webhook"]["password"]
                response = requests.post(url, json=payload, auth=HTTPBasicAuth(user, password))
                
                # Lấy mã trạng thái (status code) của phản hồi
                status_code = response.status_code

                # Lấy nội dung (content) của phản hồi
                response_content = response.text
                
                if status_code == 200:
                    info_placeholder.empty()
                    st.success("Đơn hàng đã được lưu và gửi đến webhook thành công!")
                    st.markdown("Xem chi tiết đơn hàng tại [đây](https://qfnpn9xcbdi.sg.larksuite.com/wiki/DBnFww2deiGz67kRxEglSsjZgxg?table=tblZhHGDDX6sz9k1&view=vew2HUeTTD).")
                    st.info(f"Nội dung phản hồi: {response_content}")
                else:
                    info_placeholder.empty()
                    st.error("Có lỗi xảy ra khi lưu và gửi đơn hàng. Vui lòng thử lại Gửi email thông qua support@nguyenngothuong.com nếu cần!")
                    st.error(f"Mã lỗi: {status_code}")
                    st.error(f"Nội dung phản hồi: {response_content}")
                
                
        st.write("")
        with st.popover("Đăng xuất"):
            if st.button("Xác nhận", key="xác nhận logout"):
                logout()
                st.success("Đăng xuất thành công!")
                login_page()
                st.rerun()