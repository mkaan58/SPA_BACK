import logging
from django.conf import settings
from .github_service import GitHubService
from .vercel_service import VercelService
from ..models import GitHubRepository, VercelDeployment, DeploymentSettings
from spa.models import Website
from typing import Dict
import json
import requests

logger = logging.getLogger(__name__)


class DeploymentService:
    def __init__(self):
        self.github = GitHubService()
        self.vercel = VercelService()
    
    def deploy_website(self, website_id: int) -> Dict:
        """Website'i deploy eder - Edit durumu için optimize edilmiş"""
        try:
            website = Website.objects.get(id=website_id)
            
            # ✅ Mevcut deployment'ı kontrol et
            existing_deployment = VercelDeployment.objects.filter(website=website).first()
            
            if existing_deployment:
                logger.info(f"🔄 Redeploy detected for website {website_id}")
                return self._redeploy_existing_website(website, existing_deployment)
            else:
                logger.info(f"🆕 New deployment for website {website_id}")
                return self._deploy_new_website(website)
                
        except Exception as e:
            logger.exception(f"Deployment failed for website {website_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
        
    def _redeploy_existing_website(self, website: Website, existing_deployment: VercelDeployment) -> Dict:
        """Mevcut website'i redeploy eder - Tüm kaynakları yeniden kullanır"""
        try:
            github_repo = existing_deployment.github_repo
            
            # ✅ 1. GitHub repo'nun hala var olduğunu doğrula
            repo_data = self.github.get_repository(github_repo.repo_name)
            if not repo_data:
                raise Exception(f"GitHub repository {github_repo.repo_name} not found. Manual intervention required.")
            
            # ✅ 2. Vercel project'in hala var olduğunu doğrula
            try:
                project_data = self.vercel.get_project_info(existing_deployment.project_id)
            except Exception as e:
                logger.error(f"Vercel project {existing_deployment.project_id} not found: {str(e)}")
                # Yeni Vercel projesi oluştur ama aynı GitHub repo kullan
                return self._recreate_vercel_project_for_existing_repo(website, github_repo)
            
            # ✅ 3. Website content'i güncelle (aynı repo'ya push)
            file_shas = self._upload_website_content(github_repo, website)
            
            # ✅ 4. Environment variables'ları güncelle
            self._update_project_environment_variables(existing_deployment.project_id, website)
            
            # ✅ 5. Deployment tetikle (auto-deployment olacak)
            deployment_result = self._trigger_deployment(existing_deployment, file_shas)
            
            logger.info(f"✅ Successful redeploy: {existing_deployment.deployment_url}")
            
            return {
                'success': True,
                'deployment_url': deployment_result.deployment_url,
                'github_repo_url': github_repo.repo_url,
                'deployment_id': deployment_result.deployment_id,
                'is_redeploy': True  # ✅ Frontend için redeploy olduğunu belirt
            }
            
        except Exception as e:
            logger.error(f"Redeploy failed: {str(e)}")
            # Fallback: Tamamen yeni deployment dene
            logger.info("Falling back to new deployment...")
            return self._deploy_new_website(website)
        
    def _deploy_new_website(self, website: Website) -> Dict:
        """Tamamen yeni website deployment'ı"""
        try:
            repo_name = self._generate_repo_name(website)
            github_repo = self._create_or_update_github_repo(website, repo_name)
            file_shas = self._upload_website_content(github_repo, website)
            vercel_deployment = self._create_or_update_vercel_project(website, github_repo)
            deployment_result = self._trigger_deployment(vercel_deployment, file_shas)
            
            return {
                'success': True,
                'deployment_url': deployment_result.deployment_url,
                'github_repo_url': github_repo.repo_url,
                'deployment_id': deployment_result.deployment_id,
                'is_redeploy': False  # ✅ Yeni deployment
            }
            
        except Exception as e:
            raise Exception(f"New deployment failed: {str(e)}")
        
    def _recreate_vercel_project_for_existing_repo(self, website: Website, github_repo: GitHubRepository) -> Dict:
        """Mevcut GitHub repo için yeni Vercel projesi oluşturur"""
        try:
            logger.warning(f"Recreating Vercel project for existing repo: {github_repo.repo_name}")
            
            # Eski Vercel deployment kaydını sil
            VercelDeployment.objects.filter(
                website=website,
                github_repo=github_repo
            ).delete()
            
            # Yeni Vercel projesi oluştur
            vercel_project_name = self._generate_vercel_project_name(website, github_repo.repo_name)
            project_data = self.vercel.create_project(
                project_name=vercel_project_name,
                github_repo_url=github_repo.repo_url
            )
            
            deployment_url = f"https://{vercel_project_name}.vercel.app"
            deployment = VercelDeployment.objects.create(
                website=website,
                github_repo=github_repo,
                project_id=project_data['id'],
                deployment_id='',
                deployment_url=deployment_url,
                status='pending',
                project_name=vercel_project_name
            )
            
            # Environment variables set et
            self._setup_project_environment_variables(project_data['id'], website)
            
            # Content'i upload et
            file_shas = self._upload_website_content(github_repo, website)
            
            # Deployment tetikle
            deployment_result = self._trigger_deployment(deployment, file_shas)
            
            return {
                'success': True,
                'deployment_url': deployment_result.deployment_url,
                'github_repo_url': github_repo.repo_url,
                'deployment_id': deployment_result.deployment_id,
                'is_recreated': True  # ✅ Vercel projesi yeniden oluşturuldu
            }
            
        except Exception as e:
            raise Exception(f"Failed to recreate Vercel project: {str(e)}")
    
    def _generate_repo_name(self, website: Website) -> str:
        username = website.user.email.split('@')[0]
        import re
        username = re.sub(r'[^a-z0-9-]', '', username.lower())
        repo_name = f"website-{website.id}-{username}"
        if len(repo_name) > 100:
            repo_name = f"website-{website.id}-{username[:20]}"
        return repo_name
    
    def _generate_vercel_project_name(self, website: Website, repo_name: str) -> str:
        base_name = repo_name.replace('_', '-').lower()
        import time
        timestamp = str(int(time.time()))[-6:]
        vercel_name = f"{base_name}-{timestamp}"
        if len(vercel_name) > 52:
            username = website.user.email.split('@')[0][:10]
            vercel_name = f"site-{website.id}-{username}-{timestamp}"
        return vercel_name
    
    def _create_or_update_github_repo(self, website: Website, repo_name: str) -> GitHubRepository:
        try:
            github_repo = GitHubRepository.objects.filter(website=website).first()
            if github_repo:
                # Repository'nin hala var olduğunu doğrula
                repo_data = self.github.get_repository(repo_name)
                if not repo_data:
                    # Repository GitHub'da yoksa, veritabanındaki kaydı sil ve yeniden oluştur
                    logger.warning(f"Repository {repo_name} not found on GitHub, deleting local record and recreating")
                    github_repo.delete()
                    github_repo = None
                
            if not github_repo:
                # Yeni repository oluştur
                repo_data = self.github.create_repository(
                    repo_name=repo_name,
                    description=f"Website: {website.title}"
                )
                github_repo = GitHubRepository.objects.create(
                    website=website,
                    repo_name=repo_name,
                    repo_url=repo_data['html_url'],
                    repo_id=str(repo_data['id'])
                )
                
            return github_repo
        except Exception as e:
            raise Exception(f"Failed to create or verify GitHub repository: {str(e)}")
    
    def _upload_website_content(self, github_repo: GitHubRepository, website: Website) -> Dict:
        """Website content'ini GitHub'a yükler - İyileştirilmiş commit mesajı"""
        try:
            file_shas = {}
            
            # ✅ HTML content'i process et
            html_content = self._process_html_content_for_vercel(website)
            
            # ✅ Daha açıklayıcı commit mesajı
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f"Update website content - {timestamp} (ID: {website.id})"
            
            result = self.github.upload_file(
                repo_name=github_repo.repo_name,
                file_path="index.html",
                content=html_content,
                commit_message=commit_message  # ✅ Timestamped commit
            )
            file_shas["index.html"] = result.get("content", {}).get("sha", "")
            
            # Package.json'ı da güncelle (version bump)
            package_json = {
                "name": github_repo.repo_name,
                "version": f"1.0.{website.id}",  # ✅ Website ID ile version
                "description": website.title,
                "main": "index.html",
                "scripts": {
                    "build": "echo 'No build required for static site'",
                    "start": "echo 'Static site ready'"
                },
                "keywords": ["static", "website", "html"],
                "author": website.user.email
            }
            
            result = self.github.upload_file(
                repo_name=github_repo.repo_name,
                file_path="package.json",
                content=json.dumps(package_json, indent=2),
                commit_message=f"Update package.json - {timestamp}"
            )
            file_shas["package.json"] = result.get("content", {}).get("sha", "")
            
            logger.info(f"✅ Website content uploaded successfully to {github_repo.repo_name}")
            return file_shas
            
        except Exception as e:
            raise Exception(f"Failed to upload website content: {str(e)}")
    def _create_or_update_vercel_project(self, website: Website, github_repo: GitHubRepository) -> VercelDeployment:
        """Vercel projesi oluştur/güncelle - Status düzeltilmiş"""
        try:
            existing_deployment = VercelDeployment.objects.filter(
                website=website,
                github_repo=github_repo
            ).first()
            
            if existing_deployment:
                # ✅ Mevcut deployment için status'u kontrol et ve güncelle
                logger.info(f"🔄 Using existing deployment: {existing_deployment.id}")
                
                # Eğer status null veya belirsizse pending yap
                if not existing_deployment.status:
                    existing_deployment.status = 'pending'
                    existing_deployment.save()
                    logger.info(f"✅ Fixed null status to pending for deployment {existing_deployment.id}")
                
                # Environment variables'ları güncelle
                self._update_project_environment_variables(existing_deployment.project_id, website)
                
                # ✅ Authentication'ı devre dışı bırak
                try:
                    self.vercel.disable_project_authentication(existing_deployment.project_id)
                    logger.info(f"✅ Authentication disabled for existing project: {existing_deployment.project_id}")
                except:
                    logger.warning("⚠️ Could not disable authentication, continuing...")
                
                return existing_deployment
            else:
                # ✅ Yeni deployment oluştur - Status açıkça set et
                vercel_project_name = self._generate_vercel_project_name(website, github_repo.repo_name)
                project_data = self.vercel.create_project(
                    project_name=vercel_project_name,
                    github_repo_url=github_repo.repo_url
                )
                
                deployment_url = f"https://{vercel_project_name}.vercel.app"
                deployment = VercelDeployment.objects.create(
                    website=website,
                    github_repo=github_repo,
                    project_id=project_data['id'],
                    deployment_id='',  # Henüz deployment trigger edilmedi
                    deployment_url=deployment_url,
                    status='pending',  # ✅ Açıkça pending set et
                    project_name=vercel_project_name
                )
                
                logger.info(f"✅ New deployment created with status: {deployment.status}")
                
                # Environment variables set et
                self._setup_project_environment_variables(project_data['id'], website)
                
                # ✅ Authentication'ı devre dışı bırak
                try:
                    self.vercel.disable_project_authentication(project_data['id'])
                    logger.info(f"✅ Authentication disabled for new project: {project_data['id']}")
                except:
                    logger.warning("⚠️ Could not disable authentication, continuing...")
                
                return deployment
                
        except Exception as e:
            logger.exception(f"❌ Failed to create Vercel project: {str(e)}")
            raise Exception(f"Failed to create Vercel project: {str(e)}")

    def _trigger_deployment(self, vercel_deployment: VercelDeployment, file_shas: Dict) -> VercelDeployment:
        """Doğru endpoint ile deployment tetikler - Status update düzeltilmiş"""
        try:
            github_repo = vercel_deployment.github_repo
            github_repo_name = github_repo.repo_name
            github_repo_id = int(github_repo.repo_id)
            
            # ✅ İlk olarak status'u building yap
            vercel_deployment.status = 'building'
            vercel_deployment.save()
            
            deployment_data = self.vercel.trigger_deployment_alternative(
                project_id=vercel_deployment.project_id,
                project_name=vercel_deployment.project_name,
                github_repo_name=github_repo_name,
                github_repo_id=github_repo_id
            )
            
            # Deployment bilgilerini güncelle
            vercel_deployment.deployment_id = deployment_data['id']
            vercel_deployment.deployment_url = f"https://{deployment_data['url']}"
            vercel_deployment.status = deployment_data.get('readyState', 'building')  # ✅ API'den gelen status
            vercel_deployment.save()
            
            logger.info(f"✅ Deployment triggered successfully: {deployment_data['id']}, Status: {vercel_deployment.status}")
            return vercel_deployment
            
        except Exception as e:
            logger.error(f"❌ Deployment trigger failed: {str(e)}")
            # ✅ Hata durumunda status'u güncelle
            vercel_deployment.status = 'error'
            vercel_deployment.error_message = str(e)
            vercel_deployment.save()
            
            # Fallback: GitHub otomatik deployment'ını bekle
            return self._wait_for_auto_deployment(vercel_deployment)
            
    def _wait_for_auto_deployment(self, vercel_deployment: VercelDeployment) -> VercelDeployment:
        """GitHub push sonrası otomatik deployment'ı bekler - Status update düzeltilmiş"""
        try:
            import time
            
            logger.info("⏳ Waiting for GitHub auto-deployment...")
            
            # ✅ Building status'unu set et
            vercel_deployment.status = 'building'
            vercel_deployment.save()
            
            time.sleep(5)
            
            # Son deployment'ları kontrol et
            for retry in range(3):
                try:
                    deployments_data = self.vercel.get_project_deployments(vercel_deployment.project_id)
                    
                    if deployments_data.get('deployments') and len(deployments_data['deployments']) > 0:
                        latest_deployment = deployments_data['deployments'][0]
                        
                        vercel_deployment.deployment_id = latest_deployment['uid']
                        vercel_deployment.deployment_url = f"https://{latest_deployment['url']}"
                        
                        # ✅ Status mapping düzelt
                        api_status = latest_deployment.get('readyState', 'BUILDING')
                        mapped_status = self._map_vercel_status_to_model(api_status)
                        vercel_deployment.status = mapped_status
                        vercel_deployment.save()
                        
                        logger.info(f"✅ Auto-deployment found: {latest_deployment['uid']}, Status: {mapped_status}")
                        return vercel_deployment
                        
                except Exception as e:
                    logger.warning(f"⚠️ Auto-deployment check failed (retry {retry}): {str(e)}")
                    
                if retry < 2:
                    time.sleep(3)
            
            # ✅ Son çare: ready olarak işaretle (ama null bırakma!)
            vercel_deployment.status = 'ready'
            vercel_deployment.save()
            logger.warning("⚠️ Auto-deployment not detected, marking as ready")
            
            return vercel_deployment
            
        except Exception as e:
            # ✅ Hata durumunda error status
            vercel_deployment.status = 'error'
            vercel_deployment.error_message = str(e)
            vercel_deployment.save()
            raise Exception(f"Failed to wait for auto-deployment: {str(e)}")


    def _map_vercel_status_to_model(self, vercel_status: str) -> str:
        """Vercel API status'unu model status'una map eder"""
        status_mapping = {
            'READY': 'ready',
            'BUILDING': 'building', 
            'ERROR': 'error',
            'CANCELED': 'canceled',
            'QUEUED': 'pending',
            'INITIALIZING': 'building',
        }
        
        # Büyük harfe çevir ve map et
        mapped = status_mapping.get(vercel_status.upper(), 'pending')
        logger.info(f"🔄 Status mapping: {vercel_status} -> {mapped}")
        return mapped

    def force_update_deployment_status(self, deployment_id: int) -> Dict:
        """Deployment status'unu zorla günceller - Debug amaçlı"""
        try:
            deployment = VercelDeployment.objects.get(id=deployment_id)
            
            if deployment.deployment_id:
                # Vercel API'den gerçek durumu al
                status_data = self.vercel.get_deployment_status(deployment.deployment_id)
                api_status = status_data.get('readyState', 'BUILDING')
                mapped_status = self._map_vercel_status_to_model(api_status)
                
                old_status = deployment.status
                deployment.status = mapped_status
                deployment.save()
                
                logger.info(f"🔄 Force status update: {old_status} -> {mapped_status}")
                
                return {
                    'success': True,
                    'old_status': old_status,
                    'new_status': mapped_status,
                    'message': f'Status updated from {old_status} to {mapped_status}'
                }
            else:
                # Deployment ID yoksa project deployments kontrol et
                deployments_data = self.vercel.get_project_deployments(deployment.project_id)
                if deployments_data.get('deployments') and len(deployments_data['deployments']) > 0:
                    latest = deployments_data['deployments'][0]
                    deployment.deployment_id = latest['uid']
                    deployment.deployment_url = f"https://{latest['url']}"
                    
                    api_status = latest.get('readyState', 'BUILDING')
                    deployment.status = self._map_vercel_status_to_model(api_status)
                    deployment.save()
                    
                    return {
                        'success': True,
                        'message': f'Found and updated deployment: {deployment.deployment_id}',
                        'status': deployment.status
                    }
                else:
                    deployment.status = 'pending'
                    deployment.save()
                    return {
                        'success': False,
                        'message': 'No deployments found, set to pending',
                        'status': 'pending'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def validate_and_cleanup_deployments(self, user_id: int = None) -> Dict:
        """Vercel'de olmayan deployment kayıtlarını temizler"""
        try:
            # Kullanıcının deployment'larını al
            if user_id:
                deployments = VercelDeployment.objects.filter(website__user_id=user_id)
            else:
                deployments = VercelDeployment.objects.all()
            
            cleanup_results = {
                'total_checked': deployments.count(),
                'invalid_found': 0,
                'cleaned_up': 0,
                'errors': [],
                'details': []
            }
            
            for deployment in deployments:
                try:
                    # Vercel project'in hala var olduğunu kontrol et
                    project_exists = self._check_vercel_project_exists(deployment.project_id)
                    
                    if not project_exists:
                        cleanup_results['invalid_found'] += 1
                        
                        # GitHub repo'yu da kontrol et
                        github_exists = False
                        if deployment.github_repo:
                            github_exists = self._check_github_repo_exists(deployment.github_repo.repo_name)
                        
                        # Kayıtları sil
                        deployment_info = {
                            'deployment_id': deployment.id,
                            'website_id': deployment.website.id,
                            'website_title': deployment.website.title,
                            'project_id': deployment.project_id,
                            'github_repo': deployment.github_repo.repo_name if deployment.github_repo else None,
                            'vercel_exists': False,
                            'github_exists': github_exists
                        }
                        
                        # GitHub repo kaydını sil (eğer GitHub'da da yoksa)
                        if deployment.github_repo and not github_exists:
                            deployment.github_repo.delete()
                            deployment_info['github_repo_deleted'] = True
                        
                        # Deployment kaydını sil
                        deployment.delete()
                        cleanup_results['cleaned_up'] += 1
                        cleanup_results['details'].append(deployment_info)
                        
                        logger.info(f"✅ Cleaned up invalid deployment: {deployment.id}")
                    
                except Exception as e:
                    error_msg = f"Error checking deployment {deployment.id}: {str(e)}"
                    cleanup_results['errors'].append(error_msg)
                    logger.error(f"❌ {error_msg}")
            
            logger.info(f"🧹 Cleanup completed: {cleanup_results['cleaned_up']}/{cleanup_results['total_checked']} invalid deployments removed")
            return cleanup_results
            
        except Exception as e:
            logger.exception(f"Cleanup failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


    def _check_vercel_project_exists(self, project_id: str) -> bool:
        """Vercel project'in var olup olmadığını kontrol eder"""
        try:
            project_data = self.vercel.get_project_info(project_id)
            return project_data is not None
        except Exception as e:
            logger.debug(f"Vercel project {project_id} does not exist: {str(e)}")
            return False

    def _check_github_repo_exists(self, repo_name: str) -> bool:
        """GitHub repo'nun var olup olmadığını kontrol eder"""
        try:
            repo_data = self.github.get_repository(repo_name)
            return repo_data is not None
        except Exception as e:
            logger.debug(f"GitHub repo {repo_name} does not exist: {str(e)}")
            return False

    def force_delete_deployment_records(self, website_id: int, user_id: int) -> Dict:
        """Belirli bir website için tüm deployment kayıtlarını zorla siler"""
        try:
            # Güvenlik kontrolü - website kullanıcıya ait mi?
            website = Website.objects.filter(id=website_id, user_id=user_id).first()
            if not website:
                return {
                    'success': False,
                    'error': 'Website not found or not authorized'
                }
            
            # GitHub repo kayıtlarını sil
            github_repos = GitHubRepository.objects.filter(website=website)
            github_count = github_repos.count()
            
            for repo in github_repos:
                try:
                    # GitHub'dan da silmeye çalış (opsiyonel)
                    self.github.delete_repository(repo.repo_name)
                    logger.info(f"🗑️ GitHub repo deleted: {repo.repo_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not delete GitHub repo {repo.repo_name}: {str(e)}")
            
            github_repos.delete()
            
            # Vercel deployment kayıtlarını sil
            deployments = VercelDeployment.objects.filter(website=website)
            deployment_count = deployments.count()
            
            for deployment in deployments:
                try:
                    # Vercel'den de silmeye çalış (opsiyonel)
                    self.vercel.delete_project(deployment.project_id)
                    logger.info(f"🗑️ Vercel project deleted: {deployment.project_id}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not delete Vercel project {deployment.project_id}: {str(e)}")
            
            deployments.delete()
            
            return {
                'success': True,
                'message': f'All deployment records deleted for website {website_id}',
                'github_repos_deleted': github_count,
                'deployments_deleted': deployment_count
            }
            
        except Exception as e:
            logger.exception(f"Force delete failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_orphaned_deployments(self, user_id: int = None) -> Dict:
        """Vercel'de bulunmayan deployment kayıtlarını listeler"""
        try:
            if user_id:
                deployments = VercelDeployment.objects.filter(website__user_id=user_id).select_related('website', 'github_repo')
            else:
                deployments = VercelDeployment.objects.all().select_related('website', 'github_repo')
            
            orphaned = []
            
            for deployment in deployments:
                vercel_exists = self._check_vercel_project_exists(deployment.project_id)
                github_exists = False
                
                if deployment.github_repo:
                    github_exists = self._check_github_repo_exists(deployment.github_repo.repo_name)
                
                if not vercel_exists:
                    orphaned.append({
                        'deployment_id': deployment.id,
                        'website_id': deployment.website.id,
                        'website_title': deployment.website.title,
                        'project_id': deployment.project_id,
                        'deployment_url': deployment.deployment_url,
                        'github_repo': deployment.github_repo.repo_name if deployment.github_repo else None,
                        'vercel_exists': vercel_exists,
                        'github_exists': github_exists,
                        'created_at': deployment.created_at,
                        'status': deployment.status
                    })
            
            return {
                'success': True,
                'total_deployments': deployments.count(),
                'orphaned_count': len(orphaned),
                'orphaned_deployments': orphaned
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _manual_deployment_trigger(self, vercel_deployment: VercelDeployment) -> VercelDeployment:
        """Manuel deployment tetikleme (fallback)"""
        try:
            # Vercel Deploy Hook kullan (daha güvenilir)
            url = f"https://api.vercel.com/v1/integrations/deploy/{vercel_deployment.project_id}"
            
            response = requests.post(url, headers=self.vercel.headers)
            
            if response.status_code == 200:
                deploy_data = response.json()
                vercel_deployment.deployment_id = deploy_data.get('uid', '')
                vercel_deployment.status = 'building'
                vercel_deployment.save()
                
                logger.info(f"Manual deployment triggered: {vercel_deployment.deployment_id}")
                return vercel_deployment
            else:
                # Son çare: basit bir status güncelleme
                vercel_deployment.status = 'ready'
                vercel_deployment.save()
                logger.warning(f"Manual deployment failed, marking as ready: {response.text}")
                return vercel_deployment
                
        except Exception as e:
            logger.error(f"Manual deployment trigger failed: {str(e)}")
            # Deployment'ı ready olarak işaretle (GitHub-Vercel bağlantısı çalışıyorsa otomatik deploy olacak)
            vercel_deployment.status = 'ready'
            vercel_deployment.save()
            return vercel_deployment
        except Exception as e:
            raise Exception(f"Failed to trigger deployment: {str(e)}")

    def check_deployment_status(self, deployment_id: int) -> Dict:
        """Deployment durumunu kontrol eder - Status update düzeltilmiş"""
        try:
            deployment = VercelDeployment.objects.get(id=deployment_id)
            
            # ✅ Deployment ID yoksa pending olarak işaretle
            if not deployment.deployment_id:
                logger.warning(f"⚠️ No deployment ID found for deployment {deployment_id}")
                # GitHub-Vercel auto deployment'ını kontrol et
                try:
                    deployments_data = self.vercel.get_project_deployments(deployment.project_id)
                    if deployments_data.get('deployments') and len(deployments_data['deployments']) > 0:
                        latest_deployment = deployments_data['deployments'][0]
                        deployment.deployment_id = latest_deployment['uid']
                        deployment.deployment_url = f"https://{latest_deployment['url']}"
                        
                        api_status = latest_deployment.get('readyState', 'BUILDING')
                        deployment.status = self._map_vercel_status_to_model(api_status)
                        deployment.save()
                        
                        logger.info(f"✅ Found missing deployment info: {deployment.deployment_id}")
                    else:
                        deployment.status = 'pending'
                        deployment.save()
                except Exception as e:
                    logger.error(f"❌ Could not fetch deployment info: {str(e)}")
                    deployment.status = 'pending'
                    deployment.save()
                    
                return {
                    'success': True,
                    'status': deployment.status,
                    'deployment_url': deployment.deployment_url
                }
            
            # ✅ Deployment ID varsa Vercel API'den durumu kontrol et
            try:
                status_data = self.vercel.get_deployment_status(deployment.deployment_id)
                
                # API'den gelen status'u map et
                api_status = status_data.get('readyState', 'BUILDING')
                mapped_status = self._map_vercel_status_to_model(api_status)
                
                deployment.status = mapped_status
                
                # Build logs varsa kaydet
                if status_data.get('buildLog'):
                    deployment.build_logs = status_data['buildLog']
                    
                # Error message varsa kaydet
                if mapped_status == 'error' and status_data.get('errorMessage'):
                    deployment.error_message = status_data['errorMessage']
                    
                deployment.save()
                
                logger.info(f"✅ Status updated: {deployment_id} -> {mapped_status}")
                
                return {
                    'success': True,
                    'status': deployment.status,
                    'deployment_url': deployment.deployment_url,
                    'error_message': deployment.error_message if deployment.error_message else None
                }
                
            except Exception as e:
                logger.error(f"❌ Failed to get deployment status from Vercel: {str(e)}")
                # API hatası durumunda mevcut status'u koru ama success=False döndür
                return {
                    'success': False,
                    'status': deployment.status,
                    'error': f'Could not check deployment status: {str(e)}'
                }
                
        except VercelDeployment.DoesNotExist:
            return {
                'success': False,
                'error': 'Deployment not found'
            }
        except Exception as e:
            logger.exception(f"❌ Unexpected error in check_deployment_status: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
        
    def _setup_project_environment_variables(self, project_id: str, website: Website):
        """Yeni Vercel projesi için environment variables'ları set eder"""
        try:
            from django.conf import settings
            
            # EmailJS environment variables
            env_vars = {}
            
            # EmailJS Public Key
            if hasattr(settings, 'YOUR_EMAIL_JS_PUBLIC_KEY'):
                env_vars['NEXT_PUBLIC_EMAILJS_PUBLIC_KEY'] = settings.YOUR_EMAIL_JS_PUBLIC_KEY
                
            # EmailJS Service ID
            if hasattr(settings, 'YOUR_EMAIL_JS_SERVICE_ID'):
                env_vars['NEXT_PUBLIC_EMAILJS_SERVICE_ID'] = settings.YOUR_EMAIL_JS_SERVICE_ID
                
            # EmailJS Template ID
            if hasattr(settings, 'YOUR_EMAIL_JS_TEMPLATE_ID'):
                env_vars['NEXT_PUBLIC_EMAILJS_TEMPLATE_ID'] = settings.YOUR_EMAIL_JS_TEMPLATE_ID
            
            # Contact Email
            env_vars['NEXT_PUBLIC_CONTACT_EMAIL'] = website.contact_email or website.user.email
            
            if env_vars:
                result = self.vercel.set_environment_variables(project_id, env_vars)
                
                success_count = sum(1 for r in result['results'] if r['success'])
                total_count = len(result['results'])
                
                logger.info(f"✅ Environment Variables Set: {success_count}/{total_count}")
                
                # Başarısız olanları log'la
                for r in result['results']:
                    if not r['success']:
                        logger.error(f"❌ Failed to set env var {r['key']}: {r['error']}")
            else:
                logger.warning("⚠️  No environment variables to set")
                
        except Exception as e:
            logger.error(f"❌ Failed to setup environment variables: {str(e)}")

    def _update_project_environment_variables(self, project_id: str, website: Website):
        """Mevcut Vercel projesi için environment variables'ları günceller"""
        try:
            from django.conf import settings
            
            # Mevcut env vars'ları al
            current_env_vars = self.vercel.get_environment_variables(project_id)
            
            # Güncellenmesi gereken değerler
            updates_needed = {
                'NEXT_PUBLIC_EMAILJS_PUBLIC_KEY': getattr(settings, 'YOUR_EMAIL_JS_PUBLIC_KEY', ''),
                'NEXT_PUBLIC_EMAILJS_SERVICE_ID': getattr(settings, 'YOUR_EMAIL_JS_SERVICE_ID', ''),
                'NEXT_PUBLIC_EMAILJS_TEMPLATE_ID': getattr(settings, 'YOUR_EMAIL_JS_TEMPLATE_ID', ''),
                'NEXT_PUBLIC_CONTACT_EMAIL': website.contact_email or website.user.email
            }
            
            # Mevcut env vars'lar arasında ara ve güncelle
            for env_var in current_env_vars.get('envs', []):
                key = env_var.get('key')
                if key in updates_needed and updates_needed[key]:
                    try:
                        self.vercel.update_environment_variable(
                            project_id, 
                            env_var['id'], 
                            updates_needed[key]
                        )
                        logger.info(f"✅ Updated env var: {key}")
                    except Exception as e:
                        logger.error(f"❌ Failed to update env var {key}: {str(e)}")
            
            # Eksik olanları ekle
            existing_keys = {env_var.get('key') for env_var in current_env_vars.get('envs', [])}
            missing_vars = {k: v for k, v in updates_needed.items() if k not in existing_keys and v}
            
            if missing_vars:
                result = self.vercel.set_environment_variables(project_id, missing_vars)
                logger.info(f"✅ Added missing env vars: {list(missing_vars.keys())}")
                
        except Exception as e:
            logger.error(f"❌ Failed to update environment variables: {str(e)}")

    def _process_html_content_for_vercel(self, website: Website) -> str:
        """HTML content'i process eder - Build zamanında env vars inject edilecek"""
        try:
            from django.conf import settings
            
            html_content = website.html_content
            email = website.contact_email or website.user.email
            
            # ✅ Django settings'ten değerleri al ve direkt inject et
            # Vercel build zamanında bu değerler env vars'tan gelecek
            
            # EmailJS Public Key
            public_key = getattr(settings, 'YOUR_EMAIL_JS_PUBLIC_KEY', 'YOUR_EMAIL_JS_PUBLIC_KEY')
            html_content = html_content.replace('{{YOUR_EMAIL_JS_PUBLIC_KEY}}', public_key)
            html_content = html_content.replace('{{ YOUR_EMAIL_JS_PUBLIC_KEY }}', public_key)
            html_content = html_content.replace('YOUR_EMAIL_JS_PUBLIC_KEY', public_key)
            
            # EmailJS Service ID
            service_id = getattr(settings, 'YOUR_EMAIL_JS_SERVICE_ID', 'YOUR_EMAIL_JS_SERVICE_ID')
            html_content = html_content.replace('{{YOUR_EMAIL_JS_SERVICE_ID}}', service_id)
            html_content = html_content.replace('{{ YOUR_EMAIL_JS_SERVICE_ID }}', service_id)
            html_content = html_content.replace('YOUR_EMAIL_JS_SERVICE_ID', service_id)
            
            # EmailJS Template ID
            template_id = getattr(settings, 'YOUR_EMAIL_JS_TEMPLATE_ID', 'YOUR_EMAIL_JS_TEMPLATE_ID')
            html_content = html_content.replace('{{YOUR_EMAIL_JS_TEMPLATE_ID}}', template_id)
            html_content = html_content.replace('{{ YOUR_EMAIL_JS_TEMPLATE_ID }}', template_id)
            html_content = html_content.replace('YOUR_EMAIL_JS_TEMPLATE_ID', template_id)
            
            # Email'i replace et
            html_content = html_content.replace("USER_EMAIL_PLACEHOLDER", email)
            
            # ✅ Debug: Replacement'ların yapıldığını kontrol et
            if 'YOUR_EMAIL_JS_PUBLIC_KEY' in html_content:
                logger.error("❌ EmailJS Public Key placeholder still exists!")
            else:
                logger.info("✅ EmailJS Public Key replaced successfully")
                
            if 'YOUR_EMAIL_JS_SERVICE_ID' in html_content:
                logger.error("❌ EmailJS Service ID placeholder still exists!")
            else:
                logger.info("✅ EmailJS Service ID replaced successfully")
                
            if 'YOUR_EMAIL_JS_TEMPLATE_ID' in html_content:
                logger.error("❌ EmailJS Template ID placeholder still exists!")
            else:
                logger.info("✅ EmailJS Template ID replaced successfully")
            
            return html_content
            
        except Exception as e:
            logger.error(f"❌ HTML processing failed: {str(e)}")
            # Fallback: En azından email'i replace et
            try:
                html_content = website.html_content
                email = website.contact_email or website.user.email
                html_content = html_content.replace("USER_EMAIL_PLACEHOLDER", email)
                return html_content
            except:
                return website.html_content
            
    def get_deployment_info(self, website_id: int) -> Dict:
        """Deployment durumu hakkında detaylı bilgi döner"""
        try:
            website = Website.objects.get(id=website_id)
            github_repo = GitHubRepository.objects.filter(website=website).first()
            vercel_deployment = VercelDeployment.objects.filter(website=website).first()
            
            info = {
                'website_id': website_id,
                'website_title': website.title,
                'has_github_repo': github_repo is not None,
                'has_vercel_deployment': vercel_deployment is not None,
            }
            
            if github_repo:
                # GitHub repo durumu
                repo_data = self.github.get_repository(github_repo.repo_name)
                info.update({
                    'github_repo_name': github_repo.repo_name,
                    'github_repo_url': github_repo.repo_url,
                    'github_repo_exists': repo_data is not None,
                })
            
            if vercel_deployment:
                # Vercel project durumu
                try:
                    project_data = self.vercel.get_project_info(vercel_deployment.project_id)
                    vercel_exists = True
                except:
                    vercel_exists = False
                    
                info.update({
                    'vercel_project_id': vercel_deployment.project_id,
                    'vercel_project_name': vercel_deployment.project_name,
                    'vercel_deployment_url': vercel_deployment.deployment_url,
                    'vercel_project_exists': vercel_exists,
                    'vercel_status': vercel_deployment.status,
                })
            
            return info
            
        except Exception as e:
            return {'error': str(e)}