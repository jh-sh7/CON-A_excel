# CON-A Excel 데이터 처리 웹 애플리케이션

Flask 기반의 Excel 데이터 처리 웹 애플리케이션입니다.

## 기능

- 번호 1 또는 2를 입력하여 CON-A DB1.xlsx에서 데이터 추출
- 대가 시트와 집계 시트 자동 생성
- Excel 파일 다운로드 기능

## 로컬 실행

```bash
# 가상환경 생성 (선택사항)
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python app.py
```

브라우저에서 http://localhost:5000 접속

## 배포 방법

### 1. Railway (추천 - 무료 플랜 제공)

1. https://railway.app 접속 및 회원가입
2. "New Project" → "Deploy from GitHub repo" 선택
3. GitHub에 코드 푸시 후 연결
4. 환경 변수 설정 (필요시)
5. 자동 배포 완료

### 2. Render

1. https://render.com 접속 및 회원가입
2. "New" → "Web Service" 선택
3. GitHub 저장소 연결
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `python app.py`
6. 배포 완료

### 3. Heroku

1. https://heroku.com 접속 및 회원가입
2. Heroku CLI 설치
3. 다음 명령어 실행:

```bash
heroku create your-app-name
git push heroku main
```

### 4. PythonAnywhere

1. https://www.pythonanywhere.com 접속 및 회원가입
2. Files 탭에서 코드 업로드
3. Web 탭에서 WSGI 설정
4. Reload 버튼 클릭

## 중요 사항

- `data/CON-A DB1.xlsx` 파일이 서버에 있어야 합니다
- 배포 시 파일 경로가 올바른지 확인하세요
- 세션 데이터는 메모리에 저장되므로 서버 재시작 시 초기화됩니다
