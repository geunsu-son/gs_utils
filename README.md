# 📦 gs_utils

**geunsu-son's Personal Python Utility Library**  
자주 사용하는 함수들을 정리해, 어떤 환경에서도 바로 불러 쓸 수 있게 만든 유틸리티 패키지입니다.

---

## 🚀 Install

GitHub에서 직접 설치:

```bash
pip install git+https://github.com/your-username/gs_utils.git
```

> 로컬에서 개발 중이라면:
>
> ```bash
> git clone https://github.com/your-username/gs_utils.git
> cd gs_utils
> pip install -e .
> ```

---

## ✨ Included Features

| 기능 | 설명 | 함수/클래스 |
|------|------|------|
| ⏱️ 실행 시간 측정 | 함수 실행 전후 시간을 콘솔에 출력 | `@time_tracker` |
| 🔄 API 재시도 로직 | Google API 요청 실패 시 자동 재시도 | `@retry_on_error` |
| 📅 날짜 처리 | 연월 증가 및 날짜 패턴 변환 | `increment_month()` |
| 🔗 URL/ID 변환 | Google 스프레드시트 URL ↔ ID 변환 | `extract_spreadsheet_id()`, `convert_sheetid_to_url()` |
| 🔢 데이터 변환 | 문자열을 숫자로 변환 | `convert_to_number()` |
| 📁 Google Drive 관리 | 파일 복제, 삭제, 폴더 생성, 업로드 | `GoogleDriveManager` |
| 📊 Google Sheets 관리 | 데이터 읽기/쓰기, 서식 복사, 시트 관리 | `GoogleSheetManager` |

---

## 🧪 Example Usage

### 기본 유틸리티 함수

```python
from gs_utils import time_tracker, increment_month, extract_spreadsheet_id
import time

@time_tracker
def my_task():
    time.sleep(2)
    return "작업 완료!"

# 날짜 처리
next_month = increment_month('202401')  # '202402'
next_month = increment_month('24-01')   # '24-02'

# URL에서 파일 ID 추출
file_id = extract_spreadsheet_id('https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms')
# 결과: '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'

my_task()
```

실행 시 출력:
```
⏳ Function 'my_task' started at: 2025-07-01 10:00:00
✅ Function 'my_task' finished at: 2025-07-01 10:00:02
🕒 Total execution time: 2.0000 seconds
--------------------------------------------------
```

### Google Drive 관리

```python
from gs_utils import GoogleDriveManager

# Google Drive 매니저 초기화
drive_manager = GoogleDriveManager()

# 파일 복제
new_file_id = drive_manager.clone_file(
    file_id='원본_파일_ID',
    new_title='새_파일_이름'
)

# 폴더 생성
folder_id = drive_manager.create_folder(
    folder_name='새_폴더',
    parent_folder_id='상위_폴더_ID'
)

# 파일 업로드
uploaded_file_id = drive_manager.upload_file(
    file_path='로컬_파일_경로',
    parent_folder_id='폴더_ID'
)
```

### Google Sheets 관리

```python
from gs_utils import GoogleSheetManager, extract_spreadsheet_id

# Google Sheets 매니저 초기화
sheet_manager = GoogleSheetManager()

# 스프레드시트에서 데이터 읽기
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/...'
df = sheet_manager.get_dataframe_from_sheet(
    spreadsheet_url=spreadsheet_url,
    sheet_name='Sheet1'
)

# 스프레드시트에 데이터 쓰기
import pandas as pd
data = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']})
sheet_manager.clear_and_set_worksheet(
    spreadsheet_url=spreadsheet_url,
    sheet_name='Sheet1',
    df=data
)

# 시트 서식 복사
sheet_manager.copy_sheet_format(
    spreadsheet_url=spreadsheet_url,
    source_sheet_name='템플릿',
    target_sheet_names=['새시트1', '새시트2']
)
```

### 하이브리드 사용법

```python
from gs_utils import (
    GoogleSheetManager, 
    increment_month, 
    extract_spreadsheet_id,
    time_tracker
)

@time_tracker
def monthly_report_generator():
    sheet_manager = GoogleSheetManager()
    
    # 유틸리티 함수와 클래스를 함께 사용
    current_month = '202401'
    next_month = increment_month(current_month)
    
    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/...'
    file_id = extract_spreadsheet_id(spreadsheet_url)
    
    # 데이터 처리
    df = sheet_manager.get_dataframe_from_sheet(file_id, 'Data')
    # ... 데이터 처리 로직
    
    return "월간 리포트 생성 완료!"

monthly_report_generator()
```

---

## 📁 Package Structure

```
gs_utils/
├── __init__.py              # 메인 export
├── decorators.py            # 데코레이터 (time_tracker)
└── google/
    ├── __init__.py          # Google API export
    ├── base_manager.py      # 기본 클래스 + 공통 유틸리티
    ├── drive_manager.py     # Google Drive 관리
    └── sheet_manager.py     # Google Sheets 관리
```

### 🔧 주요 컴포넌트

- **`GoogleBaseManager`**: 모든 Google API 클래스의 기본 클래스
- **`GoogleDriveManager`**: Google Drive 파일/폴더 관리
- **`GoogleSheetManager`**: Google Sheets 데이터 관리
- **공통 유틸리티 함수들**: 날짜, URL, 데이터 변환 등

---

## 📚 Roadmap

- [x] 실행 시간 측정 데코레이터 (`@time_tracker`)
- [x] Google API 연동 함수 (편의성 ↑)
  - [x] Google Drive 관리 (`GoogleDriveManager`)
  - [x] Google Sheets 관리 (`GoogleSheetManager`)
  - [x] 공통 유틸리티 함수들
- [ ] Google Calendar API 연동
- [ ] Google Docs API 연동
- [ ] 추가 유틸리티 함수들

---

## 🔧 Requirements

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib pandas
```

---

## 🙌 Author

손근수(geunsu-son)
데이터 기반 문제 해결을 즐기는 데이터 엔지니어

---

> PR, 아이디어, 개선 제안은 언제든지 환영합니다!
