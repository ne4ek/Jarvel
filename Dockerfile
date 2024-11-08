FROM python:3.10.13

WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
    tzdata \
    ffmpeg

ENV TZ=Europe/Moscow
RUN ln -sf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["python", "main.py"]