# Use officail Python base image
FROM python:3.13-slim   

# Set the working directory in the container
WORKDIR /app

# Copy dependency file and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY app.py /app/app.py
COPY ui /app/ui
COPY tests /app/tests
COPY logs /app/logs
COPY README.md /app/README.md

# Expose the port the app runs on
EXPOSE 8501

# Default commend: run tests. You can override this in docker run time to launch Streamlit.
CMD ["pytest", "tests/"]