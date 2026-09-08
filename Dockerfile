FROM python:3.11-slim

WORKDIR /workspace

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p tests/generated reports eval/tasks/stack eval/tasks/fibonacci \
    eval/tasks/flatten eval/tasks/binary_tree eval/tasks/text_stats

RUN python prepare_data.py

ENV TGEN_DEVICE=cpu
ENV TGEN_SEED=42
ENV TGEN_MODE=full
ENV TGEN_COVERAGE_THRESHOLD=0.80
ENV TGEN_MAX_TESTS=50

CMD ["bash"]
