from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from  django.dispatch import receiver

# Create your models here.

class Job(models.Model):
        title = models.CharField(max_length=100)
        description = models.TextField()
        skill_required = models.TextField() 
        posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
        created_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
                return self.title

class Application(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Shortlisted', 'Shortlisted'),
        ('Rejected', 'Rejected'),
    )

    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/')
    match_score = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    class Meta: unique_together = ('job','applicant')
    
    def __str__(self):
        return f"{self.applicant.username} - {self.job.title}"
        
class Profile(models.Model):
        ROLE_CHOICES = (
                ('recruiter' , 'Recruiter'),
                ('jobseeker', 'Job Seeker'),
        )

        user = models.OneToOneField(User, on_delete=models.CASCADE)
        role = models.CharField(max_length=20, choices=ROLE_CHOICES)

        def __str__(self):
            return f"{self.user.username} - {self.role}"
        

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
       if created:
              Profile.objects.create(user = instance, role='jobseeker')
        