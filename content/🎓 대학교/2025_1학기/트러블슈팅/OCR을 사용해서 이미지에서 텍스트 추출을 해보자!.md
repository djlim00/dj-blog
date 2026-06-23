
# 1. Tesseract

1. OCR은 그냥 웬만하면 파이썬을 사용해서 하는게 좋다..(Tess4J를 사용했는데 뭐 잘 안된다.)
2. 무료 OCR은 Tesseract를 사용하자.

### 구조 : Python OCR API 서버에서 수행하고 스프링이 HTTP 요청으로 OCR 결과를 받아옴
| 역할                | 설명                                    |
| ----------------- | ------------------------------------- |
| Python FastAPI 서버 | 이미지 받아서 OCR 수행 → 사업체명/성명 추출 → JSON 응답 |
| Kotlin Spring 서버  | 사용자가 업로드한 파일을 Python 서버로 보내서 결과 받아오기  |
> User → Spring 서버 (MyPageController) → Python OCR 서버 (FastAPI) → 결과 리턴


### 그럼 파이썬 서버는 조상님이 만들어주느냐..

- 그건 아니다.  FastAPI를 이용해서 간단하게 서버를 만들어주자.

```python title:"서버 코드"
from fastapi import FastAPI, UploadFile, File  
from fastapi.responses import JSONResponse  
import pytesseract  
from PIL import Image  
import io  
import re  
  
app = FastAPI()  
  
@app.post("/ocr/contract")  
async def ocr_contract(file: UploadFile = File(...)):  
    contents = await file.read()  
    image = Image.open(io.BytesIO(contents))  
    text = pytesseract.image_to_string(image, lang='kor')  
  
    company_match = re.search(r'사\s*업\s*체\s*명\s*[:：]?\s*(.+)', text)  
    worker_match = re.search(r'성\s*명\s*[:：]?\s*(.+)', text)  
  
    company_name = company_match.group(1).strip() if company_match else ""  
    worker_name = worker_match.group(1).strip() if worker_match else ""  
  
    return JSONResponse({  
        "company_name": company_name,  
        "worker_name": worker_name  
    })  
  
@app.get("/")  
async def root():  
    return {"message": "Hello World"}  
  
if __name__ == "__main__":  
    import uvicorn  
    uvicorn.run(app, host="0.0.0.0", port=8000)
```
- 위에 `async def ocr_contract(file: UploadFile = File(...))` 이건 OCR을 수행하는 엔드 포인트이다.
	- @app.post("/ocr/contract")로 url과 post 요청임을 명시
- 아래는 테스트옹 get요청이다(hello world 반환)
- 맨 아래는 일종의 main 함수? 호스트 주소랑, 포트를 지정

### python ocr_server.py를 하면 서버가 띄워짐
![[Pasted image 20250428153631.png]]
- 그저 신기할 따름이다..

____
# 2. Azure Computer Vision

- 이건 Ai가 이미지를 분석해준다. 
- 사실 일반적인 OCR보다 훨씬 헤비한 기능이라서 현재 프로젝트의 근로 계약서 분석에 이정도로 필요할까 싶은데..
	- 이미지에서 어떤 물체인지 알려주고 막 그정도도 해줌..(강아지 사진 보고 강아지라고 한다든지,,)
- 하지만 근로 계약서가 모두 형식이 다르기 때문에 이런게 필요할 수 있겠다.

![[Pasted image 20250429093300.png]]
- 이번에는 Python으로 FastAPI가 필요가 없다. 
- Azure Computer Vision 서버가 따로 있어서 우리는 <mark style="background: #FFF3A3A6;">api키값</mark>들을 가지고 거기랑 소통해서 결과를 받는다.

___
# 3. 결국 Google Vision으로 했다는..
