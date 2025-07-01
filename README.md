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

| 기능 | 설명 | 함수 |
|------|------|------|
| ⏱️ 실행 시간 측정 | 함수 실행 전후 시간을 콘솔에 출력 | `@time_tracker` |

---

## 🧪 Example Usage

```python
from gs_utils import time_tracker
import time

@time_tracker
def my_task():
    time.sleep(2)
    return "작업 완료!"

my_task()
```

실행 시 출력:
```
⏳ Function 'my_task' started at: 2025-07-01 10:00:00
✅ Function 'my_task' finished at: 2025-07-01 10:00:02
🕒 Total execution time: 2.0000 seconds
--------------------------------------------------
```

---

## 📚 Roadmap

- [x] 실행 시간 측정 데코레이터 (`@time_tracker`)
- [ ] googleapiclient 연동 함수 (편의성 ↑)
- [ ] 추가 함수 고민 (ing)

---

## 🙌 Author

손근수(geunsu-son)
데이터 기반 문제 해결을 즐기는 데이터 엔지니어

---

> PR, 아이디어, 개선 제안은 언제든지 환영합니다!
