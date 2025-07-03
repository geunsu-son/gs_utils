from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import pandas as pd
import re
import os
import time
import inspect
from .base_manager import GoogleBaseManager, retry_on_error, extract_spreadsheet_id

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