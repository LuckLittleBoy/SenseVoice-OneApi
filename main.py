# -*- coding: utf-8 -*-
import os
import logging
import uvicorn
import ffmpeg
import numpy as np
from typing import BinaryIO
from fastapi import FastAPI, File, UploadFile, HTTPException
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess

SAMPLE_RATE = 16000

# 模型加载
model_path = os.getenv("MODEL_PATH", "iic/SenseVoiceSmall")

# 支持任意时长音频输入
vad_enable = os.getenv("VAD_ENABLE", False)

# 推理方式
device_type = os.getenv("DEVICE_TYPE", "cpu")

# 设置用于 CPU 内部操作并行性的线程数
cpu_num = os.getenv("ncpu", 4)

# 语言
language = os.getenv("language", "zh")

batch_size = os.getenv("batch_size", 64)

use_itn = os.getenv("use_itn", False)

app = FastAPI()

if vad_enable:
    # 准确预测
    model = AutoModel(
        model=model_path,
        vad_model="fsmn-vad",
        vad_kwargs={"max_single_segment_time": 30000},
        trust_remote_code=False,
        device=device_type,
        ncpu=cpu_num,
        disable_update=True
    )
else:
    # 快速预测
    model = AutoModel(
        model=model_path,
        trust_remote_code=False,
        device=device_type,
        ncpu=cpu_num,
        disable_update=True
    )

@app.post("/v1/chat/completions")
async def test():
    logging.warning("oneapi channel test")
    return {"message": ""}


@app.post("/v1/audio/transcriptions")
async def transcriptions(file: UploadFile = File(...)):
    try:
        logging.warning(f"oneapi audio transcriptions, file content type is {file.content_type}")

        data = load_audio(file.file)

        res = model.generate(
            input=data,
            cache={},
            language=language,
            use_itn=use_itn,
            batch_size=batch_size,
        )

        result = rich_transcription_postprocess(res[0]["text"])

        logging.warning(result)

        return {"text": result}
    except Exception as e:
        logging.exception(e)
        raise HTTPException(status_code=500, detail=str(e))

def load_audio(file: BinaryIO, encode=True, sr: int = SAMPLE_RATE):
    """
    Open an audio file object and read as mono waveform, resampling as necessary.
    Modified from https://github.com/openai/whisper/blob/main/whisper/audio.py to accept a file object
    Parameters
    ----------
    file: BinaryIO
        The audio file like object
    encode: Boolean
        If true, encode audio stream to WAV before sending to whisper
    sr: int
        The sample rate to resample the audio if necessary
    Returns
    -------
    A NumPy array containing the audio waveform, in float32 dtype.
    """
    if encode:
        try:
            # This launches a subprocess to decode audio while down-mixing and resampling as necessary.
            # Requires the ffmpeg CLI and `ffmpeg-python` package to be installed.
            out, _ = (
                ffmpeg.input("pipe:", threads=0)
                .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=sr)
                .run(cmd="ffmpeg", capture_stdout=True, capture_stderr=True, input=file.read())
            )
        except ffmpeg.Error as e:
            raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

    return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0

if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)
