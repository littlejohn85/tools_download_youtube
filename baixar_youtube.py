from pytubefix import YouTube
import os
import subprocess

# -----------------------------------------------
# Caminho absoluto do FFmpeg (ajuste se necessário)
# -----------------------------------------------
FFMPEG = r"C:\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"

# -----------------------------------------------
# Criar pasta para salvar os vídeos baixados
# -----------------------------------------------
PASTA_VIDEOS = "videos_baixados"
os.makedirs(PASTA_VIDEOS, exist_ok=True)

# -----------------------------------------------
# Auxiliares de tempo
# -----------------------------------------------
def seconds_to_hhmmss(segundos):
    segundos = int(segundos)
    h = segundos // 3600
    m = (segundos % 3600) // 60
    s = segundos % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def hhmmss_to_seconds(t):
    # aceita "HH:MM:SS" ou "MM:SS" ou "SS"
    parts = t.split(":")
    parts = [int(p) for p in parts]
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return parts[0]*60 + parts[1]
    if len(parts) == 3:
        return parts[0]*3600 + parts[1]*60 + parts[2]
    raise ValueError("Formato de tempo inválido")

def normalize_time_input(value):
    # valor pode ser int/float (segundos) ou string "HH:MM:SS"
    if isinstance(value, (int, float)):
        return seconds_to_hhmmss(int(value)), int(value)
    # se for string, verificar se é número (segundos) ou já formato HH:MM:SS
    value = value.strip()
    try:
        secs = int(value)
        return seconds_to_hhmmss(secs), secs
    except ValueError:
        # assume HH:MM:SS ou MM:SS
        secs = hhmmss_to_seconds(value)
        return seconds_to_hhmmss(secs), secs

# -----------------------------------------------
# Função para baixar vídeo com áudio
# -----------------------------------------------
def download_video(url):
    yt = YouTube(url)
    # compatibilidade com pytubefix/pytube: usar order_by/resolution caso get_highest_resolution falhe
    try:
        stream = yt.streams.filter(progressive=True, file_extension='mp4').get_highest_resolution()
    except Exception:
        stream = (
            yt.streams
              .filter(progressive=True, file_extension='mp4')
              .order_by("resolution")
              .desc()
              .first()
        )

    print(f"Baixando: {yt.title}")
    caminho_arquivo = stream.download(output_path=PASTA_VIDEOS)
    
    print(f"Download concluído! Arquivo salvo em: {caminho_arquivo}")
    return caminho_arquivo

# -----------------------------------------------
# Função para recortar vídeo usando FFmpeg (corrigida)
# -----------------------------------------------
def recortar_video(arquivo_video, inicio, fim, saida_nome="recorte.mp4"):
    # Normaliza entradas e obtém segundos
    inicio_str, inicio_secs = normalize_time_input(inicio)
    fim_str, fim_secs = normalize_time_input(fim)

    if fim_secs <= inicio_secs:
        raise ValueError("Tempo final deve ser maior que o tempo inicial.")

    duracao_secs = fim_secs - inicio_secs
    duracao_str = seconds_to_hhmmss(duracao_secs)  # opcional para logs

    # Caminho completo do vídeo de saída (usar caminho absoluto para evitar problemas)
    saida_caminho = os.path.abspath(os.path.join(PASTA_VIDEOS, saida_nome))

    # Monta lista de args para subprocess (mais robusto que string e os.system)
    # Usa -ss <start> antes do -i e -t <duration> para duração
    comando = [
        FFMPEG,
        "-ss", str(inicio_secs),
        "-i", os.path.abspath(arquivo_video),
        "-t", str(duracao_secs),
        "-c", "copy",
        saida_caminho
    ]

    print("Executando recorte do vídeo...")
    print("Comando:", " ".join(f'"{c}"' if " " in c else c for c in comando))  # log amigável
    
    try:
        resultado = subprocess.run(
                comando,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False  # <--- impede UnicodeDecodeError
            )
    except FileNotFoundError:
        print("Erro: ffmpeg não foi encontrado no caminho configurado.")
        print("Verifique a variável FFMPEG no topo do script:", FFMPEG)
        return None
    except subprocess.CalledProcessError as e:
        print("ffmpeg retornou erro ao executar o recorte.")
        print("Código de saída:", e.returncode)
        # Apenas exibe parte dos bytes para evitar erro
        print("stderr (bytes):", e.stderr[:500])
        return None
# -----------------------------------------------
# Execução principal
# -----------------------------------------------
if __name__ == "__main__":
    video_url = input("Entre com a URL do vídeo: ")

    # Baixar vídeo
    caminho_video = download_video(video_url)

    # Perguntar ao usuário se quer recortar
    opcao = input("Deseja recortar o vídeo? (s/n): ").lower().strip()

    if opcao == "s":
        inicio = input("Digite o tempo inicial (HH:MM:SS ou segundos): ").strip()
        fim = input("Digite o tempo final (HH:MM:SS ou segundos): ").strip()

        # Converte para número se possível (mantemos a flexibilidade)
        try:
            inicio = int(inicio)
        except:
            pass

        try:
            fim = int(fim)
        except:
            pass

        nome_saida = input("Nome do arquivo de saída (ex: corte.mp4): ").strip()
        if not nome_saida:
            nome_saida = "recorte.mp4"

        recortar_video(caminho_video, inicio, fim, nome_saida)

    print("Processo concluído!")
