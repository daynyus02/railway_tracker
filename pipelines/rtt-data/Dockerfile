FROM public.ecr.aws/lambda/python:latest

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY extract.py .
COPY transform.py .
COPY load.py .
COPY main.py .

CMD ["main.lambda_handler"]