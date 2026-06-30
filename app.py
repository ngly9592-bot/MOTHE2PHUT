import streamlit as st
import pandas as pd
import time

# Cấu hình trang
st.set_page_config(page_title="VCB AI Video Generator", layout="wide")

st.title("🎬 Trình tạo Video AI: Kịch bản Mở thẻ Vietcombank")
st.markdown("Ứng dụng này quản lý kịch bản và tích hợp API tạo Video AI (như HeyGen, D-ID) để render video tự động dựa trên lời thoại và mô tả hành động.")

st.divider()

# Dữ liệu kịch bản trích xuất từ tài liệu
script_data = [
    {
        "Cảnh": "Mở đầu",
        "Hình ảnh": "Nhân viên Vietcombank mỉm cười trước máy tính.",
        "Lời thoại": "Xin chào Quý khách! Chỉ vài bước đơn giản dưới đây, Quý khách có thể đăng ký mở thẻ online ngay tại nhà. Hãy làm theo hướng dẫn nhé!",
        "Hành động / Ghi chú": "Chữ: HƯỚNG DẪN ĐĂNG KÝ MỞ THẺ TRỰC TUYẾN"
    },
    {
        "Cảnh": "Bước 1: Truy cập vào website",
        "Hình ảnh": "Quay màn hình: gõ địa chỉ vietcombank.com.vn, sau đó dangkydichvu.vietcombank.com.vn",
        "Lời thoại": "Quý khách có 2 cách: Cách 1: vào https://www.vietcombank.com.vn/vi-VN... Cách 2: truy cập trực tiếp vào https://dangkydichvu.vietcombank.com.vn/...",
        "Hành động / Ghi chú": "Con trỏ di vào mục Khách hàng cá nhân → Đăng ký dịch vụ."
    },
    {
        "Cảnh": "Bước 2: Chọn tính năng đăng ký",
        "Hình ảnh": "Giao diện trang đăng ký dịch vụ hiển thị. Có nút 'Đăng ký trực tuyến' ở giữa.",
        "Lời thoại": "Tại đây, Quý khách chọn tính năng Đăng ký trực tuyến trên màn hình chính. Hoặc có thể chọn mục Đăng ký tại sản phẩm dịch vụ tương ứng.",
        "Hành động / Ghi chú": "Click vào nút to 'Đăng ký trực tuyến' ở giữa màn hình."
    },
    {
        "Cảnh": "Bước 3: Điền thông tin và nhập OTP",
        "Hình ảnh": "Form đăng ký hiện ra. Chuyển cảnh 2: Ô nhập mã OTP.",
        "Lời thoại": "Quý khách điền đầy đủ thông tin cá nhân, sau đó bấm Đăng ký. Hệ thống sẽ gửi mã xác thực đến số điện thoại. Quý khách nhập mã đó và bấm Tiếp tục...",
        "Hành động / Ghi chú": "Nhập thông tin -> Bấm Đăng ký -> Nhập OTP 6 số -> Bấm Tiếp tục."
    },
    {
        "Cảnh": "Bước 4: Chọn sản phẩm dịch vụ",
        "Hình ảnh": "Màn hình hiện danh sách các loại thẻ/dịch vụ.",
        "Lời thoại": "Sau khi đăng nhập thành công, Quý khách thực hiện chọn loại sản phẩm dịch vụ mà mình có nhu cầu đăng ký.",
        "Hành động / Ghi chú": "Con trỏ click chọn 1 dòng sản phẩm (ví dụ: 'Thẻ tín dụng')."
    },
    {
        "Cảnh": "Bước 5: Chọn tư vấn và điền thông tin",
        "Hình ảnh": "Giao diện bước 5: Các tùy chọn (Hình thức tư vấn, Địa điểm, Thời gian).",
        "Lời thoại": "Quý khách chọn hình thức tư vấn mong muốn, địa điểm và thời gian nhận tư vấn. Lưu ý: Hãy điền đầy đủ thông tin tại bước này.",
        "Hành động / Ghi chú": "Chọn Tư vấn qua điện thoại, chọn Chi nhánh, khung giờ..."
    },
    {
        "Cảnh": "Bước 6: Kiểm tra và xác nhận",
        "Hình ảnh": "Màn hình chuyển sang bảng tổng hợp tất cả thông tin.",
        "Lời thoại": "Hệ thống hiển thị lại toàn bộ thông tin đã đăng ký. Quý khách vui lòng kiểm tra thật kỹ. Nếu đúng, bấm Xác nhận để tiếp tục.",
        "Hành động / Ghi chú": "Cuộn chậm từ trên xuống -> Bấm nút 'Xác nhận'."
    },
    {
        "Cảnh": "Bước 7: Thông báo thành công & Upload hồ sơ",
        "Hình ảnh": "Thông báo xanh 'Đăng ký SPDV thành công'. Popup yêu cầu 'Upload hồ sơ'.",
        "Lời thoại": "Thông báo đăng ký thành công hiện lên. Ngay sau đó, hệ thống sẽ yêu cầu upload hồ sơ. Quý khách nhấn Đồng ý để thực hiện tải hồ sơ lên nhé!",
        "Hành động / Ghi chú": "Click nút Đồng ý -> Chọn file CMND -> Bấm Upload."
    },
    {
        "Cảnh": "Kết thúc",
        "Hình ảnh": "Quay lại nhân viên, cười và kết thúc.",
        "Lời thoại": "Vậy là Quý khách đã hoàn tất đăng ký. Nhân viên Vietcombank sẽ liên hệ lại đúng giờ hẹn. Cảm ơn Quý khách!",
        "Hành động / Ghi chú": "Chữ: CẢM ƠN QUÝ KHÁCH! Hotline: 1900..."
    }
]

