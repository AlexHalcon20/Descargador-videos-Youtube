from pytubefix import YouTube
from pytubefix.exceptions import AgeRestrictedError, LoginRequired, VideoUnavailable
import os


def cargar_video(url, forzar_oauth=False):
    """Carga el video y fuerza la obtención de sus metadatos (title,
    author, length) para que cualquier problema de disponibilidad salte
    aquí mismo, de forma controlada.

    NOTA IMPORTANTE: por un bug conocido de pytubefix (issue #674),
    activar use_oauth=True hace que YouTube responda con un falso
    "UNPLAYABLE / the page needs to be reloaded" para CUALQUIER video,
    incluso los que no tienen restricción de edad. Por eso solo usamos
    OAuth como último recurso, cuando el video realmente lo exige.
    """
    if forzar_oauth:
        yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
    else:
        yt = YouTube(url)

    # Forzamos el acceso a los metadatos ahora mismo (en vez de dejar
    # que fallen más adelante, fuera de este try/except).
    _ = yt.title
    _ = yt.author
    _ = yt.length
    return yt


def main():
    print("=== DESCARGADOR DE VIDEOS DE YOUTUBE ===\n")

    url = input("Introduce la URL del video de YouTube: ")

    try:
        try:
            # Intentamos primero SIN iniciar sesión: funciona para la
            # gran mayoría de los videos.
            yt = cargar_video(url)
        except (AgeRestrictedError, LoginRequired):
            # Solo si el video de verdad tiene restricción de edad,
            # reintentamos iniciando sesión con Google.
            print("🔒 Este video requiere iniciar sesión (restricción de edad).")
            print("   Reintentando con tu cuenta de Google...")
            yt = cargar_video(url, forzar_oauth=True)

        print(f"\n🎬 Título: {yt.title}")
        print(f"👤 Autor: {yt.author}")
        print(f"⏱️ Duración: {yt.length} segundos")
    except (AgeRestrictedError, LoginRequired) as e:
        print(f"❌ No se pudo iniciar sesión para ver este video: {e}")
        return
    except VideoUnavailable as e:
        print(f"❌ El video no está disponible: {e}")
        print("💡 Esto puede deberse a varias causas:")
        print("   - El video fue eliminado, es privado o está bloqueado en tu región.")
        print("   - Si el video SÍ tiene restricción de edad: hay un bug conocido")
        print("     de pytubefix donde iniciar sesión (OAuth) rompe la carga de")
        print("     CUALQUIER video. Revisa si ya salió una versión más nueva:")
        print("     pip install --upgrade pytubefix")
        return
    except Exception as e:
        print(f"❌ Error al cargar el video: {e}")
        return

    # Primero intentamos streams progresivos (video + audio en uno)
    progressive_streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
    
    # También obtenemos streams adaptativos (solo video, mayor calidad)
    adaptive_streams = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution').desc()
    
    print("\n📺 Opciones de descarga disponibles:")
    all_options = []
    option_num = 1
    
    # Mostrar streams progresivos
    if progressive_streams:
        print("\n🔄 Descargas directas (video + audio):")
        for stream in progressive_streams:
            size_mb = round(stream.filesize / 1024 / 1024, 2)
            print(f"{option_num}. {stream.resolution} - {size_mb} MB (directo)")
            all_options.append(('progressive', stream))
            option_num += 1
    
    # Mostrar streams adaptativos
    if adaptive_streams:
        print("\n⚡ Alta calidad (requiere combinar audio):")
        for stream in adaptive_streams:
            # Solo mostrar si la resolución es mayor a lo disponible en progresivo
            max_progressive_res = int(progressive_streams[0].resolution[:-1]) if progressive_streams else 0
            current_res = int(stream.resolution[:-1])
            
            if current_res > max_progressive_res:
                size_mb = round(stream.filesize / 1024 / 1024, 2)
                print(f"{option_num}. {stream.resolution} - {size_mb} MB (alta calidad)")
                all_options.append(('adaptive', stream))
                option_num += 1

    if not all_options:
        print("⚠️ No hay opciones de descarga disponibles.")
        return

    try:
        choice = int(input(f"\nSelecciona una opción (1-{len(all_options)}): ")) - 1
        stream_type, selected_stream = all_options[choice]
    except (ValueError, IndexError):
        print("❌ Selección inválida.")
        return

    # Crear carpeta de descargas si no existe
    download_folder = "descargas"
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    if stream_type == 'progressive':
        # Descarga directa
        print(f"\n⬇️ Descargando '{yt.title}' en {selected_stream.resolution} (directo)...")
        try:
            selected_stream.download(output_path=download_folder)
            print("✅ ¡Descarga completada exitosamente!")
        except Exception as e:
            print(f"❌ Error durante la descarga: {e}")
    
    else:  # adaptive
        # Descargar video y audio por separado, luego combinar
        print(f"\n⬇️ Descargando video en {selected_stream.resolution}...")
        
        try:
            # Obtener el mejor audio disponible
            audio_stream = yt.streams.filter(only_audio=True).first()
            if not audio_stream:
                print("❌ No se encontró stream de audio.")
                return
            
            # Descargar video
            video_filename = f"temp_video_{yt.video_id}.mp4"
            selected_stream.download(output_path=download_folder, filename=video_filename)
            
            # Descargar audio
            audio_filename = f"temp_audio_{yt.video_id}.mp4"
            audio_stream.download(output_path=download_folder, filename=audio_filename)
            
            print("🔄 Combinando video y audio...")
            
            # Combinar usando ffmpeg (necesita estar instalado)
            final_filename = f"{yt.title[:50].replace('/', '_')}.mp4"  # Limitar longitud del nombre
            video_path = os.path.join(download_folder, video_filename)
            audio_path = os.path.join(download_folder, audio_filename)
            output_path = os.path.join(download_folder, final_filename)
            
            # Comando ffmpeg para combinar
            ffmpeg_cmd = f'ffmpeg -i "{video_path}" -i "{audio_path}" -c copy "{output_path}"'
            
            result = os.system(ffmpeg_cmd)
            
            if result == 0:
                # Limpiar archivos temporales
                os.remove(video_path)
                os.remove(audio_path)
                print("✅ ¡Descarga y combinación completada exitosamente!")
            else:
                print("❌ Error al combinar video y audio.")
                print("💡 Asegúrate de tener ffmpeg instalado en tu sistema.")
                print("   Los archivos separados están en la carpeta 'descargas'")
                
        except Exception as e:
            print(f"❌ Error durante la descarga: {e}")

def check_ffmpeg():
    """Verifica si ffmpeg está disponible"""
    return os.system("ffmpeg -version > nul 2>&1") == 0 if os.name == 'nt' else os.system("ffmpeg -version > /dev/null 2>&1") == 0

if __name__ == "__main__":
    if not check_ffmpeg():
        print("⚠️ ADVERTENCIA: ffmpeg no está instalado.")
        print("   Solo se podrán descargar videos en calidades básicas (progresivos).")
        print("   Para alta calidad, instala ffmpeg desde: https://ffmpeg.org/")
        print()
    
    main()