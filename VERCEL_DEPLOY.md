# Vercel 배포 가이드 - QUAZ 갤러리

## 프로젝트 정보
- **프로젝트 이름**: QUAZ 갤러리 (네이비 블루 게시판)
- **기능**: 게시물 CRUD, 댓글/대댓글, 검색, 트렌드 페이지, 장르 필터

## GitHub 푸시 완료 ✅
코드가 성공적으로 GitHub에 푸시되었습니다:
- Repository: `https://github.com/jh-sh7/CON-A_excel.git`
- Branch: `main`
- **참고**: 저장소 이름은 CON-A_excel이지만, 메인 프로젝트는 QUAZ 갤러리입니다.

## Vercel 배포 방법

### 방법 1: Vercel 웹 대시보드 사용 (추천)

1. **Vercel 로그인**
   - https://vercel.com 접속
   - GitHub 계정으로 로그인

2. **프로젝트 가져오기**
   - "Add New..." → "Project" 클릭
   - GitHub 저장소 `jh-sh7/CON-A_excel` 선택
   - "Import" 클릭

3. **프로젝트 설정**
   - **Framework Preset**: "Other" 선택
   - **Root Directory**: `./` (기본값)
   - **Build Command**: (비워두기)
   - **Output Directory**: (비워두기)

4. **환경 변수 설정** (선택사항)
   - `SECRET_KEY`: Flask 세션 키 (랜덤 문자열)
     - 생성 방법: Python에서 `import secrets; print(secrets.token_hex(32))` 실행

5. **배포**
   - "Deploy" 버튼 클릭
   - 배포 완료 후 URL 확인

### 방법 2: Vercel CLI 사용

```bash
# Vercel CLI 설치
npm i -g vercel

# 로그인
vercel login

# 프로젝트 디렉토리에서 배포
vercel

# 프로덕션 배포
vercel --prod
```

## 중요 사항

### SQLite 데이터베이스
- Vercel은 serverless 환경이므로 **SQLite DB는 임시 파일 시스템에 저장**됩니다
- 서버 재시작 시 데이터가 초기화될 수 있습니다
- 프로덕션 환경에서는 PostgreSQL, MySQL 등 영구 DB 사용 권장

### 정적 파일
- `static/` 폴더의 CSS 파일은 자동으로 서빙됩니다
- `templates/` 폴더의 HTML 템플릿도 포함됩니다

### 배포 후 확인
배포가 완료되면 다음 URL로 접속:
- `https://your-project-name.vercel.app/` - **QUAZ 갤러리 메인** (게시물 목록)
- `https://your-project-name.vercel.app/trends` - **요즘 트렌드** (조회수 높은 게시물)
- `https://your-project-name.vercel.app/write` - 글쓰기
- `https://your-project-name.vercel.app/admin` - 관리자 페이지
- `https://your-project-name.vercel.app/excel` - CON-A 엑셀 앱 (기존 기능)

## 문제 해결

### 배포 실패 시
1. Vercel 대시보드의 "Deployments" 탭에서 로그 확인
2. `requirements.txt`의 패키지 버전 확인
3. Python 버전 확인 (Vercel은 기본적으로 Python 3.9 사용)

### 데이터베이스 오류
- Vercel의 임시 파일 시스템 제한으로 인해 SQLite가 작동하지 않을 수 있습니다
- 이 경우 외부 DB 서비스 사용 필요
