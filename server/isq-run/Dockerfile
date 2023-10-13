FROM arclightquantum/isq:latest

LABEL author="kahsolt"
LABEL email="kahsolt@qq.com"

RUN apt update
RUN apt -y install python3 python3-pip

WORKDIR /isq

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY app.py .
ENV PORT 5001
EXPOSE 5001
CMD ["python3", "app.py"]
