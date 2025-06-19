FROM public.ecr.aws/lambda/python:3.13

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY extract_reports.py .
COPY transform_summary.py .
COPY load_reports.py .
COPY main_reports.py .

CMD ["main_reports.lambda_handler"]