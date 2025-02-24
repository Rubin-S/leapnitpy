from django.contrib.auth.models import User
from django.db import models
import os
import time




class Course(models.Model):
    COURSE_CHOICES = [
        ('JEE', 'JEE'),
        ('NEET', 'NEET'),
        ('JEE+NEET', 'JEE+NEET'),
    ]
    name = models.CharField(max_length=20, choices=COURSE_CHOICES)
    batch = models.CharField(max_length=50)
    course_id = models.CharField(max_length=100, unique=True)

    def save(self, *args, **kwargs):
        if not self.course_id:
            self.course_id = f"{self.name}-{self.batch}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.course_id

class UserData(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('administrator', 'Administrator'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userdata')
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=10, unique=True)
    school_name = models.CharField(max_length=255, blank=True, null=True)
    parent_email = models.EmailField(blank=True, null=True)
    parent_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)
    roll_no = models.CharField(max_length=50, blank=True, null=True)
    batch = models.CharField(max_length=50)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='userdata', default=None, blank=True, null=True)

    def __str__(self):
        return self.name

class Subject(models.Model):
    subject_name = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subjects', default=None, blank=True, null=True)

    def __str__(self):
        return f"{self.subject_name} ({self.course.name} - {self.course.batch})"


class Chapter(models.Model):
    chapter_name = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='chapters', default=None, blank=True, null=True)

    def __str__(self):
        return f"{self.chapter_name} ({self.subject.subject_name} - {self.subject.course})"



class StudyMaterial(models.Model):
    file = models.FileField(upload_to='study_materials/')
    description = models.TextField()
    chapter = models.ManyToManyField('Chapter', related_name='study_materials')


    def save(self, *args, **kwargs):
        # Save the file with current timestamp and its original extension
        if self.file and not self.file.name.startswith(str(int(time.time()))):
            # Get the original extension
            extension = os.path.splitext(self.file.name)[1]
            # Generate new filename with timestamp
            timestamp_filename = f"{int(time.time())}{extension}"
            self.file.name = timestamp_filename

        super().save(*args, **kwargs)  # Call the real save method




class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('numerical', 'Numerical'),
        ('option', 'Option'),
    ]
    TAG_CHOICES = [
        ('AI generated', 'AI generated'),
        ('PYQ', 'PYQ'),
        ('Expected Question', 'Expected Question'),
    ]
    question_text = models.TextField()
    option_a = models.CharField(max_length=255, null=True, blank=True)
    option_b = models.CharField(max_length=255, null=True, blank=True)
    option_c = models.CharField(max_length=255, null=True, blank=True)
    option_d = models.CharField(max_length=255, null=True, blank=True)
    correct_option = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], null=True, blank=True)
    type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    correct_answer_numerical_min = models.FloatField(null=True, blank=True)
    correct_answer_numerical_max = models.FloatField(null=True, blank=True)
    question_file = models.FileField(upload_to='questions/', null=True, blank=True)
    option_a_file = models.FileField(upload_to='questions/options/', null=True, blank=True)
    option_b_file = models.FileField(upload_to='questions/options/', null=True, blank=True)
    option_c_file = models.FileField(upload_to='questions/options/', null=True, blank=True)
    option_d_file = models.FileField(upload_to='questions/options/', null=True, blank=True)
    explanation = models.TextField(null=True, blank=True)
    explanation_file = models.FileField(upload_to='questions/explanations/', null=True, blank=True)
    marks_award = models.FloatField()
    marks_deduct = models.FloatField()
    chapter = models.ManyToManyField(Chapter, related_name='questions')
    tag = models.CharField(max_length=50, choices=TAG_CHOICES)
    visible = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question_text}"

    def save(self, *args, **kwargs):
        # Rename files with a timestamp
        file_fields = [
            'question_file', 'option_a_file', 'option_b_file',
            'option_c_file', 'option_d_file', 'explanation_file'
        ]
        for field_name in file_fields:
            file_field = getattr(self, field_name)
            if file_field:
                extension = os.path.splitext(file_field.name)[1]
                timestamp_filename = f"{int(time.time())}{extension}"
                file_field.name = timestamp_filename

        super().save(*args, **kwargs)



class Test(models.Model):
    test_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    test_name = models.TextField(max_length=100, null=True, blank=True)
    duration = models.DurationField()
    question_list = models.ManyToManyField(Question, related_name='tests')
    owner = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name="tests_owner", blank=True, null=True)
    result_released = models.BooleanField(default=False)
    accepting_response = models.BooleanField(default=True)
    def __str__(self):
        return self.test_id

    def save(self, *args, **kwargs):
        # Only assign a new test_id if it is not already set (i.e., on creation)
        if not self.test_id:
            timestamp_filename = f"{int(time.time())}"
            self.test_id = timestamp_filename
        super().save(*args, **kwargs)  # Call the real save method

class TestSubmitted(models.Model):
    user_email = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='tests_submitted')
    test_id = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='submissions')
    json_response = models.JSONField(blank=True, null=True)
    analysis = models.JSONField(blank=True, null=True)
    score = models.FloatField(default=0.0, blank=True, null=True)

    def __str__(self):
        return f"Submission for {self.test_id} by {self.user_email.name}"
