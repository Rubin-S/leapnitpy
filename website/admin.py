from django.contrib import admin
from .models import (
    UserData, Course, Subject, Chapter, StudyMaterial,
    Question, Test, TestSubmitted
)

@admin.register(UserData)
class UserDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'role', 'roll_no')
    search_fields = ('name', 'email', 'phone_number', 'role')
    list_filter = ('role',)
    ordering = ('name',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'batch', 'course_id')
    search_fields = ('name', 'batch', 'course_id')
    list_filter = ('name',)
    ordering = ('name', 'batch')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_name', 'course')
    search_fields = ('subject_name', 'course__name')
    list_filter = ('course',)
    ordering = ('subject_name',)


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('chapter_name', 'subject')
    search_fields = ('chapter_name', 'subject__subject_name')
    list_filter = ('subject',)
    ordering = ('chapter_name',)


@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ('description', )
    search_fields = ('description', 'chapter__chapter_name')
    list_filter = ('chapter__subject',)
    filter_horizontal = ('chapter',)
    ordering = ('chapter',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'type', 'tag', 'marks_award', 'marks_deduct',)
    search_fields = ('question_text',  'tag','chapter__chapter_name', 'chapter__subject__subject_name')
    list_filter = ('type', 'tag', 'chapter')
    filter_horizontal = ('chapter',)
    ordering = ('chapter',)
    fieldsets = (
        ('Question Details', {
            'fields': ('question_text', 'type', 'chapter', 'tag', 'marks_award', 'marks_deduct', 'visible')
        }),
        ('Options', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d', 'correct_option')
        }),
        ('Numerical Answer', {
            'fields': ('correct_answer_numerical_min', 'correct_answer_numerical_max')
        }),
        ('Files', {
            'fields': ('question_file', 'option_a_file', 'option_b_file', 'option_c_file', 'option_d_file', 'explanation_file')
        }),
        ('Explanation', {
            'fields': ('explanation',)
        }),
    )


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('test_id', 'duration', "test_name")
    search_fields = ('test_id', "test_name")
    filter_horizontal = ('question_list',)
    ordering = ('test_id',)


@admin.register(TestSubmitted)
class TestSubmittedAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'test_id')
    search_fields = ('user_email__name', 'test_id__test_id')
    list_filter = ('test_id',)
    ordering = ('user_email',)

admin.site.site_header = 'LEAP Admin'
admin.site.index_title = 'LEAP Admin'
admin.site.site_title = 'LEAP Admin'
