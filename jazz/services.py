"""
/jazz/services.py
: librosa, ffmpeg 작업을 처리하여 반환

- 함수로 model을 넘겨받으면 db수정이 가능함.
- url은 브라우저가 접근하는 주소, path는 서버가 접근하는 주소

subprocess : 외부 프로세스를 실행하는 도구
ffmpeg : 음원 파일을 변환 후 새 파일 생성하는 도구(로컬 터미널에서 동작)
"""

import subprocess
import librosa
from pathlib import Path

from django.conf import settings

from jazz.models import AudioTransformJob

LOOP_BPM_BY_STYLE = {
    "swing": 145.0,
    "lofi": 84.0,
}


def _get_result_path(jazz: AudioTransformJob, suffix: str):
    input_path = Path(jazz.original_file.path)
    result_dir = Path(settings.MEDIA_ROOT) / "audio" / "results"
    result_dir.mkdir(parents=True, exist_ok=True)

    result_filename = f"{input_path.stem}_{suffix}_{jazz.id}.mp3"
    output_path = result_dir / result_filename
    result_file_name = f"audio/results/{result_filename}"

    return output_path, result_file_name


def _build_atempo_filter(speed_ratio: float):
    # ffmpeg의 atempo 필터는 한 번에 0.5~2.0 사이 값만 받을 수 있습니다.
    # 예를 들어 0.25배속이 필요하면 atempo=0.5,atempo=0.5처럼 여러 번 나눠 적용합니다.
    if speed_ratio <= 0:
        raise ValueError("speed_ratio must be greater than 0")

    filters = []

    while speed_ratio < 0.5:
        filters.append("atempo=0.5")
        speed_ratio /= 0.5

    while speed_ratio > 2.0:
        filters.append("atempo=2.0")
        speed_ratio /= 2.0

    filters.append(f"atempo={speed_ratio:.6f}")
    return ",".join(filters)


def set_duration(jazz: AudioTransformJob, path: str):
    import librosa

    jazz.duration = librosa.get_duration(path=path)
    jazz.save(update_fields=['duration'])
    return jazz


def set_status(jazz: AudioTransformJob, stat: str):
    jazz.status = stat
    jazz.save(update_fields=['status'])
    return jazz


def get_bpm(path: str):
    # librosa.load는 오디오 데이터를 실제로 메모리에 올리고, beat_track이 박자 위치를 추정합니다.
    y, sr = librosa.load(path, sr=None, mono=True)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    try:
        return float(tempo)
    except TypeError:
        return float(tempo[0])


def analyze_bpm(jazz: AudioTransformJob):
    bpm = get_bpm(jazz.original_file.path)
    jazz.bpm = bpm
    jazz.save(update_fields=["bpm"])
    return bpm


def get_jazz_loop_path(style: str = "swing"):
    # 재즈 루프는 프로젝트 안에 준비해두는 방식으로 시작합니다.
    # 예: media/audio/loops/swing.mp3
    # 나중에 bossa.mp3, lofi.mp3 같은 파일을 추가하면 style 값으로 선택할 수 있습니다.
    loop_path = Path(settings.MEDIA_ROOT) / "audio" / "loops" / f"{style}.mp3"

    if not loop_path.exists():
        raise FileNotFoundError(
            f"재즈 루프 파일이 없습니다: {loop_path}. "
            "media/audio/loops/ 폴더에 swing.mp3 같은 루프 파일을 추가해주세요."
        )

    return loop_path


