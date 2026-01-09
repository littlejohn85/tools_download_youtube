# 📥 YouTube Downloader + ✂️ Video Cutter (Debug & Flow)

Este documento descreve **o fluxo**, **o objetivo**, **o debug técnico** e **boas práticas** aplicadas ao script fornecido, que realiza:

1. Download de vídeos do YouTube (vídeo + áudio)
2. Recorte de trechos específicos usando FFmpeg

---

## 🎯 Objetivo do Script

Automatizar o processo de:

* Baixar um vídeo do YouTube em MP4 (stream progressivo)
* Permitir ao usuário definir um intervalo de tempo
* Gerar um novo arquivo contendo apenas o trecho desejado

Tudo isso de forma **robusta**, **compatível com Windows** e tolerante a erros comuns.

---

## 🧠 Visão Geral do Fluxo

```text
[Usuário]
   ↓ URL
[download_video]
   ↓ arquivo.mp4
[Input recorte?]
   ↓ (s)
[normalize_time_input]
   ↓ segundos
[recortar_video]
   ↓ ffmpeg
[arquivo_recortado.mp4]
```

---

## 📦 Dependências

* Python 3.9+
* pytubefix
* FFmpeg (binário externo)

```bash
pip install pytubefix
```

---

## 📁 Estrutura Gerada

```text
.
├── script.py
├── videos_baixados/
│   ├── video_original.mp4
│   └── recorte.mp4
```

---

## 🔧 Debug por Blocos

### 1️⃣ Configuração do FFmpeg

```python
FFMPEG = r"C:\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"
```

✅ Correto para Windows
⚠️ Se o caminho estiver errado → `FileNotFoundError`

---

### 2️⃣ Criação da Pasta de Saída

```python
os.makedirs(PASTA_VIDEOS, exist_ok=True)
```

✔️ Evita erro se a pasta já existir
✔️ Garante organização

---

### 3️⃣ Funções de Tempo (PONTO CRÍTICO)

Essas funções são o **coração do script**.

#### ✔️ O que foi resolvido:

* Entrada aceita:

  * `120`
  * `"02:00"`
  * `"01:02:10"`

* Tudo é normalizado para **segundos inteiros**

#### 🔍 normalize_time_input

```text
Entrada → valida → converte → retorna:
("HH:MM:SS", segundos)
```

✔️ Evita erro de parsing
✔️ Padroniza o FFmpeg

---

### 4️⃣ Download do Vídeo

```python
stream = yt.streams.filter(progressive=True).get_highest_resolution()
```

#### 🐞 Problema comum

* `get_highest_resolution()` pode falhar dependendo da versão

#### ✅ Correção aplicada

Fallback com:

```python
.order_by("resolution").desc().first()
```

✔️ Garante compatibilidade entre pytube e pytubefix

---

### 5️⃣ Recorte com FFmpeg (PARTE MAIS IMPORTANTE)

#### ❌ Erros clássicos evitados

* Uso de `os.system`
* Tempo final absoluto (ffmpeg espera **duração**)
* Erros de Unicode no stderr

#### ✅ Comando correto gerado

```bash
ffmpeg -ss <inicio> -i video.mp4 -t <duracao> -c copy saida.mp4
```

#### 🧠 Lógica aplicada

```python
duracao = fim - inicio
```

✔️ Evita cortes errados
✔️ Evita vídeo vazio

---

### 6️⃣ subprocess.run (DEBUG ROBUSTO)

```python
subprocess.run(
    comando,
    check=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=False
)
```

#### Por que `text=False`?

✔️ FFmpeg gera bytes inválidos para UTF-8 no Windows
✔️ Evita `UnicodeDecodeError`

---

## 🚨 Validações Importantes

```python
if fim_secs <= inicio_secs:
    raise ValueError("Tempo final deve ser maior")
```

✔️ Evita crashes silenciosos

---

## ✅ Pontos Fortes do Código

* ✔️ Compatível com Windows
* ✔️ Entrada de tempo flexível
* ✔️ Download robusto
* ✔️ Recorte sem re-encode (`-c copy`)
* ✔️ Logs claros
* ✔️ Tratamento de erro real

---

## ⚠️ Limitações Conhecidas

* Não trata vídeos com DRM
* Não baixa resoluções DASH separadas
* Não re-encoda (corte não é frame-perfect)

---

## 🔮 Melhorias Futuras (Sugestões)

* ⏱️ Barra de progresso
* 🎧 Download separado de áudio/vídeo
* 🎞️ Re-encode opcional (`libx264`)
* 🧪 Testes automatizados
* 🖥️ Interface gráfica (Tkinter / Web)

---

## 🧾 Conclusão

O script está **bem estruturado**, **funcional** e com **boas práticas reais de produção**.

O debug aplicado resolve:

* Problemas de tempo
* Erros do FFmpeg no Windows
* Incompatibilidades do pytube

➡️ Pode ser usado como base comercial ou ferramenta profissional.
