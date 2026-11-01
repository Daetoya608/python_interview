FROM python:3.11-slim
WORKDIR /app
RUN groupadd --gid 10001 app && useradd --uid 10001 --gid app --no-create-home app \
    && mkdir /data && chown app:app /data
COPY app.py .
USER 10001:10001
ENV DATA_DIR=/data
EXPOSE 8000
CMD ["python", "app.py"]
