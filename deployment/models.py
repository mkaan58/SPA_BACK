# deployment/models.py
from django.db import models
from users.models import User
from spa.models import Website
from django.utils import timezone


class GitHubRepository(models.Model):
    website = models.OneToOneField(Website, on_delete=models.CASCADE, related_name='github_repo')
    repo_name = models.CharField(max_length=255)
    repo_url = models.URLField()
    repo_id = models.CharField(max_length=50)  # GitHub repo ID
    default_branch = models.CharField(max_length=50, default='main')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.repo_name} - {self.website.title}"


class VercelDeployment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('building', 'Building'),
        ('ready', 'Ready'),
        ('error', 'Error'),
        ('canceled', 'Canceled'),
    ]
    
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name='deployments')
    github_repo = models.ForeignKey(GitHubRepository, on_delete=models.CASCADE, related_name='deployments')
    deployment_id = models.CharField(max_length=255)  # Vercel deployment ID
    project_id = models.CharField(max_length=255)     # Vercel project ID
    deployment_url = models.URLField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    project_name = models.CharField(max_length=255, blank=True)  # Yeni alan
    commit_sha = models.CharField(max_length=40, blank=True)
    error_message = models.TextField(blank=True)
    build_logs = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        status_display = self.get_status_display() if self.status else 'Unknown'
        return f"{self.website.title} - {status_display}"


class DeploymentSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='deployment_settings')
    
    # Custom domain settings (future feature)
    custom_domain_enabled = models.BooleanField(default=False)
    default_subdomain_prefix = models.CharField(max_length=50, blank=True)  # user preferences for subdomain
    
    # Deployment preferences
    auto_deploy_enabled = models.BooleanField(default=True)
    build_command = models.CharField(max_length=255, default='')
    output_directory = models.CharField(max_length=100, default='')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Deployment Settings - {self.user.email}"