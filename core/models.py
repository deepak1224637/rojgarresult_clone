from django.db import models

class JobPost(models.Model):
    title =  models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    description = models.TextField()
    last_date = models.DateField()
    how_to_apply = models.TextField(blank=True, null=True)
    important_links = models.TextField(blank=True, null=True)
    important_dates = models.TextField(blank=True, null=True)
    eligibility = models.TextField(blank=True, null=True)
    age_limit = models.TextField(blank=True, null=True)
    exam_fee = models.TextField(blank=True, null=True)
    total_posts = models.CharField(max_length=50, blank=True)
    apply_link = models.URLField()
    posted_on = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.title


# ✅ Admit Card
class AdmitCard(models.Model):
    title = models.CharField(max_length=200)
    exam_date = models.DateField(null=True, blank=True)
    download_link = models.URLField()
    date_published = models.DateField(null=True, blank=True)
    posted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    


# ✅ Result
class Result(models.Model):
    title = models.CharField(max_length=200)
    result_date = models.DateField(null=True, blank=True)
    result_link = models.URLField()
    posted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# ✅ Syllabus
class Syllabus(models.Model):
    exam_name = models.CharField(max_length=200)
    syllabus_pdf = models.URLField(help_text="Google Drive / Direct PDF Link")
    posted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.exam_name
    

class HighlightPost(models.Model):
    title = models.CharField(max_length=200)
    post_count = models.PositiveIntegerField(default=0)
    link = models.URLField(null=True, blank=True)
    bg_color = models.CharField(
        max_length=20,
        help_text="Bootstrap background color (e.g. danger, primary, success)",
        default='primary'
    )
    posted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

# class HighlightPost(models.Model):
#     title = models.CharField(max_length=200)
#     content = models.TextField()
    
#     posted_on =models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.title



class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
