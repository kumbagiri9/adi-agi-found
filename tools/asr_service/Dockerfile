FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn pydantic
COPY app.py /app/app.py
EXPOSE 7001
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","7001"]
