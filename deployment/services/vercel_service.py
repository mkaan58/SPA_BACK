import requests
import json
from django.conf import settings
from typing import Dict, Optional


class VercelService:
    def __init__(self):
        self.token = settings.VERCEL_ACCESS_TOKEN
        self.base_url = "https://api.vercel.com"
        self.github_username = "mkaan58"  # Kişisel GitHub hesap adı
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def create_project(self, project_name: str, github_repo_url: str) -> Dict:
        """Vercel'de yeni proje oluşturur (kişisel hesap reposu ile)"""
        url = f"{self.base_url}/v9/projects"
        
        repo_path = github_repo_url.replace(f"https://github.com/{self.github_username}/", "")
        
        data = {
            "name": project_name,
            "gitRepository": {
                "type": "github",
                "repo": f"{self.github_username}/{repo_path}"
            },
            "buildCommand": "",
            "outputDirectory": ".",
            "framework": None,
            "publicSource": True
        }
        print(f"Vercel API Request: URL={url}, Data={data}, Headers={self.headers}")
        response = requests.post(url, headers=self.headers, json=data)
        print(f"Vercel API Response: Status={response.status_code}, Body={response.text}")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to create Vercel project: {response.text}")
        
    def trigger_deployment(self, project_id: str, project_name: str, file_shas: Dict = None) -> Dict:
        """Git-based deployment tetikler (DOĞRU ENDPOINT)"""
        # DOĞRU ENDPOINT - project_id URL'de değil, body'de
        url = f"{self.base_url}/v13/deployments"
        
        # Dokümantasyona uygun data yapısı
        data = {
            "name": project_name,
            "project": project_id,  # project_id burada belirtiliyor
            "target": "production",
            "gitSource": {
                "type": "github",
                "repoId": project_id,  # GitHub repo ile bağlantı
                "ref": "main"  # veya "master"
            }
        }
        
        print(f"Vercel API trigger_deployment Request: URL={url}, Data={data}, Headers={self.headers}")
        response = requests.post(url, headers=self.headers, json=data)
        print(f"Vercel API trigger_deployment Response: Status={response.status_code}, Body={response.text}")
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise Exception(f"Failed to trigger deployment: {response.text}")
        
    def trigger_deployment_alternative(self, project_id: str, project_name: str, github_repo_name: str,github_repo_id: int) -> Dict:
        """Alternatif: GitHub repo bilgisi ile deployment"""
        url = f"{self.base_url}/v13/deployments"
        
        data = {
            "name": project_name,
            "project": project_id,
            "target": "production",
            "gitSource": {
                "type": "github",
                "repo": f"{self.github_username}/{github_repo_name}",
                "repoId": github_repo_id,
                "ref": "main"
            }
        }
        
        print(f"Vercel API Alternative Request: URL={url}, Data={data}")
        response = requests.post(url, headers=self.headers, json=data)
        print(f"Vercel API Alternative Response: Status={response.status_code}, Body={response.text}")
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise Exception(f"Failed to trigger deployment: {response.text}")
    
    def get_deployment_status(self, deployment_id: str) -> Dict:
        """Deployment durumunu kontrol eder - DOĞRU ENDPOINT"""
        # v13 endpoint'i doğru
        url = f"{self.base_url}/v13/deployments/{deployment_id}"
        
        response = requests.get(url, headers=self.headers)
        print(f"Vercel API get_deployment_status Response: Status={response.status_code}, Body={response.text}")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get deployment status: {response.text}")
    
    def get_project_deployments(self, project_id: str) -> Dict:
        """Proje deployment'larını listeler - DOĞRU ENDPOINT"""
        # v6 endpoint'i doğru
        url = f"{self.base_url}/v6/deployments"
        
        params = {
            "projectId": project_id,
            "limit": 10
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        print(f"Vercel API get_project_deployments Response: Status={response.status_code}, Body={response.text}")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get deployments: {response.text}")
    
    def delete_project(self, project_id: str) -> bool:
        """Vercel projesini siler"""
        url = f"{self.base_url}/v9/projects/{project_id}"
        
        response = requests.delete(url, headers=self.headers)
        print(f"Vercel API delete_project Response: Status={response.status_code}")
        
        return response.status_code == 200
    
    def get_project_info(self, project_id: str) -> Dict:
        """Proje bilgilerini getirir"""
        url = f"{self.base_url}/v9/projects/{project_id}"
        
        response = requests.get(url, headers=self.headers)
        print(f"Vercel API get_project_info Response: Status={response.status_code}, Body={response.text}")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get project info: {response.text}")
    
    def generate_unique_project_name(self, base_name: str) -> str:
        """Benzersiz proje adı oluşturur (çakışma önleme)"""
        import random
        import string
        
        base_name = base_name.lower().replace('_', '-')
        
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        
        return f"{base_name}-{suffix}"
    
    def set_environment_variables(self, project_id: str, env_vars: Dict[str, str]) -> Dict:
        """Vercel projesine environment variables set eder"""
        url = f"{self.base_url}/v9/projects/{project_id}/env"
        
        results = []
        
        for key, value in env_vars.items():
            data = {
                "key": key,
                "value": value,
                "type": "plain",  # "encrypted", "system", veya "plain"
                "target": ["production", "preview", "development"]  # Tüm environmentlarda kullan
            }
            
            print(f"Vercel Set Env Var Request: URL={url}, Key={key}")
            response = requests.post(url, headers=self.headers, json=data)
            print(f"Vercel Set Env Var Response: Status={response.status_code}, Body={response.text}")
            
            if response.status_code in [200, 201]:
                results.append({
                    'key': key,
                    'success': True,
                    'data': response.json()
                })
            else:
                results.append({
                    'key': key,
                    'success': False,
                    'error': response.text
                })
        
        return {'results': results}

    def get_environment_variables(self, project_id: str) -> Dict:
        """Vercel projesinin environment variables'larını getirir"""
        url = f"{self.base_url}/v9/projects/{project_id}/env"
        
        response = requests.get(url, headers=self.headers)
        print(f"Vercel Get Env Vars Response: Status={response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get environment variables: {response.text}")

    def update_environment_variable(self, project_id: str, env_id: str, value: str) -> Dict:
        """Mevcut environment variable'ı günceller"""
        url = f"{self.base_url}/v9/projects/{project_id}/env/{env_id}"
        
        data = {
            "value": value
        }
        
        response = requests.patch(url, headers=self.headers, json=data)
        print(f"Vercel Update Env Var Response: Status={response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to update environment variable: {response.text}")

    def delete_environment_variable(self, project_id: str, env_id: str) -> bool:
        """Environment variable'ı siler"""
        url = f"{self.base_url}/v9/projects/{project_id}/env/{env_id}"
        
        response = requests.delete(url, headers=self.headers)
        print(f"Vercel Delete Env Var Response: Status={response.status_code}")
        
        return response.status_code == 200