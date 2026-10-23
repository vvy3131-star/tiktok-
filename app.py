import streamlit as st
from PIL import Image, ImageFilter, ImageOps
import numpy as np
import os
import yt_dlp
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip

# Cấu hình giao diện Streamlit
st.set_page_config(page_title="Tạo Video Trình Phát Nhạc TikTok Style", page_icon="🎵", layout="centered")

st.title("🎵 Trình Tạo Video Giao Diện Trình Phát Nhạc (Glassmorphism)")
st.write("Tạo video dọc chuẩn TikTok/Reels với hiệu ứng nền mờ, trình phát nhạc trong suốt và âm thanh từ YouTube!")

# --- HÀM TẢI ÂM THANH TỪ YOUTUBE ---
@st.cache_resource
def download_youtube_audio(search_query_or_url):
    audio_filename = "downloaded_audio.mp3"
    if os.path.exists(audio_filename):
        try:
            os.remove(audio_filename)
        except:
            pass
        
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
            duration = info.get('duration', 10)
        return audio_filename, title, int(duration)
    except Exception as e:
        st.error(f"Lỗi khi tải nhạc từ YouTube: {e}")
        return None, None, 0

# --- THANH BÊN (SIDEBAR) TÙY CHỈNH ---
st.sidebar.header("⚙️ Tùy chỉnh video")

uploaded_image = st.sidebar.file_uploader("Tải lên ảnh bìa (Album Art)", type=["jpg", "png", "jpeg"])
music_input = st.sidebar.text_input("Link YouTube hoặc Tên bài hát", "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
song_title = st.sidebar.text_input("Tên bài hát hiển thị", "4 Mùa Thường Em - Demo Remix")
artist_name = st.sidebar.text_input("Tên nghệ sĩ / ID TikTok", "@prDhaiyang_461")
max_duration = st.sidebar.slider("Thời lượng video xuất ra (giây)", min_value=3, max_value=25, value=10)

# Xử lý ảnh mặc định nếu chưa tải lên
if uploaded_image is not None:
    img = Image.open(uploaded_image).convert("RGBA")
else:
    img = Image.new('RGBA', (500, 500), color=(255, 182, 193, 255))

# --- XEM TRƯỚC GIAO DIỆN ---
st.subheader("📱 Xem trước thông tin")
col1, col2 = st.columns([1, 2])
with col1:
    st.image(img.convert("RGB"), caption="Ảnh bìa", width=200)
with col2:
    st.markdown(f"**🎶 Bài hát:** {song_title}")
    st.markdown(f"**👤 Nghệ sĩ:** {artist_name}")
    st.markdown(f"**🔗 Nguồn nhạc:** {music_input}")

st.markdown("---")

# --- NÚT TẠO VIDEO ---
if st.button("🚀 Tiến hành tạo Video Hiệu Ứng Đẹp"):
    with st.spinner("Đang tải âm thanh và render hiệu ứng video, vui lòng đợi..."):
        audio_path, yt_title, yt_duration = download_youtube_audio(music_input)
        
        if audio_path and os.path.exists(audio_path):
            try:
                # Kích thước chuẩn video dọc TikTok (9:16)
                width, height = 720, 1280
                clip_duration = min(max_duration, yt_duration) if yt_duration > 0 else max_duration
                
                # 1. Tạo hiệu ứng nền mờ (Blur Background) từ ảnh gốc
                bg_base = img.convert("RGB").resize((width, height))
                bg_img = bg_base.filter(ImageFilter.GaussianBlur(25))
                # Làm tối nhẹ nền để nổi bật khung phát nhạc
                bg_np = np.array(bg_img) * 0.7 
                background_clip = ImageClip(bg_np.astype(np.uint8)).set_duration(clip_duration)
                
                # 2. Tạo khung trình phát nhạc trong suốt (Glassmorphism card) giống mẫu
                card_width, card_height = 620, 780
                card_img = Image.new("RGBA", (card_width, card_height), (255, 255, 255, 35)) # Độ trong suốt kính mờ
                
                # Tạo viền bo tròn nhẹ cho card (hoặc khung vuông góc mềm)
                # Dán ảnh bìa vào chính giữa khung card
                art_size = 540
                resized_art = img.convert("RGBA").resize((art_size, art_size))
                
                # Tính toán vị trí để căn giữa ảnh trong card
                art_x = (card_width - art_size) // 2
                art_y = 40
                card_img.paste(resized_art, (art_x, art_y), resized_art)
                
                # Lưu ảnh card tạm thời
                card_path = "temp_glass_card.png"
                card_img.save(card_path)
                
                # Đưa khung card vào video chính (căn giữa màn hình)
                card_clip = ImageClip(card_path).set_duration(clip_duration).set_position(("center", 180))
                
                # 3. Thêm âm thanh
                audio_clip = AudioFileClip(audio_path).subclip(0, clip_duration)
                
                # 4. Tổng hợp video hoàn chỉnh
                video = CompositeVideoClip([background_clip, card_clip], size=(width, height))
                video = video.set_audio(audio_clip)
                video = video.set_duration(clip_duration)
                
                output_path = "output_tiktok_video.mp4"
                video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
                
                st.success("🎉 Tạo video thành công với hiệu ứng cực đẹp!")
                st.video(output_path)
                
                # Nút tải xuống
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="📥 Tải xuống Video MP4",
                        data=file,
                        file_name="music_tiktok_style.mp4",
                        mime="video/mp4"
                    )
                
                # Dọn dẹp file tạm
                if os.path.exists(card_path):
                    os.remove(card_path)
                    
            except Exception as e:
                st.error(f"Đã xảy ra lỗi trong quá trình render video: {e}")
        else:
            st.error("Không thể tải âm thanh từ YouTube. Vui lòng kiểm tra lại link hoặc từ khóa tìm kiếm.")
