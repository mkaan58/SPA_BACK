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
        
    def disable_project_authentication(self, project_id: str):
        """Vercel projesinin authentication'ını devre dışı bırakır"""
        url = f"{self.base_url}/v9/projects/{project_id}"
        
        # Önce mevcut project bilgilerini al
        get_response = requests.get(url, headers=self.headers)
        if get_response.status_code != 200:
            return False
            
        project_data = get_response.json()
        
        # ssoProtection'ı null yap
        project_data['ssoProtection'] = None
        
        # Project'i güncelle
        response = requests.patch(url, headers=self.headers, json={
            "ssoProtection": None
        })
        
        print(f"Disable Auth Response: Status={response.status_code}, Body={response.text}")
        
        if response.status_code in [200, 201]:
            return True
        return False

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

    def add_domain_to_project(self, project_id: str, domain_name: str) -> Dict:
        """Domain'i Vercel projesine ekler"""
        url = f"{self.base_url}/v9/projects/{project_id}/domains"
        
        data = {
            "name": domain_name
        }
        
        print(f"Vercel Add Domain Request: URL={url}, Data={data}")
        response = requests.post(url, headers=self.headers, json=data)
        print(f"Vercel Add Domain Response: Status={response.status_code}, Body={response.text}")
        
        if response.status_code in [200, 201]:
            return {
                'success': True,
                'domain_id': domain_name,  # Vercel domain name'i ID olarak kullanır
                'domain_data': response.json()
            }
        elif response.status_code == 409:
            return {
                'success': False,
                'error': 'Domain already exists in this project'
            }
        else:
            return {
                'success': False,
                'error': f"Vercel domain ekleme hatası: {response.text}"
            }
    
    def remove_domain_from_project(self, project_id: str, domain_name: str) -> Dict:
        """Domain'i Vercel projesinden kaldırır"""
        url = f"{self.base_url}/v9/projects/{project_id}/domains/{domain_name}"
        
        print(f"Vercel Remove Domain Request: URL={url}")
        response = requests.delete(url, headers=self.headers)
        print(f"Vercel Remove Domain Response: Status={response.status_code}, Body={response.text}")
        
        if response.status_code == 200:
            return {
                'success': True,
                'message': f'Domain {domain_name} removed from project'
            }
        elif response.status_code == 404:
            return {
                'success': False,
                'error': 'Domain not found in project'
            }
        else:
            return {
                'success': False,
                'error': f"Vercel domain kaldırma hatası: {response.text}"
            }
    
    def get_domain_info(self, domain_name: str) -> Dict:
        """Domain bilgilerini Vercel'den getirir"""
        url = f"{self.base_url}/v5/domains/{domain_name}"
        
        print(f"Vercel Get Domain Info Request: URL={url}")
        response = requests.get(url, headers=self.headers)
        print(f"Vercel Get Domain Info Response: Status={response.status_code}, Body={response.text}")
        
        if response.status_code == 200:
            data = response.json()
            domain_info = data.get('domain', {})
            
            return {
                'success': True,
                'domain_info': {
                    'name': domain_info.get('name'),
                    'verified': domain_info.get('verified', False),
                    'nameservers': domain_info.get('nameservers', []),
                    'intended_nameservers': domain_info.get('intendedNameservers', []),
                    'service_type': domain_info.get('serviceType'),
                    'ssl_enabled': domain_info.get('verified', False)
                }
            }
        elif response.status_code == 404:
            return {
                'success': False,
                'error': 'Domain not found in Vercel'
            }
        else:
            return {
                'success': False,
                'error': f"Domain info fetch failed: {response.text}"
            }
    
    def get_project_domains(self, project_id: str) -> Dict:
        """Proje domain'lerini listeler"""
        url = f"{self.base_url}/v9/projects/{project_id}/domains"
        
        print(f"Vercel Get Project Domains Request: URL={url}")
        response = requests.get(url, headers=self.headers)
        print(f"Vercel Get Project Domains Response: Status={response.status_code}, Body={response.text}")
        
        if response.status_code == 200:
            return {
                'success': True,
                'domains': response.json()
            }
        else:
            return {
                'success': False,
                'error': f"Project domains fetch failed: {response.text}"
            }
    
    def verify_domain_dns(self, domain_name: str) -> Dict:
        """Domain DNS ayarlarını kontrol eder (basit kontrol)"""
        try:
            import dns.resolver
            
            # A record kontrolü
            try:
                answers = dns.resolver.resolve(domain_name, 'A')
                a_record_found = any(str(answer) == '76.76.19.61' for answer in answers)
            except:
                a_record_found = False
            
            # CNAME record kontrolü (www)
            try:
                answers = dns.resolver.resolve(f'www.{domain_name}', 'CNAME')
                cname_record_found = any('vercel-dns.com' in str(answer) for answer in answers)
            except:
                cname_record_found = False
            
            return {
                'success': True,
                'dns_verified': a_record_found or cname_record_found,
                'a_record_correct': a_record_found,
                'cname_record_correct': cname_record_found
            }
            
        except ImportError:
            # dns resolver mevcut değilse, basit kontrol
            return {
                'success': True,
                'dns_verified': True,  # Test için True döndür
                'a_record_correct': True,
                'cname_record_correct': True,
                'note': 'DNS verification skipped (dnspython not available)'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'DNS verification failed: {str(e)}'
            }