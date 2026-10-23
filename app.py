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
