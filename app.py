import streamlit as st
import pandas as pd
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import time

# 1. Cấu hình trang Streamlit
st.set_page_config(page_title="VCB AI Video Generator & Downloader", layout="wide")

st.title("🎬 Ứng Dụng Xuất Video Kịch Bản Vietcombank Tự Động")
st.markdown("Hệ thống tự động biên dịch kịch bản văn bản thành các slide video Phân cảnh + Lời thoại bằng Tiếng Việt và xuất file để tải về.")

st.divider()

# 2. Dữ liệu kịch bản gốc từ tài liệu của bạn
script_data = [
    {
        "Cảnh": "MỞ ĐẦU",
        "Hình ảnh": "Nhân viên Vietcombank mỉm cười trước máy tính.",
        "Lời thoại": "Xin chào Quý khách! Chỉ vài bước đơn giản dưới đây, Quý khách có thể đăng ký mở thẻ online ngay tại nhà. Hãy làm theo hướng dẫn nhé!"
    },
    {
        "Cảnh": "Bước 1: Truy cập vào website",
        "Hình ảnh": "Quay màn hình: gõ địa chỉ vietcombank.com.vn -> dangkydichvu.vietcombank.com.vn",
        "Lời thoại": "Quý khách có 2 cách: Cách 1: vào website chính thức, chọn Khách hàng cá nhân -> Đăng ký dịch vụ. Cách 2: truy cập trực tiếp vào link đăng ký dịch vụ."
    },
    {
        "Cảnh": "Bước 2: CHỌN TÍNH NĂNG ĐĂNG KÝ",
        "Hình ảnh": "Giao diện trang đăng ký hiển thị nút 'Đăng ký trực tuyến' nổi bật ở giữa.",
        "Lời thoại": "Tại đây, Quý khách chọn tính năng Đăng ký trực tuyến trên màn hình chính. Hoặc có thể chọn mục Đăng ký tại sản phẩm dịch vụ tương ứng."
    },
    {
        "Cảnh": "Bước 3: Điền thông tin và nhập OTP",
        "Hình ảnh": "Form đăng ký hiện ra (Họ tên, SĐT, CCCD...) -> Chuyển sang ô nhập OTP.",
        "Lời thoại": "Quý khách điền đầy đủ thông tin cá nhân, sau đó bấm Đăng ký. Hệ thống sẽ gửi mã xác thực đến số điện thoại. Quý khách nhập mã đó và bấm Tiếp tục."
    },
    {
        "Cảnh": "Bước 4: Chọn sản phẩm dịch vụ",
        "Hình ảnh": "Màn hình hiển thị danh sách loại thẻ. Con trỏ click chọn dòng 'Thẻ tín dụng'.",
        "Lời thoại": "Sau khi đăng nhập thành công, Quý khách thực hiện chọn loại sản phẩm dịch vụ mà mình có nhu cầu đăng ký."
    },
    {
        "Cảnh": "Bước 5: Chọn tư vấn và điền thông tin",
        "Hình ảnh": "Giao diện chọn Hình thức tư vấn, Địa điểm, Thời gian nhận thẻ.",
        "Lời thoại": "Quý khách chọn hình thức tư vấn mong muốn, địa điểm và thời gian nhận tư vấn. Lưu ý điền bổ sung thông tin nếu chưa có trên hệ thống."
    },
    {
        "Cảnh": "Bước 6: Kiểm tra và xác nhận",
        "Hình ảnh": "Màn hình hiển thị bảng tổng hợp toàn bộ thông tin đã nhập.",
        "Lời thoại": "Hệ thống hiển thị lại toàn bộ thông tin đã đăng ký. Quý khách vui lòng kiểm tra thật kỹ. Nếu đúng, bấm Xác nhận để tiếp tục."
    },
    {
        "Cảnh": "Bước 7: Thông báo thành công và upload hồ sơ",
        "Hình ảnh": "Thông báo xanh đăng ký thành công -> Hiện popup upload ảnh CMND/CCCD.",
        "Lời thoại": "Thông báo đăng ký thành công hiện lên. Ngay sau đó, hệ thống sẽ yêu cầu upload hồ sơ. Quý khách nhấn Đồng ý để thực hiện tải hồ sơ lên nhé!"
    },
    {
        "Cảnh": "KẾT THÚC",
        "Hình ảnh": "Quay lại nhân viên Vietcombank mỉm cười chào tạm biệt khách hàng.",
        "Lời thoại": "Vậy là Quý khách đã hoàn tất đăng ký. Nhân viên Vietcombank sẽ liên hệ lại đúng giờ hẹn. Cảm ơn Quý khách! Hotline: 1900..."
    }
]

# Hiển thị bảng kịch bản trực quan
st.subheader("📋 Kịch bản đang sử dụng để sinh video")
st.dataframe(pd.DataFrame(script_data), use_container_width=True)

st.divider()

