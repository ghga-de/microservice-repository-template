FROM python:3.9-slim

WORKDIR /service
COPY . /service
RUN pip install -r requirements.txt

EXPOSE 5000

# create new user and execute as that user
RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

ENTRYPOINT ["python"]
CMD [ "./src/app.py" ]
