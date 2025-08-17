# Whisper Transcription Project

OpenAI Whisperを使用した音声文字起こしツール。ローカルの音声ファイルとYouTube動画の両方に対応し、プロジェクトベースの組織化された管理システムを提供します。

## 機能

- **ローカル音声ファイルの文字起こし**: 各種音声形式に対応
- **YouTube動画の文字起こし**: ライブ配信含む動画から音声抽出・文字起こし
- **プロジェクト管理**: 音声ファイルごとに整理されたディレクトリ構造
- **複数出力形式**: テキスト、SRT、VTT、JSON形式で保存
- **設定保存**: トランスクリプション設定とメタデータの自動保存
- **多言語対応**: 自動言語検出または手動指定
- **複数モデル**: tiny〜largeまでのWhisperモデルから選択可能

## セットアップ

### 1. 依存関係のインストール

```bash
# Python仮想環境の作成（推奨）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows

# 必要なパッケージのインストール
pip install -r requirements.txt
```

### 2. FFmpegのインストール

音声処理にFFmpegが必要です：

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
[FFmpeg公式サイト](https://ffmpeg.org/download.html)からダウンロードしてインストール

## 使用方法

### プロジェクト一覧の確認

```bash
python main.py list

# 出力例：
# === Audio Projects ===
# 📁 youtube_nbedH0FLLyw
#    Title: MIKI 雀聖計画 2025 お試し配信
#    Duration: 1689 seconds
#    Type: youtube
#    Audio: ✓
#    Transcription: ✓
```

### ローカル音声ファイルの文字起こし

```bash
python main.py audio <音声ファイルパス> [オプション]

# 例：
python main.py audio sample.mp3
python main.py audio interview.wav -m small -l ja -f text
```

**プロジェクト構造**：
- `audio_projects/local_<ファイル名>/`
  - `src_audio/`: 元の音声ファイル
  - `transcription/`: 文字起こし結果
  - `metadata.json`: ファイル情報

### YouTube動画の文字起こし

```bash
python main.py youtube <YouTubeURL> [オプション]

# 例：
python main.py youtube https://youtube.com/watch?v=VIDEO_ID
python main.py youtube https://youtube.com/live/nbedH0FLLyw -m small -l ja
```

**プロジェクト構造**：
- `audio_projects/youtube_<VIDEO_ID>/`
  - `src_audio/`: ダウンロードした音声ファイル
  - `transcription/`: 文字起こし結果とSettings
  - `metadata.json`: 動画情報（タイトル、アップローダー等）

### オプション

**共通オプション:**
- `-m, --model`: Whisperモデルサイズ (tiny, base, small, medium, large)
  - デフォルト: base
- `-l, --language`: 言語コード（例: 'ja'=日本語, 'en'=英語）
  - 指定しない場合は自動検出
- `-f, --format`: 出力形式 (text, srt, vtt, json, all)
  - デフォルト: all

**YouTube専用オプション:**
- `-a, --audio-format`: ダウンロード音声形式 (mp3, wav, m4a)
  - デフォルト: mp3
- `-k, --keep-audio`: ダウンロードした音声ファイルを保持
  - 注意: 新しいプロジェクト構造では音声ファイルは自動的にプロジェクトフォルダに保存されます

## モデルサイズの選択

| モデル | サイズ | 必要VRAM | 速度 | 精度 |
|--------|--------|----------|------|------|
| tiny   | 39 MB  | ~1 GB    | 最速 | 低   |
| base   | 74 MB  | ~1 GB    | 速い | 中   |
| small  | 244 MB | ~2 GB    | 中   | 中高 |
| medium | 769 MB | ~5 GB    | 遅い | 高   |
| large  | 1550 MB| ~10 GB   | 最遅 | 最高 |

## プロジェクト構造と出力ファイル

各音声ファイルは独立したプロジェクトとして管理されます：

```
audio_projects/
├── youtube_nbedH0FLLyw/              # YouTube動画プロジェクト
│   ├── src_audio/
│   │   └── nbedH0FLLyw.mp3          # ダウンロード音声
│   ├── transcription/
│   │   ├── transcript.txt           # プレーンテキスト
│   │   ├── transcript.srt           # SubRip字幕形式
│   │   ├── transcript.vtt           # WebVTT字幕形式
│   │   ├── transcript.json          # タイムスタンプ付き詳細データ
│   │   └── settings.json            # トランスクリプション設定
│   └── metadata.json                # 動画メタデータ
└── local_interview/                  # ローカル音声プロジェクト
    ├── src_audio/
    │   └── interview.wav
    ├── transcription/
    │   ├── transcript.txt
    │   ├── transcript.srt
    │   ├── transcript.vtt
    │   ├── transcript.json
    │   └── settings.json
    └── metadata.json
```

### 保存される情報

**metadata.json（YouTube）**:
- 動画タイトル、アップローダー、再生時間
- アップロード日、視聴回数
- 元のURL、ビデオID

**metadata.json（ローカル）**:
- ファイル名、ファイルサイズ
- 処理日時、ソースタイプ

**settings.json**:
- 使用したWhisperモデル
- 言語設定、出力形式
- 処理日時

## トラブルシューティング

### CUDA/GPUサポート

GPUを使用する場合は、PyTorchのCUDA版をインストール：
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### メモリ不足エラー

大きなモデルでメモリ不足が発生する場合は、より小さなモデル（tiny, base）を使用してください。

### 既存ファイルとの競合

新しいプロジェクト構造では、古い`transcriptions/`や`audio_files/`ディレクトリは使用されません。これらは安全に削除できます。

## 実行例

```bash
# YouTube動画の文字起こし（smallモデル、日本語）
python main.py youtube "https://youtube.com/live/nbedH0FLLyw" -m small -l ja

# プロジェクト一覧の確認
python main.py list

# ローカルファイルの文字起こし
python main.py audio /path/to/audio.mp3 -m base -l ja
```

## ライセンス

このプロジェクトはMITライセンスです。