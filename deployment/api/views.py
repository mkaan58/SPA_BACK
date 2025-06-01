# deployment/api/views.py
import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from spa.models import Website
from ..models import GitHubRepository, VercelDeployment, DeploymentSettings
from ..services.deployment_service import DeploymentService
from .serializers import (
    GitHubRepositorySerializer,
    VercelDeploymentSerializer, 
    DeploymentSettingsSerializer,
    DeployWebsiteSerializer,
    DeploymentStatusSerializer
)

logger = logging.getLogger(__name__)


class DeploymentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def deploy_website(self, request):
        """Website'i deploy eder - Redeploy durumu için optimize edilmiş"""
        serializer = DeployWebsiteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        website_id = serializer.validated_data['website_id']
        
        # Website'in kullanıcıya ait olduğunu kontrol et
        website = get_object_or_404(Website, id=website_id, user=request.user)
        
        try:
            deployment_service = DeploymentService()
            
            # ✅ Mevcut deployment durumunu kontrol et
            existing_deployment = VercelDeployment.objects.filter(website=website).first()
            is_redeploy = existing_deployment is not None
            
            if is_redeploy:
                logger.info(f"🔄 Redeploy request for website {website_id}")
            else:
                logger.info(f"🆕 New deployment request for website {website_id}")
            
            result = deployment_service.deploy_website(website_id)
            
            if result['success']:
                # Deployment bilgilerini döndür
                deployment = VercelDeployment.objects.filter(website=website).first()
                serializer = VercelDeploymentSerializer(deployment)
                
                response_data = {
                    'success': True,
                    'message': 'Redeploy completed successfully' if is_redeploy else 'Website deployment started successfully',
                    'deployment': serializer.data,
                    'deployment_url': result['deployment_url'],
                    'github_repo_url': result['github_repo_url'],
                    'is_redeploy': result.get('is_redeploy', is_redeploy),
                    'is_recreated': result.get('is_recreated', False)
                }
                
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': result['error'],
                    'is_redeploy': is_redeploy
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.exception(f"Deployment error: {str(e)}")
            return Response({
                'success': False,
                'error': f"Deployment failed: {str(e)}",
                'is_redeploy': is_redeploy
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def check_status(self, request):
        """Deployment durumunu kontrol eder"""
        serializer = DeploymentStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        deployment_id = serializer.validated_data['deployment_id']
        
        # Deployment'ın kullanıcıya ait olduğunu kontrol et
        deployment = get_object_or_404(
            VercelDeployment, 
            id=deployment_id, 
            website__user=request.user
        )
        
        try:
            deployment_service = DeploymentService()
            result = deployment_service.check_deployment_status(deployment_id)
            
            return Response(result)
            
        except Exception as e:
            logger.exception(f"Status check error: {str(e)}")
            return Response({
                'success': False,
                'error': f"Status check failed: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def list_deployments(self, request):
        """Kullanıcının deployment'larını listeler"""
        deployments = VercelDeployment.objects.filter(website__user=request.user)
        serializer = VercelDeploymentSerializer(deployments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def list_repositories(self, request):
        """Kullanıcının GitHub repository'lerini listeler"""
        repos = GitHubRepository.objects.filter(website__user=request.user)
        serializer = GitHubRepositorySerializer(repos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def deployment_info(self, request):
        """Website deployment durumu hakkında detaylı bilgi döner"""
        website_id = request.query_params.get('website_id')
        
        if not website_id:
            return Response({
                'error': 'website_id parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Website'in kullanıcıya ait olduğunu kontrol et
        website = get_object_or_404(Website, id=website_id, user=request.user)
        
        try:
            deployment_service = DeploymentService()
            info = deployment_service.get_deployment_info(website_id)
            
            return Response(info)
            
        except Exception as e:
            logger.exception(f"Deployment info error: {str(e)}")
            return Response({
                'error': f"Failed to get deployment info: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def force_redeploy(self, request):
        """Zorla redeploy yapar - Sorun yaşanan durumlarda kullanılır"""
        serializer = DeployWebsiteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        website_id = serializer.validated_data['website_id']
        
        # Website'in kullanıcıya ait olduğunu kontrol et
        website = get_object_or_404(Website, id=website_id, user=request.user)
        
        try:
            deployment_service = DeploymentService()
            
            # ✅ Mevcut deployment'ları kontrol et
            existing_deployment = VercelDeployment.objects.filter(website=website).first()
            
            if existing_deployment:
                logger.info(f"🔄 Force redeploy for website {website_id}")
                
                # Manual trigger
                deployment_result = deployment_service._trigger_deployment(existing_deployment, {})
                
                return Response({
                    'success': True,
                    'message': 'Force redeploy triggered successfully',
                    'deployment_url': deployment_result.deployment_url,
                    'deployment_id': deployment_result.deployment_id
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': 'No existing deployment found for force redeploy'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.exception(f"Force redeploy error: {str(e)}")
            return Response({
                'success': False,
                'error': f"Force redeploy failed: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=False, methods=['post'])
    def force_status_update(self, request):
        """Deployment status'unu zorla günceller - Debug/Fix amaçlı"""
        deployment_id = request.data.get('deployment_id')
        
        if not deployment_id:
            return Response({
                'error': 'deployment_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Deployment'ın kullanıcıya ait olduğunu kontrol et
        deployment = get_object_or_404(
            VercelDeployment, 
            id=deployment_id, 
            website__user=request.user
        )
        
        try:
            deployment_service = DeploymentService()
            result = deployment_service.force_update_deployment_status(deployment_id)
            
            return Response(result)
            
        except Exception as e:
            logger.exception(f"Force status update error: {str(e)}")
            return Response({
                'success': False,
                'error': f"Force status update failed: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=False, methods=['post'])
    def fix_null_statuses(self, request):
        """Null status'ları düzeltir - Toplu fix"""
        try:
            deployment_service = DeploymentService()
            
            # Kullanıcının null status'lu deployment'larını bul
            null_deployments = VercelDeployment.objects.filter(
                website__user=request.user,
                status__isnull=True
            )
            
            fixed_count = 0
            results = []
            
            for deployment in null_deployments:
                try:
                    # Status'u pending olarak set et
                    deployment.status = 'pending'
                    deployment.save()
                    
                    # Gerçek status'u kontrol etmeye çalış
                    if deployment.deployment_id:
                        status_result = deployment_service.check_deployment_status(deployment.id)
                        results.append({
                            'deployment_id': deployment.id,
                            'fixed': True,
                            'new_status': deployment.status,
                            'api_check': status_result.get('success', False)
                        })
                    else:
                        results.append({
                            'deployment_id': deployment.id,
                            'fixed': True,
                            'new_status': 'pending',
                            'api_check': False,
                            'note': 'No deployment ID found'
                        })
                    
                    fixed_count += 1
                    
                except Exception as e:
                    results.append({
                        'deployment_id': deployment.id,
                        'fixed': False,
                        'error': str(e)
                    })
            
            return Response({
                'success': True,
                'message': f'Fixed {fixed_count} null status deployments',
                'total_null_found': null_deployments.count(),
                'fixed_count': fixed_count,
                'results': results
            })
            
        except Exception as e:
            logger.exception(f"Fix null statuses error: {str(e)}")
            return Response({
                'success': False,
                'error': f"Fix null statuses failed: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def debug_deployment(self, request):
        """Deployment debug bilgileri - Sorun tespiti için"""
        website_id = request.query_params.get('website_id')
        
        if not website_id:
            return Response({
                'error': 'website_id parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Website'in kullanıcıya ait olduğunu kontrol et
        website = get_object_or_404(Website, id=website_id, user=request.user)
        
        try:
            deployment_service = DeploymentService()
            
            # Deployment bilgilerini topla
            github_repo = GitHubRepository.objects.filter(website=website).first()
            vercel_deployment = VercelDeployment.objects.filter(website=website).first()
            
            debug_info = {
                'website_id': website_id,
                'website_title': website.title,
                'github_repo': None,
                'vercel_deployment': None,
                'vercel_api_status': None,
                'vercel_project_deployments': None
            }
            
            if github_repo:
                debug_info['github_repo'] = {
                    'id': github_repo.id,
                    'repo_name': github_repo.repo_name,
                    'repo_url': github_repo.repo_url,
                    'repo_id': github_repo.repo_id
                }
            
            if vercel_deployment:
                debug_info['vercel_deployment'] = {
                    'id': vercel_deployment.id,
                    'deployment_id': vercel_deployment.deployment_id,
                    'project_id': vercel_deployment.project_id,
                    'deployment_url': vercel_deployment.deployment_url,
                    'status': vercel_deployment.status,
                    'status_is_null': vercel_deployment.status is None,
                    'project_name': vercel_deployment.project_name,
                    'created_at': vercel_deployment.created_at,
                    'updated_at': vercel_deployment.updated_at
                }
                
                # Vercel API'den gerçek durumu kontrol et
                if vercel_deployment.deployment_id:
                    try:
                        api_status = deployment_service.vercel.get_deployment_status(vercel_deployment.deployment_id)
                        debug_info['vercel_api_status'] = api_status
                    except Exception as e:
                        debug_info['vercel_api_status'] = {'error': str(e)}
                
                # Project deployment'larını kontrol et
                try:
                    project_deployments = deployment_service.vercel.get_project_deployments(vercel_deployment.project_id)
                    debug_info['vercel_project_deployments'] = project_deployments
                except Exception as e:
                    debug_info['vercel_project_deployments'] = {'error': str(e)}
            
            return Response(debug_info)
            
        except Exception as e:
            logger.exception(f"Debug deployment error: {str(e)}")
            return Response({
                'error': f"Debug failed: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(detail=False, methods=['delete'])
    def cleanup_deployment(self, request):
        """Deployment'ı temizler - GitHub repo ve Vercel projesini siler"""
        website_id = request.query_params.get('website_id')
        
        if not website_id:
            return Response({
                'error': 'website_id parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Website'in kullanıcıya ait olduğunu kontrol et
        website = get_object_or_404(Website, id=website_id, user=request.user)
        
        try:
            deployment_service = DeploymentService()
            
            # GitHub repo'yu sil
            github_repo = GitHubRepository.objects.filter(website=website).first()
            if github_repo:
                success = deployment_service.github.delete_repository(github_repo.repo_name)
                if success:
                    github_repo.delete()
                    logger.info(f"✅ GitHub repo deleted: {github_repo.repo_name}")
            
            # Vercel projesi sil
            vercel_deployment = VercelDeployment.objects.filter(website=website).first()
            if vercel_deployment:
                success = deployment_service.vercel.delete_project(vercel_deployment.project_id)
                if success:
                    vercel_deployment.delete()
                    logger.info(f"✅ Vercel project deleted: {vercel_deployment.project_id}")
            
            return Response({
                'success': True,
                'message': 'Deployment cleanup completed successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.exception(f"Cleanup error: {str(e)}")
            return Response({
                'success': False,
                'error': f"Cleanup failed: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# deployment/api/views.py - Cleanup endpoint'leri eklendi

    @action(detail=False, methods=['post'])
    def cleanup_invalid_deployments(self, request):
        """Vercel'de olmayan deployment kayıtlarını temizler"""
        try:
            deployment_service = DeploymentService()
            result = deployment_service.validate_and_cleanup_deployments(user_id=request.user.id)
            
            if result.get('success', True):  # Eğer success key yoksa True olarak varsay
                return Response({
                    'success': True,
                    'message': f"Cleanup completed: {result['cleaned_up']} invalid deployments removed",
                    'details': result
                })
            else:
                return Response({
                    'success': False,
                    'error': result.get('error', 'Unknown error')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.exception(f"Cleanup error: {str(e)}")
            return Response({
                'success': False,
                'error': f"Cleanup failed: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def list_orphaned_deployments(self, request):
        """Vercel'de bulunmayan deployment kayıtlarını listeler"""
        try:
            deployment_service = DeploymentService()
            result = deployment_service.get_orphaned_deployments(user_id=request.user.id)
            
            return Response(result)
            
        except Exception as e:
            logger.exception(f"List orphaned error: {str(e)}")
            return Response({
                'success': False,
                'error': f"List orphaned failed: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['delete'])
    def force_delete_website_deployments(self, request):
        """Belirli bir website için tüm deployment kayıtlarını zorla siler"""
        website_id = request.query_params.get('website_id')
        
        if not website_id:
            return Response({
                'error': 'website_id parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            deployment_service = DeploymentService()
            result = deployment_service.force_delete_deployment_records(
                website_id=int(website_id), 
                user_id=request.user.id
            )
            
            if result['success']:
                return Response(result)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.exception(f"Force delete error: {str(e)}")
            return Response({
                'success': False,
                'error': f"Force delete failed: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def refresh_deployment_list(self, request):
        """Deployment listesini yeniler ve geçersiz kayıtları otomatik temizler"""
        try:
            deployment_service = DeploymentService()
            
            # 1. Önce geçersiz deployment'ları temizle
            cleanup_result = deployment_service.validate_and_cleanup_deployments(user_id=request.user.id)
            
            # 2. Sonra güncel deployment listesini döndür
            deployments = VercelDeployment.objects.filter(website__user=request.user)
            
            # 3. Her deployment için gerçek durumu kontrol et
            updated_deployments = []
            for deployment in deployments:
                try:
                    if deployment.deployment_id:
                        status_result = deployment_service.check_deployment_status(deployment.id)
                        if status_result.get('success'):
                            deployment.refresh_from_db()  # DB'den güncel veriyi al
                            
                    updated_deployments.append(deployment)
                except Exception as e:
                    logger.warning(f"Could not update deployment {deployment.id}: {str(e)}")
                    updated_deployments.append(deployment)
            
            serializer = VercelDeploymentSerializer(updated_deployments, many=True)
            
            return Response({
                'success': True,
                'message': f'Deployment list refreshed. Cleaned up {cleanup_result.get("cleaned_up", 0)} invalid records.',
                'cleanup_details': cleanup_result,
                'deployments': serializer.data
            })
            
        except Exception as e:
            logger.exception(f"Refresh deployment list error: {str(e)}")
            return Response({
                'success': False,
                'error': f"Refresh failed: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeploymentSettingsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = DeploymentSettingsSerializer
    
    def get_queryset(self):
        # Kullanıcının deployment ayarlarını getir veya oluştur
        settings, created = DeploymentSettings.objects.get_or_create(user=self.request.user)
        return DeploymentSettings.objects.filter(user=self.request.user)
    
    def get_object(self):
        # Tek bir ayar objesi döndür
        settings, created = DeploymentSettings.objects.get_or_create(user=self.request.user)
        return settings
    
    @action(detail=False, methods=['get'])
    def my_settings(self, request):
        """Kullanıcının deployment ayarlarını getirir"""
        settings = self.get_object()
        serializer = DeploymentSettingsSerializer(settings)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_settings(self, request):
        """Kullanıcının deployment ayarlarını günceller"""
        settings = self.get_object()
        serializer = DeploymentSettingsSerializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


