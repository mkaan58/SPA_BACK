# deployment/api/serializers.py
from rest_framework import serializers
from ..models import GitHubRepository, VercelDeployment, DeploymentSettings


class GitHubRepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GitHubRepository
        fields = [
            'id', 'repo_name', 'repo_url', 'repo_id', 
            'default_branch', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class VercelDeploymentSerializer(serializers.ModelSerializer):
    github_repo = GitHubRepositorySerializer(read_only=True)
    website_id = serializers.IntegerField(source='website.id', read_only=True)
    
    class Meta:
        model = VercelDeployment
        fields = [
            'id', 'deployment_id', 'project_id', 'deployment_url',
            'status', 'commit_sha', 'error_message', 'build_logs',
            'github_repo', 'created_at', 'updated_at', 'website_id'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DeploymentSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeploymentSettings
        fields = [
            'id', 'custom_domain_enabled', 'default_subdomain_prefix',
            'auto_deploy_enabled', 'build_command', 'output_directory',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DeployWebsiteSerializer(serializers.Serializer):
    website_id = serializers.IntegerField()


class DeploymentStatusSerializer(serializers.Serializer):
    deployment_id = serializers.IntegerField()