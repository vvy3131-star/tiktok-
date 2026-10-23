import streamlit as st
from PIL import Image, ImageFilter
import numpy as np
import os

# Cấu hình giao diện Streamlit
st.set_page_config(page_title="Tạo Video Trình Phát Nhạc Trong Suốt", page_icon="🎵", layout="centered")

st.title("🎵 Trình Tạo Video Giao Diện Trình Phát Nhạc")
st.write("Tải lên hình ảnh, tùy chỉnh tên bài hát và tạo video phong cách trong suốt (Glassmorphic) giống như video mẫu!")

# --- THANH BÊN (SIDEBAR) TÙY CHỈNH ---
st.sidebar.header("⚙️ Tùy chỉnh nội dung")
uploaded_image = st.sidebar.file_uploader("Tải lên ảnh bìa (Album Art)", type=["jpg", "png", "jpeg"])
song_title = st.sidebar.text_input("Tên bài hát", "4 Mùa Thường Em - Demo Haiyang Remix")
artist_name = st.sidebar.text_input("Tên nghệ sĩ / ID TikTok", "@prDhaiyang_461")
duration = st.sidebar.slider("Thời lượng video (giây)", min_value=3, max_value=15, value=5)

# Xử lý ảnh mặc định nếu chưa tải lên
if uploaded_image is not None:
    img = Image.open(uploaded_image).convert("RGB")
else:
    # Tạo một ảnh màu hồng mặc định nếu chưa có ảnh
    img = Image.new('RGB', (500, 500), color=(255, 182, 193))

# --- HIỂN THỊ GIAO DIỆN TRỰC QUAN TRÊN WEB ---
st.subheader("📱 Xem trước ảnh bìa và thông tin")
col1, col2 = st.columns([1, 2])
with col1:
    st.image(img, caption="Ảnh đã chọn", width=200)
with col2:
    st.markdown(f"**🎶 Bài hát:** {song_title}")
    st.markdown(f"**👤 Tài khoản:** {artist_name}")
    st.markdown(f"**⏱️ Thời lượng:** {duration} giây")

st.markdown("---")

# --- NÚT TẠO VIDEO ---
if st.button("🚀 Tiến hành tạo Video MP4"):
    with st.spinner("Đang render video, vui lòng đợi trong giây lát..."):
        try:
            from moviepy.editor import ImageClip, CompositeVideoClip
            
            # Kích thước video dọc chuẩn TikTok (9:16)
            width, height = 720, 1280
            
            # 1. Tạo hiệu ứng nền mờ từ ảnh gốc
            bg_img = img.resize((width, height)).filter(ImageFilter.GaussianBlur(20))
            bg_np = np.array(bg_img)
            background_clip = ImageClip(bg_np).set_duration(duration)
            
            # 2. Tạo khung trình phát nhạc trong suốt (Glassmorphism card)
            card_width, card_height = 600, 750
            card_img = Image.new("RGBA", (card_width, card_height), (255, 255, 255, 45)) # Độ trong suốt tùy chỉnh
            
            # Dán ảnh vào khung card (bo góc hoặc vuông tùy ý)
            resized_art = img.resize((520, 520))
            card_img.paste(resized_art, (40, 40))
            
            # Lưu ảnh card tạm thời
            card_path = "temp_card.png"
            card_img.save(card_path)
            
            # Tạo clip cho khung card và đặt ở giữa màn hình
            card_clip = ImageClip(card_path).set_duration(duration).set_position(("center", 200))
            
            # 3. Tổng hợp video
            video = CompositeVideoClip([background_clip, card_clip], size=(width, height))
            
            output_path = "output_music_video.mp4"
            video.write_videofile(output_path, fps=24, codec="libx264", audio=False)
            
            st.success("🎉 Tạo video thành công!")
            st.video(output_path)
            
            # Nút tải xuống
            with open(output_path, "rb") as file:
                st.download_button(
                    label="📥 Tải xuống Video MP4",
                    data=file,
                    file_name="music_player_video.mp4",
                    mime="video/mp4"
                )
            
            # Dọn dẹp file tạm
            if os.path.exists(card_path):
                os.remove(card_path)
                
        except Exception as e:
            st.error(f"Đã xảy ra lỗi khi tạo video: {e}")
