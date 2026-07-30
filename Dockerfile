FROM mcr.microsoft.com/playwright/python:v1.61.0-jammy

WORKDIR /app

# Pip önbelleğini kapatıp kurulumu hızlandıralım
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "tarayici.py"]
