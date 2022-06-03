FROM gcr.io/google-appengine/python 
LABEL python_version=python3.6
RUN virtualenv --no-download /env -p python3.6
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH
RUN apt-get update \
 && apt-get install -y libgl1-mesa-glx && pip install --upgrade pip && apt-get install -y poppler-utils 
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD exec gunicorn -b :$PORT extractor.wsgi:application