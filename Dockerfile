FROM python:3.12-slim

WORKDIR /app

# time zone
ENV TZ=Asia/Novosibirsk
RUN apt-get update && apt-get install -y tzdata
RUN ln -fs /usr/share/zoneinfo/Asia/Novosibirsk /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

# install uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

# install python-dependencies
COPY . .
RUN uv sync --locked

CMD ["uv", "run", "bot_main.py"]

