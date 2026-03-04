"""
URLs de la aplicacion core.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('students/', views.students, name='students'),
    path('courses/', views.courses, name='courses'),
    path('add-student/', views.add_student, name='add_student'),
    path('add-course/', views.add_course, name='add_course'),
    path('enroll-student/', views.enroll_student, name='enroll_student'),
    path('attendance/', views.attendance, name='attendance'),
    path('record-attendance/', views.record_attendance, name='record_attendance'),
    path('process-attendance/', views.process_daily_attendance, name='process_attendance'),
    path('token-balance/<str:student_id>/', views.token_balance, name='token_balance'),
    path('catalog/', views.catalog, name='catalog'),
    path('redeem-tokens/', views.redeem_tokens, name='redeem_tokens'),
    path('token-rewards/', views.token_rewards, name='token_rewards'),
    path('blockchain/', views.blockchain_view, name='blockchain_view'),
    path('validate-blockchain/', views.validate_blockchain, name='validate_blockchain'),
    path('init-database/', views.init_database, name='init_database'),
]