def mix_jazz_loop(jazz: AudioTransformJob, loop_path=None, loop_bpm=None):
    jazz = set_status(jazz, AudioTransformJob.Status.PROCESSING)

    try:
        input_path = Path(jazz.original_file.path)
        loop_path = Path(loop_path) if loop_path else get_jazz_loop_path(jazz.style)
        loop_bpm = loop_bpm or LOOP_BPM_BY_STYLE.get(jazz.style, 145.0)
        output_path, result_file_name = _get_result_path(jazz, "loop_mix")

        # 원본 BPM이 DB에 없으면 여기서 다시 분석합니다.
        # 업로드 시 analyze_bpm(jazz)를 이미 호출했다면 jazz.bpm 값을 그대로 사용합니다.
        target_bpm = jazz.bpm or analyze_bpm(jazz)
        speed_ratio = target_bpm / loop_bpm
        atempo_filter = _build_atempo_filter(speed_ratio)

        # -stream_loop -1은 루프 파일을 무한 반복시킵니다.
        # amix의 duration=first 때문에 최종 결과는 원본 음원 길이에 맞춰 끝납니다.
        # loop는 145 BPM 기준 파일이므로, 원본 BPM / 145 비율로 먼저 tempo를 맞춘 뒤 섞습니다.
        filter_complex = (
            "[0:a]volume=0.85[original];"
            f"[1:a]{atempo_filter},volume=0.35,highpass=f=90,lowpass=f=12000[loop];"
            "[original][loop]amix=inputs=2:duration=first:dropout_transition=2,"
            "volume=0.95[mixed]"
        )

        command = [
            "ffmpeg",
            "-y",
            "-i", str(input_path),
            "-stream_loop", "-1",
            "-i", str(loop_path),
            "-filter_complex", filter_complex,
            "-map", "[mixed]",
            "-vn",
            str(output_path),
        ]

        subprocess.run(command, check=True, capture_output=True, text=True)

        jazz.result_file.name = result_file_name
        jazz.status = AudioTransformJob.Status.COMPLETED
        jazz.error_message = ""
        jazz.save(update_fields=["result_file", "status", "error_message"])

    except Exception as exc:
        jazz.status = AudioTransformJob.Status.FAILED
        jazz.error_message = str(exc)
        jazz.save(update_fields=["status", "error_message"])

    return jazz


def transformToJazz(jazz: AudioTransformJob):
    jazz = set_status(jazz, AudioTransformJob.Status.PROCESSING)

    try:
        input_path = Path(jazz.original_file.path)

        # FileField의 .url은 브라우저용 주소이고, ffmpeg는 서버의 실제 파일 경로가 필요합니다.
        # 그래서 original_file.url이 아니라 original_file.path를 Path 객체로 바꿔서 사용합니다.
        output_path, result_file_name = _get_result_path(jazz, "jazz")

        # 지금은 진짜 재즈 편곡이 아니라 "처리 파이프라인 확인용" 가짜 변환입니다.
        # - highpass: 너무 낮은 저역 잡음을 조금 줄임
        # - lowpass: 과하게 날카로운 고역을 조금 정리
        # - equalizer: 중저역을 살짝 올려 더 따뜻한 느낌을 줌
        # - aecho: 공간감/잔향 느낌을 추가
        # - volume: 전체 볼륨을 살짝 낮춰 clipping 가능성을 줄임
        audio_filter = (
            "highpass=f=80,"
            "lowpass=f=12000,"
            "equalizer=f=250:t=q:w=1:g=2,"
            "aecho=0.8:0.88:600:0.22,"
            "volume=0.9"
        )

        command = [
            "ffmpeg",
            "-y",  # 같은 이름의 결과 파일이 이미 있으면 덮어씁니다.
            "-i", str(input_path),
            "-filter:a", audio_filter,
            "-vn",  # 혹시 입력 파일에 영상 스트림이 있어도 오디오만 출력합니다.
            str(output_path),
        ]

        subprocess.run(command, check=True, capture_output=True, text=True)

        # ffmpeg가 만든 실제 파일은 MEDIA_ROOT/audio/results/ 안에 있습니다.
        # DB에는 MEDIA_ROOT 기준의 상대 경로를 넣어야 브라우저에서 result_file.url이 잘 만들어집니다.
        jazz.result_file.name = result_file_name
        jazz.status = AudioTransformJob.Status.COMPLETED
        jazz.error_message = ""
        jazz.save(update_fields=["result_file", "status", "error_message"])

    except Exception as exc:
        jazz.status = AudioTransformJob.Status.FAILED
        jazz.error_message = str(exc)
        jazz.save(update_fields=["status", "error_message"])

    return jazz
