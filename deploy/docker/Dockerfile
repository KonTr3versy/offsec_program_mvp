FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Install system deps (optional minimal)
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY offsec_program_mvp ./offsec_program_mvp

# Environment variables
ENV DATABASE_URL=sqlite:///./offsec_program.db
ENV REQUIRE_API_KEY=true
ENV OFFSEC_ENV=prod

EXPOSE 8000

CMD ["uvicorn", "offsec_program_mvp.main:app", "--host", "0.0.0.0", "--port", "8000"]
