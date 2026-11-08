FROM python:3.11-slim
RUN useradd -r -u 10001 lab
WORKDIR /app
COPY python-pickle/app.py /app/app.py
COPY python-pickle/generate.py /app/generate.py
COPY web/server.py /app/server.py
ENV APP_NAME="Python / pickle" LAB_COMMAND="python3 /app/app.py"
USER lab
EXPOSE 8080
CMD ["python3", "-u", "/app/server.py"]
