from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import pandas as pd
import re
import os
import time
import inspect
from .base_manager import GoogleBaseManager, retry_on_error, increment_month, extract_spreadsheet_id

class GoogleDriveManager(GoogleBaseManager):
    """구글 드라이브 관리를 위한 클래스"""
    
    # 기본 설정 정의
    DEFAULT_SCOPES = [
        'https://www.googleapis.com/auth/drive',
    ]
    DEFAULT_SERVICE = 'drive'
    DEFAULT_VERSION = 'v3'
    
    def __init__(self, json_folder = None, scopes = None, version = None, service_name = None):
        """
        구글 드라이브 API 서비스 초기화
        
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

    def clone_file(self, file_id, new_title):
        """
        구글 스프레드시트를 복제하고 새 이름 지정
        
        Args:
            file_id (str): 복제할 스프레드시트 ID
            new_title (str): 새로운 스프레드시트 제목
            
        Returns:
            str: 복제된 파일의 ID 또는 None (실패 시)
        """
        break_point = 0
        while True:
            try:
                copied_file = self.service.files().copy(
                    fileId=file_id,
                    supportsAllDrives=True,
                    body={"name": new_title}
                ).execute()
                return copied_file['id']
            except HttpError as error:
                print(f"⚠️ {inspect.currentframe().f_code.co_name} | 파일 복제 중 오류 발생: {error}")
                break_point = break_point + 1
                time.sleep(10)
                if break_point == 5:
                    return None

    def delete_file(self, file_id):
        """
        구글 스프레드시트 삭제
        
        Args:
            file_id (str): 삭제할 스프레드시트 ID
        """
        try:
            self.service.files().delete(fileId=file_id).execute()
            print(f"✅ 파일 ID {file_id}: 삭제 완료")
        except HttpError as error:
            print(f"⚠️ {inspect.currentframe().f_code.co_name} | 파일 삭제 중 오류 발생: {error}")

    def create_folder(self, folder_name, parent_folder_id):
        """
        구글 드라이브에 폴더가 없으면 생성, 있으면 해당 폴더 ID 반환

        Args:
            folder_name (str): 생성할 폴더 이름
            parent_folder_id (str): 상위 폴더 ID
        Returns:
            str: 폴더 ID
        """
        query = (
            f"'{parent_folder_id}' in parents and "
            f"mimeType='application/vnd.google-apps.folder' and "
            f"name='{folder_name}' and trashed=false"
        )
        response = self.service.files().list(
            q=query,
            spaces='drive',
            includeItemsFromAllDrives=True,
            fields='files(id, name)',
            supportsAllDrives=True
        ).execute()
        files = response.get('files', [])
        if files:
            folder_id = files[0].get('id')
            print(f"✅ 폴더 '{folder_name}' 이미 존재 - ID: {folder_id}")
            return folder_id
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id],
        }
        folder = self.service.files().create(
            body=file_metadata, fields='id', supportsAllDrives=True
        ).execute()
        print(f"✅ 폴더 '{folder_name}' 생성 완료 - ID: {folder.get('id')}")
        return folder.get('id')

    def upload_file(self, file_path, parent_folder_id):
        """
        구글 드라이브에 파일을 업로드합니다.

        Args:
            file_path (str): 업로드할 파일 경로
            parent_folder_id (str): 상위 폴더 ID
        Returns:
            str: 업로드된 파일의 ID
        """
        file_name = os.path.basename(file_path)
        media = MediaFileUpload(file_path, resumable=True)
        file_metadata = {
            'name': file_name,
            'parents': [parent_folder_id],
        }
        file = self.service.files().create(
            body=file_metadata, media_body=media, fields='id', supportsAllDrives=True
        ).execute()
        print(f"✅ 파일 '{file_name}' 업로드 완료 - ID: {file.get('id')}")
        return file.get('id')

    def create_new_row(self, original_row, new_ym, new_file_id, new_title):
        """
        새로운 행 데이터 생성
        
        Args:
            original_row (pd.Series): 원본 행 데이터
            new_ym (str): 새로운 연월
            new_file_id (str): 새로운 파일 ID
            new_title (str): 새로운 파일 제목
            
        Returns:
            pd.Series: 새로운 행 데이터
        """
        new_row = original_row.copy()
        new_row['연월'] = new_ym
        new_row['URL or ID'] = new_file_id
        new_row['파일이름'] = new_title
        new_row['URL 전처리'] = f"https://docs.google.com/spreadsheets/d/{new_file_id}"

        preserve_columns = ['병원', '지점/데이터', '데이터', '프로그램']
        for col in preserve_columns:
            new_row[col] = original_row[col]
            
        return new_row
    
    @retry_on_error
    def update_data_with_clones(self, data, target_ym):
        """
        데이터에서 특정 연월의 스프레드시트를 복제하고 다음 연월로 정보 업데이트
        
        Args:
            data (pd.DataFrame): 병원지점별 데이터 업데이트용 URL 시트의 Data
            target_ym (str): 대상 연월 - 포맷: yyMM (예: '2411')

        Returns:
            pd.DataFrame: 업데이트된 데이터프레임
        """
        new_data = []
        target_ym_full = f"20{target_ym}"
        sheet_insert_ym = increment_month(target_ym)
        print(f'{target_ym} → {sheet_insert_ym} 월별 시트 복제 작업 시작!')
        
        for idx, row in data.iterrows():
            if str(row['연월']) == str(target_ym):
                try:
                    file_name = str(row['파일이름'])

                    if re.search(rf"{target_ym_full[:4]}-{target_ym_full[4:]}", file_name):
                        pattern = rf"{target_ym_full[:4]}-{target_ym_full[4:]}"
                        new_ym = increment_month(f"{target_ym_full[:4]}-{target_ym_full[4:]}")
                    elif re.search(rf"{target_ym_full}", file_name):
                        pattern = rf"{target_ym_full}"
                        new_ym = increment_month(target_ym_full)
                    elif re.search(rf"{target_ym}", file_name):
                        pattern = rf"{target_ym}"
                        new_ym = increment_month(target_ym)
                    else:
                        continue

                    new_title = re.sub(pattern, new_ym, file_name)
                    spreadsheet_id = extract_spreadsheet_id(row['URL 전처리'])
                    
                    if not spreadsheet_id:
                        print(f"행 {idx}: 유효하지 않은 URL 또는 ID")
                        continue
                    
                    new_file_id = self.clone_file(spreadsheet_id, new_title)
                    
                    if not new_file_id:
                        print(f'{new_title} 시트 생성에 실패했습니다.')
                        new_row = self.create_new_row(row, sheet_insert_ym, '시트생성 실패', new_title)
                        new_data.append(new_row)
                    else:
                        new_row = self.create_new_row(row, sheet_insert_ym, new_file_id, new_title)
                        new_data.append(new_row)
                        print(f"{file_name} => {new_title}: 파일 복제 및 데이터 업데이트 완료")
                
                except Exception as e:
                    print(f"{new_title} 처리 중 오류 발생: {str(e)}")
                    continue
        
        if new_data:
            return pd.concat([pd.DataFrame(new_data), data], ignore_index=True)
        else:
            print("복제된 데이터가 없습니다.")
            return data 