# 3. Hàm vẽ Text Tiếng Việt có dấu lên Video bằng Pillow (Tránh lỗi font của OpenCV)
def create_video_frame(title, img_desc, voice_text, width=1280, height=720):
    # Tạo hình nền màu xám trắng thanh lịch
    img = Image.new('RGB', (width, height), color=(245, 247, 248))
    draw = ImageDraw.Draw(img)
    
    # Vẽ thanh tiêu đề trên cùng màu xanh Vietcombank (Green #006A4E)
    draw.rectangle([0, 0, width, 110], fill=(0, 106, 78))
    
    # Tìm kiếm font chữ hệ thống hỗ trợ tiếng Việt để hiển thị không lỗi
    font_paths = ["Arial.ttf", "arial.ttf", "/Library/Fonts/Arial.ttf", "C:\\Windows\\Fonts\\arial.ttf"]
    font_title, font_sub, font_body = None, None, None
    for path in font_paths:
        if os.path.exists(path):
            try:
                font_title = ImageFont.truetype(path, 34)
                font_sub = ImageFont.truetype(path, 22)
                font_body = ImageFont.truetype(path, 20)
                break
            except:
                continue
    if font_title is None:
        font_title = font_sub = font_body = ImageFont.load_default()

    # Viết tiêu đề Phân Cảnh (Chữ trắng trên nền xanh)
    draw.text((40, 35), title.upper(), fill=(255, 255, 255), font=font_title)
    
    # Phần hiển thị mô tả Hình ảnh trực quan
    draw.text((50, 160), "🎬 BỐ TRÍ HÌNH ẢNH MINH HỌA:", fill=(0, 106, 78), font=font_sub)
    draw.text((50, 205), img_desc, fill=(40, 40, 40), font=font_body)
    
    # Vẽ đường kẻ chia tách vùng nội dung
    draw.line([(50, 320), (width-50, 320)], fill=(200, 200, 200), width=2)
    
    # Phần hiển thị Lời thoại / Giọng đọc thuyết minh (Voice-over)
    draw.text((50, 360), "🗣️ LỜI THOẠI AI (VOICE-OVER SCRIPT):", fill=(0, 106, 78), font=font_sub)
    
    # Tự động xuống dòng cho đoạn lời thoại dài không bị tràn màn hình
    words = voice_text.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        if len(" ".join(current_line)) > 75:  # Giới hạn ký tự mỗi dòng
            current_line.pop()
            lines.append(" ".join(current_line))
            current_line = [word]
    lines.append(" ".join(current_line))
    
    y_text = 410
    for line in lines:
        draw.text((50, y_text), line, fill=(60, 60, 60), font=font_body)
        y_text += 35
        
    # Thanh hiển thị chân trang thương hiệu
    draw.rectangle([0, height-50, width, height], fill=(0, 106, 78))
    draw.text((40, height-35), "HƯỚNG DẪN ĐĂNG KÝ DỊCH VỤ TRỰC TUYẾN - VIETCOMBANK AI VIDEO SYSTEM", fill=(255, 255, 255), font=font_body)
    
    # Chuyển đổi định dạng từ PIL Image sang mảng NumPy màu BGR để OpenCV xử lý được
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

# 4. Khu vực tương tác tạo và tải video
st.subheader("⚙️ Tạo & Xuất File Video")
output_filename = "kich_ban_mo_the_vcb.mp4"

if st.button("🚀 Bắt đầu xuất Video AI từ kịch bản", type="primary"):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Thiết lập tham số video đầu ra (Độ phân giải HD 1280x720, 24 khung hình/giây)
    width, height = 1280, 720
    fps = 24
    duration_per_scene = 4  # Mỗi bước xuất hiện trong 4 giây trên video
    frames_per_scene = fps * duration_per_scene
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Bộ mã hóa video MP4 chuẩn thông dụng
    video_writer = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))
    
    status_text.text("Đang khởi tạo trình biên dịch video...")
    total_scenes = len(script_data)
    
    for idx, item in enumerate(script_data):
        status_text.text(f"Đang thiết kế khung hình: {item['Cảnh']}...")
        
        # Tạo ảnh khung hình mẫu cho phân cảnh
        frame = create_video_frame(item['Cảnh'], item['Hình ảnh'], item['Lời thoại'], width, height)
        
        # Ghi lặp lại khung hình đó để tạo thời gian chờ (Duration) cho clip
        for _ in range(frames_per_scene):
            video_writer.write(frame)
            
        # Cập nhật thanh tiến trình chạy
        progress_bar.progress(int((idx + 1) / total_scenes * 100))
        time.sleep(0.2)
        
    video_writer.release()  # Đóng kết nối xuất file hoàn tất
    status_text.text("🎉 Hoàn tất quá trình tạo video kịch bản thành công!")
    
    # 5. Hiển thị Video phát trực tiếp và nút Download cho người dùng
    st.success("Tạo thành công file video định dạng MP4!")
    
    col_v, col_d = st.columns([2, 1])
    with col_v:
        st.markdown("#### Trình phát video xem trước:")
        st.video(output_filename)
        
    with col_d:
        st.markdown("#### Tải video về máy tính:")
        with open(output_filename, "rb") as file:
            st.download_button(
                label="📥 Tải xuống Video (.mp4)",
                data=file,
                file_name="Video_Huong_Dan_Mo_The_VCB.mp4",
                mime="video/mp4",
                key="download-mp4"
            )
        st.info("💡 Bạn có thể lấy video này gửi lên các nền tảng AI như Studio D-ID hoặc HeyGen để khớp khẩu hình nhân viên số tự động hoàn chỉnh.")
