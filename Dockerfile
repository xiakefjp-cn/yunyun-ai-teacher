FROM python:3.12-slim
WORKDIR /srv/yunyun
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
COPY app ./app
COPY web ./web
COPY demo_workspace ./seeds
RUN useradd --uid 10001 --create-home teacher && mkdir /workspace && chown -R teacher:teacher /srv/yunyun /workspace
USER teacher
EXPOSE 8765
CMD ["python", "-m", "app.container"]
