# deployment/api/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from spa.models import Website
from ..models import VercelDeployment
from ..services.deployment_service import DeploymentService
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Website)
def auto_deploy_website(sender, instance, created, **kwargs):
    """Website güncellendiğinde otomatik deploy tetikler"""
    if not created:  # Sadece güncelleme durumunda
        try:
            # Kullanıcının auto-deploy ayarını kontrol et
            from ..models import DeploymentSettings
            settings = DeploymentSettings.objects.filter(user=instance.user).first()
            
            if settings and settings.auto_deploy_enabled:
                # Varolan deployment var mı kontrol et
                deployment = VercelDeployment.objects.filter(website=instance).first()
                
                if deployment:
                    # Deployment service ile güncelle
                    deployment_service = DeploymentService()
                    deployment_service.deploy_website(instance.id)
                    logger.info(f"Auto-deployment triggered for website {instance.id}")
                    
        except Exception as e:
            logger.exception(f"Auto-deployment failed for website {instance.id}: {str(e)}")


@receiver(post_delete, sender=Website)
def cleanup_deployments(sender, instance, **kwargs):
    """Website silindiğinde deployment'ları temizler"""
    try:
        # GitHub repo'yu sil (isteğe bağlı)
        github_repo = instance.github_repo if hasattr(instance, 'github_repo') else None
        if github_repo:
            deployment_service = DeploymentService()
            deployment_service.github.delete_repository(github_repo.repo_name)
            logger.info(f"GitHub repository {github_repo.repo_name} deleted")
            
        # Vercel project'i sil (isteğe bağlı)
        deployments = VercelDeployment.objects.filter(website=instance)
        for deployment in deployments:
            deployment_service = DeploymentService()
            deployment_service.vercel.delete_project(deployment.project_id)
            logger.info(f"Vercel project {deployment.project_id} deleted")
            
    except Exception as e:
        logger.exception(f"Cleanup failed for website {instance.id}: {str(e)}")