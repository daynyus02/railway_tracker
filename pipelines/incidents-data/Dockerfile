FROM public.ecr.aws/lambda/python:3.13

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY extract_incidents.py .
COPY transform_incidents.py .
COPY load_incidents.py .
COPY main_incidents.py .

CMD ["main_incidents.lambda_handler"]