# MATer_2 - 수학 문제 풀이 도우미

MATer_2는 사용자가 모르는 수학 문제를 이미지로 업로드하면, AI가 2가지 다른 풀이 방법으로 정답과 과정을 제시하고, 개념 설명과 유사한 문제를 제공하는 웹 애플리케이션입니다.

## 주요 기능

1. **이미지 업로드**: 수학 문제 이미지를 업로드 (드래그 앤 드롭 지원)
2. **2가지 풀이 방법**: 서로 다른 접근 방식으로 문제를 풀이
3. **개념 설명**: 문제에서 사용된 수학 개념을 자세히 설명
4. **유사 문제 생성**: 비슷한 난이도의 문제를 자동 생성
5. **개발자 정보**: 개발자 신승원의 정보 확인

## 설치 및 실행

### 1. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

OpenAI API 키를 설정해야 합니다 (선택사항, 없으면 데모 모드로 작동):

```bash
# Windows
set OPENAI_API_KEY=your_api_key_here

# Linux/Mac
export OPENAI_API_KEY=your_api_key_here
```

### 3. 애플리케이션 실행

```bash
python mater2_app.py
```

브라우저에서 `http://localhost:5000`으로 접속하세요.

## 사용 방법

1. 웹사이트에 접속합니다.
2. 수학 문제 이미지를 업로드합니다 (클릭하거나 드래그 앤 드롭).
3. "문제 풀기" 버튼을 클릭합니다.
4. 2가지 풀이 방법, 개념 설명, 유사 문제를 확인합니다.
5. 상단의 "개발자 정보" 버튼을 클릭하여 개발자 정보를 확인할 수 있습니다.

## 기술 스택

- **Backend**: Flask (Python)
- **AI**: OpenAI GPT-4o Vision API
- **Frontend**: HTML, CSS, JavaScript
- **이미지 처리**: Pillow

## 파일 구조

```
.
├── mater2_app.py          # Flask 애플리케이션 메인 파일
├── templates/
│   └── mater2_index.html  # 메인 HTML 템플릿
├── uploads/               # 업로드된 이미지 임시 저장 폴더
└── requirements.txt       # Python 패키지 의존성
```

## 주의사항

- OpenAI API 키가 없으면 데모 모드로 작동하며, 실제 AI 분석은 제공되지 않습니다.
- 이미지 파일 크기는 최대 16MB까지 지원됩니다.
- 지원 이미지 형식: PNG, JPG, JPEG, GIF, WEBP

## 개발자

**신승원**

"안녕하세요, MATer_2 개발자 신승원 입니다. 모르는 수학 문제는 더 강하고 자세한 MATer_2에서 도움을 받으세요! 수학을 더 재밌고 쉽게! MATer_2."
