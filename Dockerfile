FROM python:3.12

# Create a non-root user
RUN useradd -ms /bin/bash vscode

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Change ownership to the non-root user
RUN chown -R vscode:vscode /app

# Switch to the non-root user
USER vscode

# Expose the port the app runs on
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

# Run the application
CMD ["flask", "run", "--host=0.0.0.0"]