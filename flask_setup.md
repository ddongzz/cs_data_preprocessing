# 1일차

## 1. python 실행 환경 구축하기

### 1-1. Python 3.12 + uv 설치

> **uv**는 pip보다 10~100배 빠른 Python 패키지 매니저입니다.  
> Rust로 작성되어 의존성 해결과 설치가 빠르며, 가상환경 관리까지 통합되어 있습니다.

```powershell
# uv 설치 (Windows PowerShell)
Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression


# uv로 Python 3.12 설치
uv python install 3.12

# 가상환경 생성 및 활성화
uv venv --python 3.12
.\.venv\Scripts\Activate.ps1

# uv init

# 의존성 설치
uv pip install -r requirements.txt
```
> **자동화 스크립트** 사용:
> ```powershell
> .\setup.ps1
> ```

### 1-2. GitHub Copilot Pro Plan 확인

1. https://github.com/settings/copilot 접속
2. Copilot Pro 구독 상태 확인
3. VS Code에서 `Ctrl+Shift+P` → "GitHub Copilot: Sign In"

### 1-3. .env 기본 구성

```env
# 예시 (실제 값은 절대 커밋하지 않습니다)
APP_ENV=development
```


### 1-4. .env 환경 삭제
```terminal
# 1. 가상환경 비활성화 (현재 활성화되어 있는 경우)
deactivate

# 2. 가상환경 폴더(.venv) 완전 삭제
Remove-Item -Recurse -Force .\.venv
```
## 2. 허깅페이스 모델을 로딩해 서비스가 구동되는 웹 서비스 만들기
- python==3.12.x에서는
- PyTorch: 2.2 버전부터 Python 3.12 공식 지원 (현재 안정 버전은 3.12 완전 지원)
- Transformers: Python 3.9 이상이면 모두 호환, 3.12도 문제없음
- Flask: 3.12 포함 최신 버전까지 문제없이 동작

```bash
#프로젝트 의존성 관리
uv add flask
# 필수 패키지 설치
uv pip install transformers torch
```


프로젝트 구조
```
flask-hf-demo/
├── venv/
└── app.py
```

코드
```python
from flask import Flask, request, jsonify
from transformers import pipeline

app = Flask(__name__)

# 서버 시작 시 모델 1회만 로딩 (요청마다 로딩하면 매우 느림)
classifier = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "text 필드가 필요합니다"}), 400

    result = classifier(text)[0]  # 예: {'label': 'POSITIVE', 'score': 0.99}
    return jsonify(result)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
```
#### 실행하기
- uv run을 사용하면 별도로 가상환경을 activate 하지 않아도, 자동으로 생성된 .venv 환경 위에서 명령어를 실행한다.
```bash
uv run flask --app app run
```
또는
```bash
uv run flask --app app run --debug
#uv run flask --app app2 run --debug
```

## 3. 허깅페이스
1. 토큰 발급

https://huggingface.co/settings/tokens 에서 발급 (Read 권한이면 충분, 모델 다운로드만 할 경우)

2. 환경변수로 설정 — uv 프로젝트 기준
```bash
# .env 파일에 추가 (프로젝트 루트)
echo 'HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx' >> .env


# uv run 시 .env 자동 반영해서 실행
uv run --env-file .env app.py
```
powershell에서 인코딩 문제발생시
```bash
Set-Content -Path .env -Value "HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx" -Encoding utf8

uv run --env-file .env app.py
```
