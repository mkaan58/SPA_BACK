# deployment/admin.py
from django.contrib import admin
from .models import GitHubRepository, VercelDeployment, DeploymentSettings


@admin.register(GitHubRepository)
class GitHubRepositoryAdmin(admin.ModelAdmin):
    list_display = ['repo_name', 'website', 'repo_url', 'created_at']
    list_filter = ['created_at']
    search_fields = ['repo_name', 'website__title', 'website__user__email']
    readonly_fields = ['repo_id', 'created_at', 'updated_at']


@admin.register(VercelDeployment)
class VercelDeploymentAdmin(admin.ModelAdmin):
    list_display = ['website', 'status', 'deployment_url', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['website__title', 'website__user__email', 'deployment_url']
    readonly_fields = ['deployment_id', 'project_id', 'created_at', 'updated_at']


@admin.register(DeploymentSettings)
class DeploymentSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'auto_deploy_enabled', 'custom_domain_enabled', 'created_at']
    list_filter = ['auto_deploy_enabled', 'custom_domain_enabled', 'created_at']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']