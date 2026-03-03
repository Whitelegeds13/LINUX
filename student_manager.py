"""
Módulo de gestión de estudiantes, cursos y matrículas.
"""

from database import get_db
from models import get_models
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib


class StudentManager:
    """Clase para gestionar estudiantes, cursos y matrículas."""
    
    def __init__(self):
        """Inicializa el gestor de estudiantes."""
        self.db = get_db()
        self.models = get_models()
    
    def create_student(self, student_id: str, name: str, lastname: str, 
                       email: str, career: str = None, semester: str = None) -> bool:
        """
        Crea un nuevo estudiante en el sistema.
        
        Args:
            student_id: ID único del estudiante
            name: Nombre del estudiante
            lastname: Apellidos del estudiante
            email: Correo electrónico
            career: Carrera profesional
            semester: Semestre actual
            
        Returns:
            True si fue exitoso, False en caso contrario
        """
        # Generar dirección de wallet basada en el student_id
        wallet_address = hashlib.sha256(student_id.encode()).hexdigest()[:64]
        
        query = """
            INSERT INTO students (student_id, name, lastname, email, career, semester, wallet_address)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                name = VALUES(name),
                lastname = VALUES(lastname),
                email = VALUES(email),
                career = VALUES(career),
                semester = VALUES(semester)
        """
        result = self.db.execute_query(query, (student_id, name, lastname, email, career, semester, wallet_address))
        
        if result:
            print(f"✓ Estudiante {name} {lastname} creado/actualizado exitosamente")
        return result is not None
    
    def create_course(self, course_id: str, course_name: str, course_code: str,
                     credits: int = 0, teacher_name: str = None, schedule: str = None) -> bool:
        """
        Crea un nuevo curso en el sistema.
        
        Args:
            course_id: ID único del curso
            course_name: Nombre del curso
            course_code: Código del curso
            credits: Créditos del curso
            teacher_name: Nombre del profesor
            schedule: Horario del curso
            
        Returns:
            True si fue exitoso, False en caso contrario
        """
        query = """
            INSERT INTO courses (course_id, course_name, course_code, credits, teacher_name, schedule)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                course_name = VALUES(course_name),
                course_code = VALUES(course_code),
                credits = VALUES(credits),
                teacher_name = VALUES(teacher_name),
                schedule = VALUES(schedule)
        """
        result = self.db.execute_query(query, (course_id, course_name, course_code, credits, teacher_name, schedule))
        
        if result:
            print(f"✓ Curso {course_name} ({course_code}) creado/actualizado exitosamente")
        return result is not None
    
    def enroll_student(self, student_id: str, course_id: str, 
                      semester: str, academic_year: str) -> bool:
        """
        Matricula a un estudiante en un curso.
        
        Args:
            student_id: ID del estudiante
            course_id: ID del curso
            semester: Semestre (ej: 2024-I)
            academic_year: Año académico
            
        Returns:
            True si fue exitoso, False en caso contrario
        """
        query = """
            INSERT INTO enrollments (student_id, course_id, semester, academic_year)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE semester = VALUES(semester)
        """
        result = self.db.execute_query(query, (student_id, course_id, semester, academic_year))
        
        if result:
            print(f"✓ Estudiante {student_id} matriculado en curso {course_id}")
        return result is not None
    
    def get_student_info(self, student_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de un estudiante.
        
        Args:
            student_id: ID del estudiante
            
        Returns:
            Diccionario con la información del estudiante o None
        """
        query = "SELECT * FROM students WHERE student_id = %s"
        results = self.db.execute_query(query, (student_id,))
        return results[0] if results else None
    
    def get_student_courses(self, student_id: str, semester: str = None) -> List[Dict[str, Any]]:
        """
        Obtiene los cursos de un estudiante.
        
        Args:
            student_id: ID del estudiante
            semester: Semestre específico (opcional)
            
        Returns:
            Lista de cursos del estudiante
        """
        if semester:
            query = """
                SELECT c.*, e.semester, e.academic_year, e.enrolled_at
                FROM enrollments e
                JOIN courses c ON e.course_id = c.course_id
                WHERE e.student_id = %s AND e.semester = %s
                ORDER BY c.course_name
            """
            return self.db.execute_query(query, (student_id, semester)) or []
        else:
            query = """
                SELECT c.*, e.semester, e.academic_year, e.enrolled_at
                FROM enrollments e
                JOIN courses c ON e.course_id = c.course_id
                WHERE e.student_id = %s
                ORDER BY e.semester, c.course_name
            """
            return self.db.execute_query(query, (student_id,)) or []
    
    def get_all_students(self) -> List[Dict[str, Any]]:
        """Obtiene todos los estudiantes."""
        return self.models.get_all_students()
    
    def get_all_courses(self) -> List[Dict[str, Any]]:
        """Obtiene todos los cursos."""
        return self.models.get_all_courses()
    
    def delete_student(self, student_id: str) -> bool:
        """
        Elimina un estudiante del sistema.
        
        Args:
            student_id: ID del estudiante
            
        Returns:
            True si fue exitoso, False en caso contrario
        """
        # Primero eliminar las matrículas
        self.db.execute_query("DELETE FROM enrollments WHERE student_id = %s", (student_id,))
        # Luego eliminar el estudiante
        result = self.db.execute_query("DELETE FROM students WHERE student_id = %s", (student_id,))
        
        if result:
            print(f"✓ Estudiante {student_id} eliminado")
        return result is not None
    
    def delete_course(self, course_id: str) -> bool:
        """
        Elimina un curso del sistema.
        
        Args:
            course_id: ID del curso
            
        Returns:
            True si fue exitoso, False en caso contrario
        """
        # Primero eliminar las matrículas
        self.db.execute_query("DELETE FROM enrollments WHERE course_id = %s", (course_id,))
        # Luego eliminar el curso
        result = self.db.execute_query("DELETE FROM courses WHERE course_id = %s", (course_id,))
        
        if result:
            print(f"✓ Curso {course_id} eliminado")
        return result is not None


# Instancia global del gestor de estudiantes
student_manager = StudentManager()


def get_student_manager() -> StudentManager:
    """Retorna la instancia global del gestor de estudiantes."""
    return student_manager
