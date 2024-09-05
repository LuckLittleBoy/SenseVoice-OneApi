# SenseVoice-OneApi
基于SenseVoice的funasr版本进行的api发布，可以无缝对接oneapi

### 模型下载
通过modelscope下载iic/SenseVoiceSmall和iic/speech_fsmn_vad_zh-cn-16k-common-pytorch
```
pip install modelscope
modelscope download --model iic/SenseVoiceSmall --local_dir ./iic/SenseVoiceSmall
modelscope download --model iic/speech_fsmn_vad_zh-cn-16k-common-pytorch --local_dir ./iic/speech_fsmn_vad_zh-cn-16k-common-pytorch
```

### Docker部署运行
```
# 根据dockerfile构建镜像
docker build -t sensevoice-oneapi:1.0 .
# 通过阿里云镜像仓库拉取，只包含SenseVoiceSmall模型，无需再下载
docker pull registry.cn-hangzhou.aliyuncs.com/lucklittleboy/sensevoice-oneapi:1.0
# 运行
# 注意在运行前如果本地没有提前下载模型，则会通过modelscope自动下载模型
docker run -d --name=sensevoice -p 8000:8000 -v /home/iic:/app/iic sensevoice-oneapi:1.0
```

### 本地安装运行
```
# 安装依赖
pip install -r requirements.txt
# 运行
python main.py
```

### 指定推理方式
默认使用CPU
```
CPU：docker run时增加 -e DEVICE_TYPE=cpu
GPU：docker run时增加 -e DEVICE_TYPE=cuda:0
```

### 接口测试
```
curl --request POST 'http://127.0.0.1:8000/v1/audio/transcriptions' \
--header 'Content-Type: multipart/form-data' \
--form 'file=@audio/asr_example_zh.wav'
```
返回结果
{"text": "欢迎大家来体验达摩院推出的语音识别模型"}

### 接入One Api
渠道类型使用OpenAI或者自定义渠道
模型填入whisper-1
代理填写对应的地址：http://ip:8000

### 终语
请施舍一个star吧
