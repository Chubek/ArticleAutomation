FROM python:3
WORKDIR /code
ADD LushaScrape.py /
RUN pip install -r requirements.txt
CMD [ "python", "./LushaScrape.py" ]