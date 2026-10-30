FROM python:3.14-slim
WORKDIR /srv/yunyun
COPY app ./app
COPY web ./web
COPY demo_workspace ./demo_workspace
RUN useradd -m teacher && chown -R teacher:teacher /srv/yunyun
USER teacher
EXPOSE 8765
CMD ["python", "-m", "app.server", "--host", "0.0.0.0", "--workspace", "demo_workspace"]
