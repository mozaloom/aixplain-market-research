FROM public.ecr.aws/lambda/python:3.12

# Set cache directories to writable /tmp
ENV HOME=/tmp
ENV XDG_CACHE_HOME=/tmp/.cache
ENV TMPDIR=/tmp
ENV PYTHONPATH=/var/task

# Copy requirements first for better caching
COPY requirements.txt /tmp/
WORKDIR /tmp
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files to /var/task (Lambda default)
WORKDIR /var/task
COPY api.py agent.py tools.py ./

# Create cache directory and set permissions
RUN mkdir -p /tmp/.cache && chmod 777 /tmp/.cache

# Set the handler
CMD ["api.handler"]