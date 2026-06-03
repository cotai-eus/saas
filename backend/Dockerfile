FROM python:3.12-slim@sha256:090ba77e2958f6af52a5341f788b50b032dd4ca28377d2893dcf1ecbdfdfe203
RUN addgroup --system --gid 1001 app && \
    adduser --system --uid 1001 --ingroup app app
WORKDIR /app
COPY --chown=app:app pyproject.toml .
COPY --chown=app:app src/ ./src/
RUN pip install --no-cache-dir . && pip list
USER app
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]