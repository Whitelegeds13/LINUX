"""
Vistas de Django para el sistema de Blockchain URP.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Q, F
from datetime import date, datetime
import uuid
import json

from .models import Student, Course, Enrollment, DailyAttendance, TokenReward, TokenRedemption, RedemptionCatalog, BlockchainBlock
from .blockchain import get_blockchain


def index(request):
    """Pagina principal."""
    context = {
        'total_students': Student.objects.count(),
        'total_courses': Course.objects.count(),
        'total_rewards': TokenReward.objects.count(),
    }
    return render(request, 'core/index.html', context)


def students(request):
    """Lista de estudiantes."""
    students = Student.objects.all()
    return render(request, 'core/students.html', {'students': students})


def courses(request):
    """Lista de cursos."""
    courses = Course.objects.all()
    return render(request, 'core/courses.html', {'courses': courses})


def add_student(request):
    """Agregar estudiante."""
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        name = request.POST.get('name')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        career = request.POST.get('career', '')
        semester = request.POST.get('semester', '')
        
        if Student.objects.filter(student_id=student_id).exists():
            messages.error(request, 'El estudiante ya existe')
        else:
            Student.objects.create(
                student_id=student_id,
                name=name,
                lastname=lastname,
                email=email,
                career=career,
                semester=semester
            )
            messages.success(request, 'Estudiante agregado correctamente')
        
        return redirect('students')
    
    return render(request, 'core/add_student.html')


def add_course(request):
    """Agregar curso."""
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        course_name = request.POST.get('course_name')
        course_code = request.POST.get('course_code')
        credits = request.POST.get('credits', 0)
        teacher_name = request.POST.get('teacher_name', '')
        schedule = request.POST.get('schedule', '')
        
        if Course.objects.filter(course_id=course_id).exists():
            messages.error(request, 'El curso ya existe')
        else:
            Course.objects.create(
                course_id=course_id,
                course_name=course_name,
                course_code=course_code,
                credits=credits,
                teacher_name=teacher_name,
                schedule=schedule
            )
            messages.success(request, 'Curso agregado correctamente')
        
        return redirect('courses')
    
    return render(request, 'core/add_course.html')


def enroll_student(request):
    """Matricular estudiante en curso."""
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        course_id = request.POST.get('course_id')
        semester = request.POST.get('semester')
        academic_year = request.POST.get('academic_year')
        
        try:
            student = Student.objects.get(student_id=student_id)
            course = Course.objects.get(course_id=course_id)
            
            Enrollment.objects.get_or_create(
                student=student,
                course=course,
                semester=semester,
                academic_year=academic_year
            )
            messages.success(request, 'Matricula realizada correctamente')
        except Student.DoesNotExist:
            messages.error(request, 'Estudiante no encontrado')
        except Course.DoesNotExist:
            messages.error(request, 'Curso no encontrado')
        
        return redirect('courses')
    
    students = Student.objects.all()
    courses = Course.objects.all()
    return render(request, 'core/enroll_student.html', {
        'students': students,
        'courses': courses
    })


def record_attendance(request):
    """Registrar asistencia."""
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        course_id = request.POST.get('course_id')
        attendance_date = request.POST.get('attendance_date')
        present = request.POST.get('present') == 'on'
        
        try:
            student = Student.objects.get(student_id=student_id)
            course = Course.objects.get(course_id=course_id)
            
            DailyAttendance.objects.update_or_create(
                student=student,
                course=course,
                attendance_date=attendance_date,
                defaults={'present': present}
            )
            messages.success(request, 'Asistencia registrada correctamente')
        except Student.DoesNotExist:
            messages.error(request, 'Estudiante no encontrado')
        except Course.DoesNotExist:
            messages.error(request, 'Curso no encontrado')
        
        return redirect('attendance')
    
    students = Student.objects.all()
    courses = Course.objects.all()
    return render(request, 'core/record_attendance.html', {
        'students': students,
        'courses': courses
    })


def attendance(request):
    """Lista de asistencia."""
    attendances = DailyAttendance.objects.select_related('student', 'course').order_by('-attendance_date')[:50]
    return render(request, 'core/attendance.html', {'attendances': attendances})


def process_daily_attendance(request):
    """Procesar asistencia diaria y otorgar tokens automaticamente."""
    if request.method == 'POST':
        attendance_date_str = request.POST.get('attendance_date')
        
        if not attendance_date_str:
            attendance_date = date.today()
        else:
            attendance_date = datetime.strptime(attendance_date_str, '%Y-%m-%d').date()
        
        # Obtener estudiantes con asistencia perfecta
        students_with_reward = get_students_with_perfect_attendance(attendance_date)
        
        # Excluir estudiantes que ya recibieron tokens para esta fecha
        already_rewarded_ids = TokenReward.objects.filter(
            reward_date=attendance_date
        ).values_list('student_id', flat=True)
        
        students_to_reward = [s for s in students_with_reward if s.student_id not in already_rewarded_ids]
        
        blockchain = get_blockchain()
        rewards_given = 0
        
        for student in students_to_reward:
            # Generar token unico
            unique_token_id = str(uuid.uuid4())
            
            # Generar barcode unico
            date_str = datetime.now().strftime('%Y%m%d')
            unique_barcode_part = str(uuid.uuid4())[:8].upper()
            unique_barcode = f"TOK-{date_str}-{unique_barcode_part}"
            
            # Crear bloque en blockchain
            block_data = {
                "type": "token_reward",
                "token_id": unique_token_id,
                "barcode": unique_barcode,
                "student_id": student.student_id,
                "student_name": f"{student.name} {student.lastname}",
                "tokens": 1,
                "reward_date": attendance_date.isoformat(),
                "description": f"Token unico con barcode {unique_barcode} otorgado por asistir a todos los cursos el {attendance_date}"
            }
            
            # Usar transaccion atomica para consistencia de datos
            with transaction.atomic():
                new_block = blockchain.add_block(block_data)
                
                # Guardar en base de datos
                TokenReward.objects.create(
                    token_id=unique_token_id,
                    student=student,
                    tokens=1,
                    reward_date=attendance_date,
                    reason=f"Token unico {unique_barcode}",
                    block_hash=new_block.hash,
                    barcode=unique_barcode,
                    barcode_generated=True
                )
                
                # Actualizar balance
                student.total_tokens += 1
                student.save()
            
            rewards_given += 1
        
        messages.success(request, f'Se otorgaron {rewards_given} tokens automaticamente con codigos de barras unicos')
        return redirect('token_rewards')
    
    return render(request, 'core/process_attendance.html')


def get_students_with_perfect_attendance(attendance_date):
    """
    Obtiene estudiantes que asistieron a todos sus cursos en una fecha especifica.
    Optimizado con una sola consulta usando anotaciones.
    """
    # Obtener estudiantes que tienen cursos matriculados Y asistieron a TODOS sus cursos
    # Usamos subconsultas para evitar el problema N+1
    
    # Subconsulta: cursos matriculados por estudiante
    from django.db.models import OuterRef, Subquery, Value
    from django.db.models.functions import Coalesce
    
    # Obtener estudiantes con sus conteos de cursos matriculados y asistencia perfecta
    students = Student.objects.annotate(
        enrolled_courses_count=Count(
            'enrollments',
            filter=Q(enrollments__semester__isnull=False)
        ),
        present_courses_count=Count(
            'dailyattendance',
            filter=Q(
                dailyattendance__attendance_date=attendance_date,
                dailyattendance__present=True,
                dailyattendance__course_id__in=Subquery(
                    Enrollment.objects.filter(
                        student=OuterRef('pk')
                    ).values('course_id')
                )
            )
        )
    ).filter(
        enrolled_courses_count__gt=0,
        enrolled_courses_count=F('present_courses_count')
    )
    
    return list(students)


def token_balance(request, student_id):
    """Ver balance de tokens de un estudiante."""
    student = get_object_or_404(Student, student_id=student_id)
    rewards = TokenReward.objects.filter(student=student)
    redemptions = TokenRedemption.objects.filter(student=student)
    
    return render(request, 'core/token_balance.html', {
        'student': student,
        'rewards': rewards,
        'redemptions': redemptions
    })


def catalog(request):
    """Catalogo de productos para canje."""
    items = RedemptionCatalog.objects.filter(available=True)
    return render(request, 'core/catalog.html', {'items': items})


def redeem_tokens(request):
    """Canje de tokens con codigo de barras unico."""
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        item_id = request.POST.get('item_id')
        
        try:
            student = Student.objects.get(student_id=student_id)
            item = RedemptionCatalog.objects.get(id=item_id, available=True)
            
            if student.total_tokens < item.item_cost:
                messages.error(request, 'Tokens insuficientes')
                return redirect('redeem_tokens')
            
            # Generar barcode unico para el canje
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            unique_barcode_part = str(uuid.uuid4())[:8].upper()
            unique_barcode = f"RED-{date_str}-{unique_barcode_part}"
            
            # Crear bloque en blockchain
            blockchain = get_blockchain()
            block_data = {
                "type": "token_redemption",
                "redemption_barcode": unique_barcode,
                "student_id": student_id,
                "student_name": f"{student.name} {student.lastname}",
                "item": item.item_name,
                "item_cost": item.item_cost,
                "description": f"Canje de tokens por {item.item_name} - Codigo: {unique_barcode}"
            }
            
            # Usar transaccion atomica para consistencia de datos
            with transaction.atomic():
                new_block = blockchain.add_block(block_data)
                
                # Registrar canje con barcode
                TokenRedemption.objects.create(
                    student=student,
                    item_name=item.item_name,
                    item_cost=item.item_cost,
                    barcode=unique_barcode
                )
                
                # Actualizar balance
                student.total_tokens -= item.item_cost
                student.save()
            
            messages.success(request, f'Canje exitoso: {item.item_name} - Codigo de barras: {unique_barcode}')
            return redirect('catalog')
            
        except Student.DoesNotExist:
            messages.error(request, 'Estudiante no encontrado')
        except RedemptionCatalog.DoesNotExist:
            messages.error(request, 'Producto no disponible')
    
    students = Student.objects.all()
    items = RedemptionCatalog.objects.filter(available=True)
    return render(request, 'core/redeem_tokens.html', {
        'students': students,
        'items': items
    })


def token_rewards(request):
    """Lista de recompensas de tokens."""
    rewards = TokenReward.objects.select_related('student').order_by('-reward_date')
    return render(request, 'core/token_rewards.html', {'rewards': rewards})


def blockchain_view(request):
    """Ver blockchain."""
    blockchain = get_blockchain()
    chain = blockchain.to_list()
    return render(request, 'core/blockchain.html', {'chain': chain})


def validate_blockchain(request):
    """Validar blockchain."""
    blockchain = get_blockchain()
    is_valid = blockchain.is_chain_valid()
    
    if is_valid:
        messages.success(request, 'La blockchain es valida')
    else:
        messages.error(request, 'La blockchain ha sido alterada - ES INVALIDA')
    
    return redirect('blockchain_view')


def init_database(request):
    """Inicializar base de datos con datos de ejemplo."""
    # Crear cursos de ejemplo
    courses_data = [
        ("CS101", "Introduccion a la Programacion", "INF101", 4, "Dr. Garcia", "Lun-Mie 08:00-10:00"),
        ("CS102", "Estructuras de Datos", "INF102", 4, "Dra. Lopez", "Mar-Jue 10:00-12:00"),
        ("CS103", "Base de Datos I", "INF103", 3, "Ing. Martinez", "Lun-Mie 14:00-16:00"),
        ("MA101", "Calculo I", "MAT101", 4, "Dr. Perez", "Mar-Jue 08:00-10:00"),
        ("CS104", "Arquitectura de Computadoras", "INF104", 3, "Ing. Rodriguez", "Vie 08:00-12:00")
    ]
    
    for course in courses_data:
        Course.objects.get_or_create(
            course_id=course[0],
            defaults={
                'course_name': course[1],
                'course_code': course[2],
                'credits': course[3],
                'teacher_name': course[4],
                'schedule': course[5]
            }
        )
    
    # Crear estudiantes de ejemplo
    students_data = [
        ("20210001", "Juan", "Perez Garcia", "juan.perez@urp.edu.pe", "Ing. Sistemas", "2024-I"),
        ("20210002", "Maria", "Lopez Sanchez", "maria.lopez@urp.edu.pe", "Ing. Sistemas", "2024-I"),
        ("20210003", "Carlos", "Rodriguez Torres", "carlos.rodriguez@urp.edu.pe", "Ing. Sistemas", "2024-I"),
        ("20210004", "Ana", "Fernandez Diaz", "ana.fernandez@urp.edu.pe", "Ing. Sistemas", "2024-I"),
        ("20210005", "Luis", "Martinez Castro", "luis.martinez@urp.edu.pe", "Ing. Sistemas", "2024-I")
    ]
    
    for student in students_data:
        Student.objects.get_or_create(
            student_id=student[0],
            defaults={
                'name': student[1],
                'lastname': student[2],
                'email': student[3],
                'career': student[4],
                'semester': student[5]
            }
        )
    
    # Crear catalogo de productos
    catalog_data = [
        ("Almuerzo Gratis - Comedor URP", "Canjea tu almuerzo gratuito en el comedor universitario", 10, "Comida"),
        ("Cafe + Galletas", "Delicioso cafe con galletas", 5, "Bebida"),
        ("Libro de Texto", "Cupon para libro de texto", 30, "Material"),
        ("Impresiones B/N", "50 hojas impresas", 3, "Servicio"),
        ("Impresiones a Color", "20 hojas a color", 8, "Servicio"),
        ("Material de Oficina", "Cuaderno, lapiceros, folder", 15, "Material"),
        ("Bebida Energetica", "Bebida energetica del mercado", 7, "Bebida"),
        ("Snacks", "Paquete de snacks", 4, "Comida")
    ]
    
    for item in catalog_data:
        RedemptionCatalog.objects.get_or_create(
            item_name=item[0],
            defaults={
                'item_description': item[1],
                'item_cost': item[2],
                'item_category': item[3],
                'available': True
            }
        )
    
    messages.success(request, 'Base de datos inicializada con datos de ejemplo')
    return redirect('index')
