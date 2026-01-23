FROM python:3.8-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir aiokafka==0.8.1 kafka-python==2.0.2

# Copy script
COPY data_generator.py .

# Run as non-root
RUN useradd -m appuser
USER appuser

CMD ["python", "-u", "data_generator.py"]
