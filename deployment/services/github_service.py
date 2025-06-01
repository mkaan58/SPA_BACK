import requests
import base64
import json
from django.conf import settings
from typing import Dict, Optional


class GitHubService:
    def __init__(self):
        self.token = settings.GITHUB_ACCESS_TOKEN
        self.base_url = "https://api.github.com"
        self.username = "mkaan58"  # Kişisel hesap kullanıcı adı
        
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
    
    def create_repository(self, repo_name: str, description: str = "") -> Dict:
        """GitHub'da yeni repository oluşturur (kişisel hesap altında)"""
        url = f"{self.base_url}/user/repos"
        
        data = {
            "name": repo_name,
            "description": description,
            "private": False,
            "auto_init": True,
            "gitignore_template": "Node",
            "has_issues": False,
            "has_projects": False,
            "has_wiki": False
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        print(f"GitHub API create_repository Response: URL={url}, Status={response.status_code}, Body={response.text}")
        
        if response.status_code == 201:
            return response.json()
        elif response.status_code == 422 and "name already exists" in response.text.lower():
            # Repository zaten varsa, mevcut repository bilgilerini getir
            return self.get_repository(repo_name) or {}
        else:
            raise Exception(f"Failed to create repository: {response.text}")
    
    def upload_file(self, repo_name: str, file_path: str, content: str, commit_message: str) -> Dict:
        """Repository'ye dosya yükler (kişisel hesap altında)"""
        url = f"{self.base_url}/repos/{self.username}/{repo_name}/contents/{file_path}"
        
        # Repository'nin var olduğunu doğrula
        repo_exists = self.get_repository(repo_name)
        if not repo_exists:
            raise Exception(f"Repository {self.username}/{repo_name} does not exist")
        
        encoded_content = base64.b64encode(content.encode()).decode()
        
        data = {
            "message": commit_message,
            "content": encoded_content
        }
        
        try:
            existing_file = self.get_file(repo_name, file_path)
            if existing_file:
                data["sha"] = existing_file["sha"]
        except:
            pass
        
        response = requests.put(url, headers=self.headers, json=data)
        print(f"GitHub API upload_file Response: URL={url}, Status={response.status_code}, Body={response.text}")
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise Exception(f"Failed to upload file: {response.text}")
    
    def get_file(self, repo_name: str, file_path: str) -> Optional[Dict]:
        """Repository'den dosya bilgilerini getirir (kişisel hesap altında)"""
        url = f"{self.base_url}/repos/{self.username}/{repo_name}/contents/{file_path}"
        
        response = requests.get(url, headers=self.headers)
        print(f"GitHub API get_file Response: URL={url}, Status={response.status_code}, Body={response.text}")
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def delete_repository(self, repo_name: str) -> bool:
        """Repository'yi siler (kişisel hesap altında)"""
        url = f"{self.base_url}/repos/{self.username}/{repo_name}"
        
        response = requests.delete(url, headers=self.headers)
        print(f"GitHub API delete_repository Response: URL={url}, Status={response.status_code}")
        
        return response.status_code == 204
    
    def get_repository(self, repo_name: str) -> Optional[Dict]:
        """Repository bilgilerini getirir (kişisel hesap altında)"""
        url = f"{self.base_url}/repos/{self.username}/{repo_name}"
        
        response = requests.get(url, headers=self.headers)
        print(f"GitHub API get_repository Response: URL={url}, Status={response.status_code}, Body={response.text}")
        
        if response.status_code == 200:
            return response.json()
        return None