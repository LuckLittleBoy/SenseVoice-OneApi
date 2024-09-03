# SenseVoice-OneApi
基于SenseVoice的funasr版本进行的api发布，可以无缝对接oneapi

### Docker部署运行
```
# 根据dockerfile构建镜像
docker build -t sensevoice-oneapi:1.0 .
# 通过阿里云镜像仓库拉取
docker pull registry.cn-hangzhou.aliyuncs.com/lucklittleboy/sensevoice-oneapi:1.0
# 运行
注意在运行前如果本地没有提前下载模型，则会通过modelscope自动下载模型
docker run -p 8000:8000 sensevoice-oneapi:1.0
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
