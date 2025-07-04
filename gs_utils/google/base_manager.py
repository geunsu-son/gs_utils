from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.service_account import Credentials
import os
import time
import glob
import inspect
import socket

def retry_on_error(func):
    """API 요청 실패 시 .json 파일을 바꿔서 재시도하는 데코레이터"""
    def wrapper(self, *args, **kwargs):
        for attempt in range(self.max_attempts):
            try:
                return func(self, *args, **kwargs)
            except HttpError as e:
                print(f"⚠️ API quota error ({e.resp.status}) - retrying with next account... (attempt {attempt+1}/{self.max_attempts})")
                self._build_next_service()
                time.sleep(2)
            except (TimeoutError, socket.timeout) as e:
                print(f"⚠️ Timeout error - retrying with next account... (attempt {attempt+1}/{self.max_attempts})")
                self._build_next_service()
                time.sleep(2)
            except Exception as e:
                print(f"⚠️ Unexpected error - retrying with next account...  (attempt {attempt+1}/{self.max_attempts})\n - ℹ️ Error info: {e}")
                self._build_next_service()
                time.sleep(2)
        raise RuntimeError(f"🔥 Request failed - exceeded maximum attempts. - {func.__name__}")
    return wrapper

def extract_spreadsheet_id(spreadsheet_url):
    """
    URL에서 파일 ID 추출
    
    Args:
        spreadsheet_url (str): 구글 스프레드시트 URL 또는 파일 ID
        
    Returns:
        str: 파일 ID
    """
    if "docs.google.com" in spreadsheet_url:
        return spreadsheet_url.split("/d/")[-1].split("/")[0]
    return spreadsheet_url

def convert_sheetid_to_url(spreadsheet_id):
    """
    파일 id를 구글시트 링크로 변경경
    
    Args:
        spreadsheet_id (str): 구글 스프레드시트 ID
        
    Returns:
        str: 구글 스프레드시트 링크
    """
    return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"

def convert_to_number(value):
    """
    문자열을 숫자로 변환
    
    Args:
        value: 변환할 값
        
    Returns:
        변환된 숫자 또는 원본 값
    """
    if isinstance(value, str):
        try:
            if '.' in value:
                return float(value.replace(',', ''))
            else:
                return int(value.replace(',', ''))
        except ValueError:
            return value
    return value

class GoogleBaseManager:
    """구글 API 서비스의 기본 기능을 제공하는 클래스"""

    def __init__(self, service_name, version, scope, attempt_retry = 3, json_folder = None):
        """
        구글 API 서비스 초기화
        
        Args:
            service_name (str): 구글 API 서비스 이름
            version (str): API 버전
            scope (list): API 스코프
            attempt_retry (int, optional): 재시도 횟수. 기본값은 3
            json_folder (str, optional): 서비스 계정 키 파일이 있는 폴더 경로. 기본값은 None
        """
        if json_folder is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            json_folder = os.path.join(os.path.dirname(os.path.dirname(current_dir)), '.secret')

        json_folder = os.path.abspath(json_folder)
        self.json_files = glob.glob(os.path.join(json_folder, '*.json'))
        self.service_name = service_name
        self.version = version
        self.scope = scope
        self.max_attempts = len(self.json_files) * attempt_retry

        if not self.json_files:
            raise FileNotFoundError(f"No .json files found in {json_folder}")

        self.current_index = 0
        self.cycle_sleep_duration = 15  # Sleep duration in seconds after each full cycle
        self._build_next_service()

    def _get_next_json(self):
        """
        다음 JSON 파일을 가져오고, 한 바퀴가 완료되면 대기 시간을 적용
        
        Returns:
            str: 다음 JSON 파일 경로
        """
        if self.current_index >= len(self.json_files):
            print(f"⏳ Cycle completed. Sleeping for {self.cycle_sleep_duration} seconds...")
            time.sleep(self.cycle_sleep_duration)
            self.current_index = 0

        json_file = self.json_files[self.current_index]
        self.current_index += 1
        return json_file

    def _build_next_service(self):
        """다음 서비스 계정으로 API 서비스 재구성"""
        current_json = self._get_next_json()
        self.credentials = Credentials.from_service_account_file(current_json, scopes=self.scope)
        self.service = build(self.service_name, self.version, credentials=self.credentials)
        print(f"🔁 Switched to service account: {os.path.basename(current_json)}")

    def request_with_retry(self, func_callable):
        """
        API 요청 실패 시 재시도 로직을 구현합니다. 주어진 함수가 API 요청을 수행하고, 실패할 경우 최대 시도 횟수만큼 재시도합니다.
        각 클래스 내에 있는 함수는 일반적으로 재시도 데코레이터가 붙어있으므로 별도로 호출할 필요가 없습니다.
        하지만 클래스에 있는 함수가 아닌 경우 별도로 호출할 때 API 허용량 초과 오류가 발생할 수 있으므로 재시도 함수로 묶어주는 것을 권장합니다.

        Args:
            func_callable (callable): API 요청을 수행하는 함수. 이 함수는 서비스 객체를 인자로 받아야 합니다.

        Returns:
            dict: API 요청의 결과로 반환된 데이터.

        Raises:
            RuntimeError: 모든 계정에서 오류가 발생한 경우.
            
        * example 1: Google 스프레드시트에서 값 가져오기\n
            result = google_client_manager.request_with_retry(
                lambda service: service.spreadsheets().values().get(
                    spreadsheetId="your_spreadsheet_id", 
                    range="Sheet1!A1:Z",
                ).execute()
            )
            df = pd.DataFrame(result['values'][1:], columns=result['values'][0])

        * example 2: Google 스프레드시트에 값 업데이트\n
            result = google_client_manager.request_with_retry(
                lambda service: service.spreadsheets().values().update(
                    spreadsheetId='your_spreadsheet_id',
                    range='Sheet1!A1',
                    body={'values': [['입력할 값']]}
                ).execute()
            )
            print(f"업데이트된 셀 수: {result['updatedCells']}")

        """
        for attempt in range(self.max_attempts):
            try:
                return func_callable(self.service)
            except HttpError as e:
                if e.resp.status in [403, 429]:
                    print(f"⚠️ API quota error ({e.resp.status}) - retrying with next account...")
                    self._build_next_service()
                    time.sleep(1)
                else:
                    raise RuntimeError(f"⚠️ API error ({e})")
        raise RuntimeError("❌ 요청 실패 - 모든 계정에서 오류 발생.")