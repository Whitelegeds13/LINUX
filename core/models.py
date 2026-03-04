"""
Modelos de Django para el sistema de Blockchain URP.
"""

from django.db import models
import uuid
import hashlib


class Student(models.Model):
    """Modelo de estudiante."""
    student_id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    career = models.CharField(max_length=100, blank=True, null=True)
    semester = models.CharField(max_length=20, blank=True, null=True)
    wallet_address = models.CharField(max_length=64, unique=True, blank=True, null=True)
    total_tokens = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.wallet_address:
            self.wallet_address = hashlib.sha256(
                self.student_id.encode()
            ).hexdigest()[:64]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.lastname} ({self.student_id})"

    class Meta:
        db_table = 'students'
        ordering = ['student_id']


class Course(models.Model):
    """Modelo de curso."""
    course_id = models.CharField(max_length=20, primary_key=True)
    course_name = models.CharField(max_length=100)
    course_code = models.CharField(max_length=20, unique=True)
    credits = models.IntegerField(default=0)
    teacher_name = models.CharField(max_length=100, blank=True, null=True)
    schedule = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course_name} ({self.course_code})"

    class Meta:
        db_table = 'courses'
        ordering = ['course_id']


class Enrollment(models.Model):
    """Modelo de matricula."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    semester = models.CharField(max_length=20)
    academic_year = models.CharField(max_length=10)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.course}"

    class Meta:
        db_table = 'enrollments'
        unique_together = ['student', 'course', 'semester', 'academic_year']


class DailyAttendance(models.Model):
    """Modelo de asistencia diaria."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendances')
    attendance_date = models.DateField()
    present = models.BooleanField(default=False)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.course} - {self.attendance_date}"

    class Meta:
        db_table = 'daily_attendance'
        unique_together = ['student', 'course', 'attendance_date']


class TokenReward(models.Model):
    """Modelo de recompensa de token (token unico)."""
    token_id = models.CharField(max_length=36, unique=True, default=uuid.uuid4)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='token_rewards')
    tokens = models.IntegerField(default=1)
    reward_date = models.DateField()
    reason = models.CharField(max_length=255, blank=True, null=True)
    block_hash = models.CharField(max_length=64, blank=True, null=True)
    # Codigo de barras unico para el token
    barcode = models.CharField(max_length=50, unique=True, blank=True, null=True)
    barcode_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.barcode:
            # Generar barcode unico: TOKEN-{YYYYMMDD}-{UUID_SHORT}
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            unique_part = str(uuid.uuid4())[:8].upper()
            self.barcode = f"TOK-{date_str}-{unique_part}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Token {self.token_id} - {self.student}"

    class Meta:
        db_table = 'token_rewards'
        ordering = ['-reward_date']


class TokenRedemption(models.Model):
    """Modelo de canje de tokens."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='token_redemptions')
    item_name = models.CharField(max_length=100)
    item_cost = models.IntegerField()
    # Codigo de barras unico para el canje
    barcode = models.CharField(max_length=50, unique=True, blank=True, null=True)
    redemption_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.barcode:
            # Generar barcode unico: RED-{YYYYMMDD}-{UUID_SHORT}
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            unique_part = str(uuid.uuid4())[:8].upper()
            self.barcode = f"RED-{date_str}-{unique_part}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.item_name}"

    class Meta:
        db_table = 'token_redemptions'
        ordering = ['-redemption_date']


class RedemptionCatalog(models.Model):
    """Modelo de catalogo de productos para canje."""
    item_name = models.CharField(max_length=100)
    item_description = models.TextField(blank=True, null=True)
    item_cost = models.IntegerField()
    item_category = models.CharField(max_length=50, blank=True, null=True)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item_name} ({self.item_cost} tokens)"

    class Meta:
        db_table = 'redemption_catalog'
        ordering = ['item_cost']


class BlockchainBlock(models.Model):
    """Modelo de bloque de blockchain."""
    block_index = models.IntegerField(primary_key=True)
    block_timestamp = models.DateTimeField()
    block_data = models.JSONField()
    block_previous_hash = models.CharField(max_length=64)
    block_nonce = models.IntegerField()
    block_hash = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bloque #{self.block_index}"

    class Meta:
        db_table = 'blockchain_blocks'
        ordering = ['-block_index']
