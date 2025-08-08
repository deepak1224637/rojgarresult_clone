# from django.db import models


# # =========================
# #  Common Base Model
# # =========================
# class BasePost(models.Model):
#     title = models.TextField()  # No length limit
#     organization = models.CharField(max_length=255, blank=True, null=True)
#     short_title = models.CharField(max_length=255, blank=True, null=True)
#     category = models.CharField(max_length=100)  # e.g., Latest Job, Admit Card
#     state = models.CharField(max_length=100, blank=True, null=True)
#     notification_link = models.TextField(blank=True, null=True)  # PDF / official
#     description = models.TextField(blank=True, null=True)
#     raw_html = models.TextField(blank=True, null=True)  # Store raw scraped HTML
#     posted_on = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         abstract = True


# # =========================
# #  Latest Job
# # =========================
# class JobPost(BasePost):
#     last_date = models.DateField(blank=True, null=True)
#     how_to_apply = models.TextField(blank=True, null=True)
#     important_links = models.TextField(blank=True, null=True)
#     important_dates = models.TextField(blank=True, null=True)
#     eligibility = models.TextField(blank=True, null=True)
#     age_limit = models.TextField(blank=True, null=True)
#     exam_fee = models.TextField(blank=True, null=True)
#     total_posts = models.TextField(blank=True, null=True)
#     apply_link = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return self.title[:100]


# # =========================
# #  Admit Card
# # =========================
# class AdmitCard(BasePost):
#     exam_date = models.DateField(blank=True, null=True)
#     download_link = models.TextField(blank=True, null=True)
#     date_published = models.DateField(blank=True, null=True)

#     def __str__(self):
#         return self.title[:100]


# # =========================
# #  Result
# # =========================
# class Result(BasePost):
#     result_date = models.DateField(blank=True, null=True)
#     result_link = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return self.title[:100]


# # =========================
# #  Answer Key
# # =========================
# class AnswerKey(BasePost):
#     exam_date = models.DateField(blank=True, null=True)
#     answer_key_link = models.TextField(blank=True, null=True)
#     date_published = models.DateField(blank=True, null=True)

#     def __str__(self):
#         return self.title[:100]


# # =========================
# #  Syllabus
# # =========================
# class Syllabus(BasePost):
#     syllabus_pdf = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return self.title[:100]


# # =========================
# #  Admission
# # =========================
# class Admission(BasePost):
#     admission_date = models.DateField(blank=True, null=True)
#     admission_link = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return self.title[:100]


# # =========================
# #  Notification
# # =========================
# class Notification(BasePost):
#     notice_date = models.DateField(blank=True, null=True)
#     notice_link = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return self.title[:100]


# # =========================
# #  Highlights
# # =========================
# class HighlightPost(models.Model):
#     title = models.CharField(max_length=200)
#     post_count = models.PositiveIntegerField(default=0)
#     link = models.TextField(blank=True, null=True)
#     bg_color = models.CharField(
#         max_length=20,
#         help_text="Bootstrap color (e.g., primary, success, danger)",
#         default='primary'
#     )
#     posted_on = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.title


# # =========================
# #  Subscribers
# # =========================
# class Subscriber(models.Model):
#     email = models.EmailField(unique=True)
#     subscribed_on = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.email


# test 3.py  check 

from django.db import models


# =========================
#  Common Base Model
# =========================
class BasePost(models.Model):
    title = models.TextField()  # Full headline
    short_title = models.CharField(max_length=255, blank=True, null=True)  # Optional short name
    organization = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=100)  # e.g., Latest Job, Admit Card
    state = models.CharField(max_length=100, blank=True, null=True)

    # Links & description
    notification_link = models.TextField(blank=True, null=True)  # PDF / official
    description = models.TextField(blank=True, null=True)
    full_link = models.URLField(blank=True, null=True)  # Canonical/full page URL
    apply_link = models.TextField(blank=True, null=True)  # For jobs/admissions
    image_url = models.URLField(blank=True, null=True)

    # SEO & metadata
    publish_date = models.CharField(max_length=100, blank=True, null=True)
    updated_date = models.CharField(max_length=100, blank=True, null=True)

    # Store raw HTML (optional)
    raw_html = models.TextField(blank=True, null=True)

    posted_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title[:100]


# =========================
#  Latest Job
# =========================
class JobPost(BasePost):
    last_date = models.DateField(blank=True, null=True)
    how_to_apply = models.TextField(blank=True, null=True)
    important_links = models.TextField(blank=True, null=True)
    important_dates = models.TextField(blank=True, null=True)
    eligibility = models.TextField(blank=True, null=True)
    age_limit = models.TextField(blank=True, null=True)
    exam_fee = models.TextField(blank=True, null=True)
    total_posts = models.TextField(blank=True, null=True)


# =========================
#  Admit Card
# =========================
class AdmitCard(BasePost):
    exam_date = models.DateField(blank=True, null=True)
    download_link = models.TextField(blank=True, null=True)
    date_published = models.DateField(blank=True, null=True)


# =========================
#  Result
# =========================
class Result(BasePost):
    result_date = models.DateField(blank=True, null=True)
    result_link = models.TextField(blank=True, null=True)


# =========================
#  Answer Key
# =========================
class AnswerKey(BasePost):
    exam_date = models.DateField(blank=True, null=True)
    answer_key_link = models.TextField(blank=True, null=True)
    date_published = models.DateField(blank=True, null=True)


# =========================
#  Syllabus
# =========================
class Syllabus(BasePost):
    syllabus_pdf = models.TextField(blank=True, null=True)


# =========================
#  Admission
# =========================
class Admission(BasePost):
    admission_date = models.DateField(blank=True, null=True)
    admission_link = models.TextField(blank=True, null=True)


# =========================
#  Notification
# =========================
class Notification(BasePost):
    notice_date = models.DateField(blank=True, null=True)
    notice_link = models.TextField(blank=True, null=True)


# =========================
#  Highlights
# =========================
class HighlightPost(models.Model):
    title = models.CharField(max_length=200)
    post_count = models.PositiveIntegerField(default=0)
    link = models.TextField(blank=True, null=True)
    bg_color = models.CharField(
        max_length=20,
        help_text="Bootstrap color (e.g., primary, success, danger)",
        default='primary'
    )
    posted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# =========================
#  Subscribers
# =========================
class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
