FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY server.py .
COPY resume_data.json .
COPY evaluations.py .

# Expose port for MCP server
EXPOSE 8000

# Run the server
CMD ["python", "server.py"]