df_script = pd.DataFrame(script_data)

st.subheader("📋 Bảng Kịch Bản Chi Tiết")
st.dataframe(df_script, use_container_width=True)

st.divider()

st.subheader("🤖 Cấu hình AI Video Generation")
col1, col2 = st.columns(2)

with col1:
    ai_avatar = st.selectbox("Chọn AI Avatar (Nhân viên VCB):", ["Cô gái mặc áo dài xanh", "Chàng trai mặc vest đen", "Tùy chỉnh tải lên..."])
    voice_model = st.selectbox("Chọn Giọng đọc AI (Voice-over):", ["Nữ - Miền Bắc (Ngọc Trinh)", "Nam - Miền Nam (Minh Hoàng)", "Nữ - Miền Nam (Lan Anh)"])

with col2:
    bg_music = st.selectbox("Nhạc nền:", ["Vietcombank Theme Nhẹ nhàng", "Corporate Uplifting", "Không nhạc"])
    resolution = st.radio("Độ phân giải:", ["1080p (Ngang - Youtube/Web)", "9:16 (Dọc - Tiktok/Shorts)"])

# Nút giả lập quá trình gửi dữ liệu qua API tạo Video
if st.button("🚀 Xử lý Kịch Bản & Tạo Video AI", type="primary"):
    with st.status("Đang gửi lệnh tới server AI Video..."):
        st.write("Đang tải dữ liệu kịch bản (Text-to-Speech)...")
        time.sleep(1.5)
        st.write("Đang render Avatar và ghép khẩu hình (Lip-sync)...")
        time.sleep(2)
        st.write("Đang thêm hiệu ứng quay màn hình và sub (Phụ đề)...")
        time.sleep(2)
        st.write("Đang render final video...")
        time.sleep(1.5)
    
    st.success("🎉 Video AI của bạn đã sẵn sàng!")
    st.info("Trong ứng dụng thực tế, bạn sẽ nhận được một file MP4 hoặc URL video trả về từ HeyGen/D-ID tại đây để phát bằng `st.video()`.")
    # st.video("duong_dan_den_video_ai_da_tao.mp4")
