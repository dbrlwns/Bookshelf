"""
Minimal soft-piano jazz remix pipeline.

이 파일은 기존 services.py를 대체하지 않는 검토용 버전입니다.
흐름만 작게 유지합니다:
1. Demucs로 vocals / no_vocals 분리
2. no_vocals.wav를 rubberband로 느리게 변경
3. soft_piano.mp3를 ducking으로 섞기
4. AudioTransformJob에 결과 저장
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from django.conf import settings

from jazz.models import AudioTransformJob


DEMUCS_MODEL = "htdemucs"
DEMUCS_DEVICE = "cpu"
DEMUCS_JOBS = "1"
BACKING_SPEED = 0.72
BACKING_VOLUME = 0.82
LOOP_VOLUME = 0.2176
VINYL_NOISE = 0.003
DUCK_THRESHOLD = 0.08
DUCK_RATIO = 10.0
DUCK_ATTACK = 15
DUCK_RELEASE = 450


def _media_path(*parts: str) -> Path:
    return Path(settings.MEDIA_ROOT).joinpath(*parts)


def _soft_piano_loop_path() -> Path:
    loop_path = _media_path("audio", "loops", "soft_piano.mp3")
    if not loop_path.exists():
        raise FileNotFoundError(f"soft_piano loop not found: {loop_path}")
    return loop_path


def _result_path(job: AudioTransformJob) -> tuple[Path, str]:
    result_dir = _media_path("audio", "results")
    result_dir.mkdir(parents=True, exist_ok=True)

    input_stem = Path(job.original_file.path).stem
    filename = f"{input_stem}_soft_piano_{job.id}.mp3"
    return result_dir / filename, f"audio/results/{filename}"


def _stem_output_dir(job: AudioTransformJob) -> Path:
    stem_dir = _media_path("audio", "stems", f"job_{job.id}")
    stem_dir.mkdir(parents=True, exist_ok=True)
    return stem_dir


def _demucs_env() -> dict[str, str]:
    env = os.environ.copy()
    cache_dir = _media_path("audio", "cache")
    torch_home = cache_dir / "torch"
    xdg_cache_home = cache_dir / "xdg"
    xdg_config_home = cache_dir / "config"

    for directory in (torch_home, xdg_cache_home, xdg_config_home):
        directory.mkdir(parents=True, exist_ok=True)

    env["TORCH_HOME"] = str(torch_home)
    env["XDG_CACHE_HOME"] = str(xdg_cache_home)
    env["XDG_CONFIG_HOME"] = str(xdg_config_home)

    checkpoint = getattr(settings, "DEMUCS_CHECKPOINT_PATH", "")
    if checkpoint:
        checkpoint_path = Path(checkpoint).expanduser()
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Demucs checkpoint not found: {checkpoint_path}")

        checkpoint_dir = torch_home / "hub" / "checkpoints"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        cached_checkpoint = checkpoint_dir / checkpoint_path.name
        if not cached_checkpoint.exists():
            shutil.copy2(checkpoint_path, cached_checkpoint)

    return env


def _run_command(command: list[str], *, env: dict[str, str] | None = None) -> None:
    result = subprocess.run(command, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(detail or f"Command failed: {' '.join(command)}")


def separate_no_vocals(job: AudioTransformJob, *, reuse: bool = True) -> Path:
    """
    Demucs two-stems 모드로 보컬을 제거하고 no_vocals.wav 경로를 반환합니다.
    WAV를 쓰는 이유는 MP3 중간 저장으로 생기는 손실을 줄이기 위해서입니다.
    """
    input_path = Path(job.original_file.path)
    output_dir = _stem_output_dir(job)
    track_dir = output_dir / DEMUCS_MODEL / input_path.stem
    no_vocals_path = track_dir / "no_vocals.wav"

    if reuse and no_vocals_path.exists():
        return no_vocals_path

    command = [
        sys.executable,
        "-m",
        "demucs",
        "--name",
        DEMUCS_MODEL,
        "--out",
        str(output_dir),
        "--device",
        DEMUCS_DEVICE,
        "--jobs",
        DEMUCS_JOBS,
        "--two-stems",
        "vocals",
        str(input_path),
    ]
    _run_command(command, env=_demucs_env())

    if not no_vocals_path.exists():
        raise FileNotFoundError(f"Demucs output not found: {no_vocals_path}")
    return no_vocals_path


def stretch_backing_with_rubberband(no_vocals_path: Path, output_path: Path) -> Path:
    """
    rubberband로 반주 속도를 낮춥니다.
    ffmpeg atempo보다 음악 time-stretch 품질이 나은 편입니다.
    """
    if not shutil.which("rubberband"):
        raise RuntimeError("rubberband command not found. Install it with: brew install rubberband")

    stretched_path = output_path.with_suffix(".backing_stretched.wav")
    command = [
        "rubberband",
        "--fine",
        "--centre-focus",
        "--tempo",
        str(BACKING_SPEED),
        str(no_vocals_path),
        str(stretched_path),
    ]
    _run_command(command)
    return stretched_path


def mix_soft_piano_loop(backing_path: Path, output_path: Path) -> None:
    """
    soft_piano loop를 backing에 섞습니다.
    sidechaincompress가 backing 소리를 trigger로 사용해서 loop가 치고 빠지게 만듭니다.
    """
    loop_path = _soft_piano_loop_path()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    filters = [
        f"[0:a]volume={BACKING_VOLUME},highpass=f=45,lowpass=f=8500,"
        "equalizer=f=220:t=q:w=1.1:g=-1.5,"
        "equalizer=f=1200:t=q:w=1.0:g=1.0[backing_base]",
        f"[1:a]volume={LOOP_VOLUME},highpass=f=70,lowpass=f=12000[loop]",
        "[backing_base]asplit=2[backing][duck_trigger]",
        "[loop][duck_trigger]"
        f"sidechaincompress=threshold={DUCK_THRESHOLD}:ratio={DUCK_RATIO}:"
        f"attack={DUCK_ATTACK}:release={DUCK_RELEASE}:makeup=1[loop_ducked]",
        f"anoisesrc=color=pink:amplitude={VINYL_NOISE}[noise]",
        "[backing][loop_ducked][noise]amix=inputs=3:duration=first:dropout_transition=2,"
        "alimiter=limit=0.95,volume=0.95[mixed]",
    ]

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(backing_path),
        "-stream_loop",
        "-1",
        "-i",
        str(loop_path),
        "-filter_complex",
        ";".join(filters),
        "-map",
        "[mixed]",
        "-vn",
        str(output_path),
    ]
    _run_command(command)


def transform_soft_piano_jazz(job: AudioTransformJob, *, reuse_stems: bool = True) -> AudioTransformJob:
    """
    Django/Celery에서 호출할 최소 진입점입니다.
    아직 기존 tasks.py에는 연결하지 않았습니다.
    """
    job.status = AudioTransformJob.Status.PROCESSING
    job.error_message = ""
    job.save(update_fields=["status", "error_message"])

    try:
        output_path, result_file_name = _result_path(job)
        no_vocals_path = separate_no_vocals(job, reuse=reuse_stems)
        backing_path = stretch_backing_with_rubberband(no_vocals_path, output_path)
        mix_soft_piano_loop(backing_path, output_path)

        job.result_file.name = result_file_name
        job.status = AudioTransformJob.Status.COMPLETED
        job.error_message = ""
        job.style = "soft_piano"
        job.save(update_fields=["result_file", "status", "error_message", "style"])
    except Exception as exc:
        job.status = AudioTransformJob.Status.FAILED
        job.error_message = str(exc)
        job.save(update_fields=["status", "error_message"])

    return job
