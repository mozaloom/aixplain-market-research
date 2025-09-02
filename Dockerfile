FROM public.ecr.aws/lambda/python:3.12

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY api.py market_research_advanced.py ./

# Set the handler
CMD ["api.handler"]