# 使用 miniconda3 镜像作为基础镜像
FROM ubuntu:latest

# 设置环境变量
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

# 使用国内镜像源
RUN sed -i 's/archive.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list
# 设置系统时区为上海
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 更新 apt-get 软件包列表并安装 GCC
RUN apt-get update && \
    apt-get install -y gcc make wget tzdata && \
    rm -rf /var/lib/apt/lists/*

# 将容器的默认用户设置为 root
USER root

# 设置工作目录
WORKDIR /app

COPY . .
RUN mv strategies /root/strategies && mv .myleap /root/.myleap

# 添加 Miniconda 到 PATH 环境变量
# RUN bash tools/Miniconda3-latest-Linux-x86_64.sh -b -p /opt/miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-py38_23.1.0-1-Linux-x86_64.sh && bash Miniconda3-py38_23.1.0-1-Linux-x86_64.sh -p /opt/miniconda -b && rm Miniconda3-py38_23.1.0-1-Linux-x86_64.sh
ENV PATH=/opt/miniconda/bin:$PATH

# 创建并激活 Conda 环境，并安装依赖项
RUN conda create -n myleap python=3.8 && echo "conda activate myleap" > ~/.bashrc
ENV PATH /opt/miniconda/envs/myleap/bin:$PATH
RUN cd tools && tar -zxvf ta-lib-0.4.0-src.tar.gz && rm ta-lib-0.4.0-src.tar.gz && cd ta-lib && ./configure && make && make install 
RUN pip install -r requirements.txt

# 暴露应用程序需要的端口
EXPOSE 8080

# 定义启动命令
CMD ["python", "run_noui.py"]
