# Generated by Django 5.2 on 2025-05-27 18:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('spa', '0007_website_contact_email'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DeploymentSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('custom_domain_enabled', models.BooleanField(default=False)),
                ('default_subdomain_prefix', models.CharField(blank=True, max_length=50)),
                ('auto_deploy_enabled', models.BooleanField(default=True)),
                ('build_command', models.CharField(default='', max_length=255)),
                ('output_directory', models.CharField(default='', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='deployment_settings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GitHubRepository',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repo_name', models.CharField(max_length=255)),
                ('repo_url', models.URLField()),
                ('repo_id', models.CharField(max_length=50)),
                ('default_branch', models.CharField(default='main', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('website', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='github_repo', to='spa.website')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='VercelDeployment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deployment_id', models.CharField(max_length=255)),
                ('project_id', models.CharField(max_length=255)),
                ('deployment_url', models.URLField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('building', 'Building'), ('ready', 'Ready'), ('error', 'Error'), ('canceled', 'Canceled')], default='pending', max_length=20)),
                ('commit_sha', models.CharField(blank=True, max_length=40)),
                ('error_message', models.TextField(blank=True)),
                ('build_logs', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('github_repo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deployments', to='deployment.githubrepository')),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deployments', to='spa.website')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
