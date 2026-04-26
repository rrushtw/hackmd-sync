# Self-contained image for the HackMD CLI. The hackmd.sh wrapper rebuilds this
# image whenever hackmd.py is newer than the existing image's creation time.
FROM python:3.12-slim
COPY hackmd.py /app/hackmd.py
ENTRYPOINT ["python", "/app/hackmd.py"]
