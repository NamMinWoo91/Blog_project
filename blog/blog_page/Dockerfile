# Python 3.9 이미지를 기반으로 합니다
FROM python:3.9

# 작업 디렉토리를 설정합니다
WORKDIR /app

# 필요한 파일들을 복사합니다
COPY requirements.txt .
COPY . .

# 필요한 패키지를 설치합니다
RUN pip install -r requirements.txt

# Django의 정적 파일을 수집합니다
RUN python manage.py collectstatic --noinput

# 8000번 포트를 엽니다
EXPOSE 8000

# Gunicorn을 사용하여 Django 애플리케이션을 실행합니다
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]