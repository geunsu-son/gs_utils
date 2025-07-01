import pandas as pd
import datetime
import decimal
import inspect
from collections import Counter
from .base_manager import (
    GoogleBaseManager, 
    retry_on_error, 
    extract_spreadsheet_id, 
    convert_sheetid_to_url, 
    convert_to_number
)

class GoogleSheetManager(GoogleBaseManager):
    """구글 스프레드시트 관리를 위한 클래스"""
    
    # 기본 설정 정의
    DEFAULT_SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
    ]
    DEFAULT_SERVICE = 'sheets'
    DEFAULT_VERSION = 'v4'
    
    def __init__(self, json_folder = None, scopes = None, version = None, service_name = None):
        """
        구글 스프레드시트 API 서비스 초기화
        
        Args:
            json_folder (str, optional): 서비스 계정 키 파일이 있는 폴더 경로
            scopes (list, optional): API 스코프 목록. 기본값은 None (DEFAULT_SCOPES 사용)
            version (str, optional): API 버전. 기본값은 None (DEFAULT_VERSION 사용)
            service_name (str, optional): 서비스 이름. 기본값은 None (DEFAULT_SERVICE 사용)
        """
        # 기본값 설정
        if scopes is None:
            scopes = self.DEFAULT_SCOPES
        if version is None:
            version = self.DEFAULT_VERSION
        if service_name is None:
            service_name = self.DEFAULT_SERVICE
            
        super().__init__(
            service_name=service_name,
            version=version,
            scope=scopes,
            json_folder=json_folder
        )

    @retry_on_error
    def get_sheet_name_id_dict(self, spreadsheet_id):
        """
        구글 스프레드시트의 시트 이름과 sheetId를 dict로 반환합니다.
        Args:
            spreadsheet_id (str): 구글 스프레드시트 ID
        Returns:
            dict: {시트이름: sheetId, ...}
        """
        sheet_metadata = self.service.spreadsheets().get(spreadsheetId=extract_spreadsheet_id(spreadsheet_id)).execute()
        sheets = sheet_metadata.get('sheets', [])
        return {sheet['properties']['title']: sheet['properties']['sheetId'] for sheet in sheets}

    @retry_on_error
    def get_sheet_name_list(self, spreadsheet_url):
        """
        구글 스프레드시트의 시트 이름 리스트를 반환합니다.
        Args:
            spreadsheet_id (str): 구글 스프레드시트 ID
        Returns:
            list: 시트 이름 리스트
        """
        sheet_metadata = self.service.spreadsheets().get(spreadsheetId=extract_spreadsheet_id(spreadsheet_url)).execute()
        sheets = sheet_metadata.get('sheets', [])
        return [sheet['properties']['title'] for sheet in sheets]

    @retry_on_error
    def copy_sheet_format(
        self,
        spreadsheet_url: str,
        source_sheet_name: str,
        target_sheet_names: list,
        source_range: dict = None,
        target_range: dict = None,
    ):
        """
        구글 스프레드시트 내에서 한 시트의 서식을 여러 시트에 복사합니다.
        Args:
            spreadsheet_url (str): 구글 스프레드시트 ID (URL에서 추출)
            source_sheet_name (str): 서식을 복사할 시트 이름
            target_sheet_names (list): 서식을 붙여넣을 시트 이름 리스트
            source_range (dict, optional): 복사할 범위 (예: {"startRowIndex":0, "endRowIndex":80, "startColumnIndex":0, "endColumnIndex":50})
            target_range (dict, optional): 붙여넣을 범위 (없으면 source_range와 동일하게 적용)
        Returns:
            dict: 구글 API 응답
        """
        spreadsheet_id = extract_spreadsheet_id(spreadsheet_url)
        spreadsheet_url = convert_sheetid_to_url(spreadsheet_id)
        name_to_id = self.get_sheet_name_id_dict(spreadsheet_id)
        source_sheet_id = name_to_id.get(source_sheet_name)

        if source_sheet_id is None:
            raise ValueError(f"⚠️ {inspect.currentframe().f_code.co_name} | source_sheet_name '{source_sheet_name}'를 찾을 수 없습니다. - URL: {spreadsheet_url}")
        
        if source_range is None:
            source_range = {
                "sheetId": source_sheet_id,
                "startRowIndex": 0,
                "endRowIndex": 1000000,
                "startColumnIndex": 0,
                "endColumnIndex": 1000
            }
        else:
            source_range = dict(source_range)
            source_range["sheetId"] = source_sheet_id

        requests = []
        for target_name in target_sheet_names:
            target_sheet_id = name_to_id.get(target_name)
            if target_sheet_id is None:
                print(f"⚠️ {inspect.currentframe().f_code.co_name} | target_sheet_name '{target_name}'를 찾을 수 없습니다. - URL: {spreadsheet_url}")
                continue

            if target_range is None:
                dest_range = {k: v for k, v in source_range.items() if k != "sheetId"}
            else:
                dest_range = dict(target_range)
            
            dest_range["sheetId"] = target_sheet_id
            requests.append({
                "copyPaste": {
                    "source": source_range,
                    "destination": dest_range,
                    "pasteType": "PASTE_FORMAT"
                }
            })
        if not requests:
            raise ValueError(f"⚠️ {inspect.currentframe().f_code.co_name} | 복사할 대상 시트가 없습니다. - URL: {spreadsheet_url}")
        
        body = {"requests": requests}
        response = self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body=body
        ).execute()
        
        print(f"✅ 구글시트 서식 복사 및 붙여넣기 완료 - {spreadsheet_url}")
        return response

    @retry_on_error
    def copy_sheet_whole_values(
        self,
        spreadsheet_source_url: str,
        source_sheet_name: str,
        spreadsheet_target_url: str = None,
        target_sheet_name: str = None,
    ):
        """
        구글 스프레드시트에서 시트의 전체 값을 여러 시트에 복사합니다.
        ⚠️ 숫자의 경우 앞뒤에 명, 만, 억 등의 서식이 붙어있을 경우 문자로 복사됩니다.
        Args:
            spreadsheet_source_url (str): 구글 스프레드시트 ID (URL에서 추출)
            source_sheet_name (str): 서식을 복사할 시트 이름
            spreadsheet_target_url (str): 구글 스프레드시트 ID (URL에서 추출)
            target_sheet_name (str): 서식을 붙여넣을 시트 이름
        """

        if target_sheet_name == None:
            raise ValueError(f"⚠️ {inspect.currentframe().f_code.co_name} | target_sheet_name이 지정되지 않았습니다.")

        spreadsheet_source_id = extract_spreadsheet_id(spreadsheet_source_url)
        spreadsheet_source_url = convert_sheetid_to_url(spreadsheet_source_id)

        if spreadsheet_target_url == None:
            spreadsheet_target_url = spreadsheet_source_url

        spreadsheet_target_id = extract_spreadsheet_id(spreadsheet_target_url)
        spreadsheet_target_url = convert_sheetid_to_url(spreadsheet_target_id)

        # 보고서 복사 붙여넣기
        result = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_source_id,
            range=f'{source_sheet_name}!A1:ZZZ'
        ).execute()
        values = result.get('values', [])
        values = [[convert_to_number(cell) for cell in row] for row in values]
        values_fillna = pd.DataFrame(values).values.tolist()
        # NaN 값을 빈 문자열로 변환
        values_fillna = [['' if pd.isna(cell) else cell for cell in row] for row in values_fillna]
        self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_target_id,
                range=f"{target_sheet_name}!A1",
                valueInputOption="USER_ENTERED",  # 또는 'RAW'
                body={"values": values_fillna},
            ).execute()
        
        print(f"✅ 구글시트 전체 값 복사 완료 - source_sheet_name: {source_sheet_name} => target_sheet_name: {target_sheet_name}, spreadsheet_url: {spreadsheet_target_url}")

    @retry_on_error
    def clear_and_set_worksheet(self, spreadsheet_url, sheet_name, df, cell_name='A1'):
        """
        워크시트를 초기화하고 주어진 데이터프레임으로 설정합니다.
        워크시트가 없는 경우 새로 생성합니다.

        Args:
            spreadsheet_url (str): Google 스프레드시트 문서의 URL 또는 ID
            sheet_name (str): 작업할 시트 탭의 이름
            df (pandas.DataFrame): 시트에 설정할 데이터프레임
        """
        # 파일 ID 추출
        spreadsheet_id = extract_spreadsheet_id(spreadsheet_url)
        spreadsheet_url = convert_sheetid_to_url(spreadsheet_id)
        
        try:
            # 시트 ID 가져오기
            sheet_metadata = self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheets = sheet_metadata.get('sheets', [])
            
            # 시트 존재 여부 확인
            sheet_id = None
            for sheet in sheets:
                if sheet['properties']['title'] == sheet_name:
                    sheet_id = sheet['properties']['sheetId']
                    break
            
            if sheet_id is None:
                # 새 시트 생성
                request = {
                    'addSheet': {
                        'properties': {
                            'title': sheet_name,
                            'gridProperties': {
                                'rowCount': 100,
                                'columnCount': 10
                            }
                        }
                    }
                }
                response = self.service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body={'requests': [request]}
                ).execute()
                sheet_id = response['replies'][0]['addSheet']['properties']['sheetId']
            
            # 데이터프레임을 리스트로 변환
            df = df.apply(lambda col: col.astype(str) if col.apply(lambda x: isinstance(x, datetime.date)).any() else col)
            df = df.apply(lambda col: col.astype(float) if col.apply(lambda x: isinstance(x, decimal.Decimal)).any() else col)
            safe_df = df.where(pd.notnull(df), '')
            values = [safe_df.columns.tolist()] + safe_df.values.tolist()
            
            # 데이터 업데이트
            body = {
                'values': values
            }
        
            # 시트 전체 초기화 (간단하게)
            self.service.spreadsheets().values().batchClear(
                spreadsheetId=spreadsheet_id,
                body={
                    'ranges': [f'{sheet_name}!A:ZZZ']  # 전체 범위 지정
                }
            ).execute()
            
            self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f'{sheet_name}!{cell_name}',
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            print(f"✅ 시트 초기화 및 데이터 입력 완료 (sheet_name: {sheet_name}, spreadsheet_url: {spreadsheet_url})")
            
        except Exception as e:
            print(f"⚠️ {inspect.currentframe().f_code.co_name} | 오류 발생: {str(e)}")
            raise

    @retry_on_error
    def get_dataframe_from_sheet(self, spreadsheet_url, sheet_name, skip_rows=0, range_name='A1:ZZZ'):
        """
        주어진 Google 스프레드시트 URL과 시트 이름을 사용하여 데이터를 불러와 Pandas DataFrame으로 변환합니다.

        Args:
            spreadsheet_url (str): Google 스프레드시트 문서의 URL 또는 ID
            sheet_name (str): 데이터를 불러올 시트 탭의 이름
            skip_rows (int, optional): 첫 번째 행을 건너뛸 행 수 (기본값: 0)
            range_name (str, optional): 데이터를 불러올 범위 (기본값: 'A1:ZZZ')

        Returns:
            pandas.DataFrame: 시트에서 가져온 데이터를 포함하는 데이터프레임
        """
        # 파일 ID 추출
        spreadsheet_id = extract_spreadsheet_id(spreadsheet_url)
        spreadsheet_url = convert_sheetid_to_url(spreadsheet_id)
        try:
            # 시트 메타데이터 가져오기
            sheet_metadata = self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheets = sheet_metadata.get('sheets', [])
            
            # 시트 존재 여부 확인
            sheet_exists = False
            for sheet in sheets:
                if sheet['properties']['title'] == sheet_name:
                    sheet_exists = True
                    break
            
            if not sheet_exists:
                # 시트1 또는 Sheet1 확인
                for sheet in sheets:
                    if sheet['properties']['title'] in ['시트1', 'Sheet1']:
                        sheet_name = sheet['properties']['title']
                        sheet_exists = True
                        break
            
            if not sheet_exists:
                raise ValueError(f"⚠️ {inspect.currentframe().f_code.co_name} | 시트 '{sheet_name}'를 찾을 수 없습니다. - URL: {spreadsheet_url}")
            
            # 데이터 가져오기
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f'{sheet_name}!{range_name}'  # 모든 데이터를 가져오기 위해 범위를 조정
            ).execute()
            values = result.get('values', [])
            if not values or len(values) == 1:  # 데이터가 없거나 컬럼명만 있는 경우 빈 데이터프레임 리턴
                return pd.DataFrame()
            
            # 첫 행을 컬럼명으로 사용
            headers = values[skip_rows]

            # 중복된 컬럼명이 있으면 '_1', '_2' 등을 추가하여 유니크하게 만듦
            header_counts = Counter(headers)
            unique_headers = []
            header_seen = {}
            for h in headers:
                if header_counts[h] > 1:
                    header_seen[h] = header_seen.get(h, 0) + 1
                    unique_headers.append(f"{h}_{header_seen[h]}")
                else:
                    unique_headers.append(h)

            # 중복된 컬럼명이 있을 경우 경고 메시지 출력
            if any(count > 1 for count in header_counts.values()):
                duplicate_headers = [h for h in header_counts if header_counts[h] > 1]
                print(f"⚠️ 중복된 컬럼명 발견: {', '.join(duplicate_headers)} (총 {len(duplicate_headers)}개 중복됨)")

            data = values[skip_rows+1:]

            # 각 행의 길이를 헤더에 맞게 조정
            header_len = len(unique_headers)
            fixed_data = []
            max_row_len = max([len(row) for row in data])
            if max_row_len != header_len:
                print(f"⚠️ {inspect.currentframe().f_code.co_name} | 데이터와 컬럼명의 열 개수 상이 - sheet_name: {sheet_name}, URL: {spreadsheet_url}")

                for row in data:
                    # 부족하면 빈 문자열로 채우기
                    if len(row) < header_len:
                        row = row + [''] * (header_len - len(row))
                    # 넘치면 자르기
                    elif len(row) > header_len:
                        row = row[:header_len]
                    fixed_data.append([convert_to_number(cell) for cell in row])
            else:
                fixed_data = [[convert_to_number(cell) for cell in row] for row in data]

            # 데이터프레임 생성
            df = pd.DataFrame(fixed_data, columns=unique_headers)
            print(f"📩 데이터 로드 완료 (행: {len(df)}, 열: {len(df.columns)}) (sheet_name: {sheet_name}, spreadsheet_url: {spreadsheet_url})")
            return df
            
        except Exception as e:
            print(f"⚠️ {inspect.currentframe().f_code.co_name} | 오류 발생: {str(e)}")
            raise 