FROM python:3.12.2



WORKDIR python-web-module-2


COPY . .




EXPOSE 5000


ENTRYPOINT ["python", "dz1.py"]