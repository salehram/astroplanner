FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for astropy; tweak for Raspberry Pi as needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libcfitsio-dev \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PORT=5000

# Default observer location (Riyadh)
ENV OBSERVER_LAT=24.7136
ENV OBSERVER_LON=46.6753
ENV OBSERVER_ELEV_M=600

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
