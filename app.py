import streamlit as st
from PIL import Image, ImageFilter
import numpy as np
import os
import yt_dlp
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip

# Cấu hình giao diện Streamlit
st.set_page_config(page_title="Tạo Video Trình Phát Nhạc YouTube", page_icon="🎵", layout="centered")

st.title("🎵 Trình Tạo Video Giao Diện Trình Phát Nhạc (Hỗ trợ YouTube Audio)")
st.write("Tải ảnh, chọn/nhập nhạc từ YouTube, tùy chỉnh tên bài hát và xuất video phong cách trong suốt!")

# --- HÀM TẢI ÂM THANH TỪ YOUTUBE ---
@st.cache_resource
def download_youtube_audio(search_query_or_url):
    audio_filename = "downloaded_audio.mp3"
    if os.path.exists(audio_filename):
        os.remove(audio_filename)
        
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloaded_audio',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
    }
    
    # Kiểm tra xem là Link hay từ khóa tìm kiếm
    if not search_query_or_url.startswith("http"):
        search_query = f"ytsearch1:{search_query_or_url}"
    else:
        search_query = search_query_or_url

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=True)
            if 'entries' in info:
                info = info['entries'][0]
            title = info.get('title', 'Bài hát không tên')
            duration = info.get('duration', 10) # Thời lượng tính bằng giây
        return audio_filename, title, int(duration)
    except Exception as e:
        st.error(f"Lỗi khi tải nhạc từ YouTube: {e}")
        return None, None, 0

# --- THANH BÊN (SIDEBAR) TÙY CHỈNH ---
st.sidebar.header("⚙️ Tùy chỉnh nội dung")

# 1. Tùy chỉnh Ảnh
uploaded_image = st.sidebar.file_uploader("Tải lên ảnh bìa (Album Art)", type=["jpg", "png", "jpeg"])

# 2. Tùy chỉnh Âm nhạc (Link hoặc Tên bài hát)
music_input = st.sidebar.text_input("Nhập Link YouTube hoặc Tên bài hát", "https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# 3. Tùy chỉnh văn bản hiển thị trên video
song_title = st.sidebar.text_input("Tên bài hát hiển thị", "4 Mùa Thường Em - Demo Remix")
artist_name = st.sidebar.text_input("Tên nghệ sĩ / ID TikTok", "@prDhaiyang_461")

# 4. Thời lượng video muốn xuất (Giới hạn theo bài hát)
max_duration = st.sidebar.slider("Thời lượng video xuất ra (giây)", min_value=3, max_value=30, value=10)

# Xử lý ảnh mặc định nếu chưa tải lên
if uploaded_image is not None:
    img = Image.open(uploaded_image).convert("RGB")
else:
    img = Image.new('RGB', (500, 500), color=(255, 182, 193))

# --- HIỂN THỊ GIAO DIỆN TRỰC QUAN ---
st.subheader("📱 Xem trước thông tin")
col1, col2 = st.columns([1, 2])
with col1:
    st.image(img, caption="Ảnh bìa", width=200)
with col2:
    st.markdown(f"**🎶 Tên hiển thị:** {song_title}")
    st.markdown(f"**👤 Nghệ sĩ:** {artist_name}")
    st.markdown(f"**🔗 Nguồn nhạc:** {music_input}")

st.markdown("---")

# --- NÚT TẠO VIDEO ---
if st.button("🚀 Tiến hành tải nhạc và tạo Video MP4"):
    with st.spinner("Đang tải âm thanh từ YouTube và Render video..."):
        # Tải nhạc từ YouTube
        audio_path, yt_title, yt_duration = download_youtube_audio(music_input)
        
        if audio_path and os.path.exists(audio_path):
            try:
                # Kích thước video dọc chuẩn TikTok (9:16)
                width, height = 720, 1280
                
                # Xác định thời lượng video (lấy min giữa thời lượng user chọn và độ dài file nhạc)
                clip_duration = min(max_duration, yt_duration) if yt_duration > 0 else max_duration
                
                # 1. Tạo hiệu ứng nền mờ từ ảnh gốc
                bg_img = img.resize((width, height)).filter(ImageFilter.GaussianBlur(20))
                bg_np = np.array(bg_img)
                background_clip = ImageClip(bg_np).set_duration(clip_duration)
                
                # 2. Tạo khung trình phát nhạc trong suốt (Glassmorphism card)
                card_width, card_height = 600, 750
                card_img = Image.new("RGBA", (card_width, card_height), (255, 255, 255, 45)) # Độ trong suốt
                
                # Dán ảnh vào khung card
                resized_art = img.resize((520, 520))
                card_img.paste(resized_art, (40, 40))
                
                card_path = "temp_card.png"
                card_img.save(card_path)
                
                # Tạo clip khung card và đặt ở giữa màn hình
                card_clip = ImageClip(card_path).set_duration(clip_duration).set_position(("center", 200))
                
                # 3. Thêm âm thanh vào video
                audio_clip = AudioFileClip(audio_path).subclip(0, clip_duration)
                
                # 4. Tổng hợp video hoàn chỉnh
                video = CompositeVideoClip([background_clip, card_clip], size=(width, height))
                video = video.set_audio(audio_clip)
                video = video.set_duration(clip_duration)
                
                output_path = "output_music_video.mp4"
                video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
                
                st.success(f"🎉 Tạo video thành công! (Tên gốc từ YouTube: {yt_title})")
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
                st.error(f"Đã xảy ra lỗi trong quá trình xử lý video: {e}")
        else:
            st.error("Không thể tải được âm thanh từ YouTube. Vui lòng kiểm tra lại đường dẫn hoặc từ khóa.")
