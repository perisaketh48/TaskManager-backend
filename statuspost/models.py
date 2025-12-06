from django.db import models
from django.conf import settings

class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Post by {self.user.username} at {self.created_at}"

class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  

    def __str__(self):
        return f"{self.user.username} liked {self.post}"  


class Comment(models.Model):
    user= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    post=models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    comment=models.CharField(max_length=555)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.user.username} commented on {self.post}: {self.comment[:20]}..."