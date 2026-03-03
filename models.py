"""
Módulo de modelos de base de datos para el sistema de blockchain URP.
"""

from database import get_db
from typing import List, Dict, Any, Optional
from datetime import datetime


class DatabaseModels:
    """Clase para manejar los modelos/tablas de la base de datos."""
    
    def __init__(self):
        """Inicializa los modelos de base de datos."""
        self.db = get_db()
    
    def create_tables(self) -> bool:
        """
        Crea todas las tablas necesarias en la base de datos.
        
        Returns:
            True si fue exitoso, False en caso contrario
        """
        queries = [
            # Tabla de estudiantes
            """
            CREATE TABLE IF NOT EXISTS students (
                student_id VARCHAR(20) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                lastname VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                career VARCHAR(100),
                semester VARCHAR(20),
                wallet_address VARCHAR(64) UNIQUE,
                total_tokens INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """,
            # Tabla de cursos
            """
            CREATE TABLE IF NOT EXISTS courses (
                course_id VARCHAR(20) PRIMARY KEY,
                course_name VARCHAR(100) NOT NULL,
                course_code VARCHAR(20) UNIQUE NOT NULL,
                credits INT DEFAULT 0,
                teacher_name VARCHAR(100),
                schedule VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            # Tabla de matriculas (estudiante-curso)
            """
            CREATE TABLE IF NOT EXISTS enrollments (
                enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(20) NOT NULL,
                course_id VARCHAR(20) NOT NULL,
                semester VARCHAR(20) NOT NULL,
                academic_year VARCHAR(10) NOT NULL,
                enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (course_id) REFERENCES courses(course_id),
                UNIQUE KEY unique_enrollment (student_id, course_id, semester, academic_year)
            )
            """,
            # Tabla de asistencia diaria
            """
            CREATE TABLE IF NOT EXISTS daily_attendance (
                attendance_id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(20) NOT NULL,
                course_id VARCHAR(20) NOT NULL,
                attendance_date DATE NOT NULL,
                present BOOLEAN DEFAULT FALSE,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (course_id) REFERENCES courses(course_id),
                UNIQUE KEY unique_attendance (student_id, course_id, attendance_date)
            )
            """,
            # Tabla de recompensas de tokens
            """
            CREATE TABLE IF NOT EXISTS token_rewards (
                reward_id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(20) NOT NULL,
                tokens INT NOT NULL,
                reward_date DATE NOT NULL,
                reason VARCHAR(255),
                block_hash VARCHAR(64),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
            """,
            # Tabla de redención de tokens (canje)
            """
            CREATE TABLE IF NOT EXISTS token_redemptions (
                redemption_id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(20) NOT NULL,
                item_name VARCHAR(100) NOT NULL,
                item_cost INT NOT NULL,
                redemption_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
            """,
            # Tabla de catálogo de productos para canje
            """
            CREATE TABLE IF NOT EXISTS redemption_catalog (
                item_id INT AUTO_INCREMENT PRIMARY KEY,
                item_name VARCHAR(100) NOT NULL,
                item_description TEXT,
                item_cost INT NOT NULL,
                item_category VARCHAR(50),
                available BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            # Tabla de bloques de la blockchain
            """
            CREATE TABLE IF NOT EXISTS blockchain_blocks (
                block_index INT PRIMARY KEY,
                block_timestamp TIMESTAMP NOT NULL,
                block_data JSON NOT NULL,
                block_previous_hash VARCHAR(64) NOT NULL,
                block_nonce INT NOT NULL,
                block_hash VARCHAR(64) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]
        
        for query in queries:
            result = self.db.execute_query(query)
            if result is None:
                print(f"✗ Error al crear tabla")
                return False
        
        print("✓ Todas las tablas creadas correctamente")
        return True
    
    def insert_sample_data(self) -> bool:
        """
        Inserta datos de ejemplo para pruebas.
        
        Returns:
            True si fue exitoso, False en caso contrario
        """
        # Insertar cursos de ejemplo
        courses = [
            ("CS101", "Introducción a la Programación", "INF101", 4, "Dr. García", "Lun-Mie 08:00-10:00"),
            ("CS102", "Estructuras de Datos", "INF102", 4, "Dra. López", "Mar-Jue 10:00-12:00"),
            ("CS103", "Base de Datos I", "INF103", 3, "Ing. Martínez", "Lun-Mie 14:00-16:00"),
            ("MA101", "Cálculo I", "MAT101", 4, "Dr. Pérez", "Mar-Jue 08:00-10:00"),
            ("CS104", "Arquitectura de Computadoras", "INF104", 3, "Ing. Rodríguez", "Vie 08:00-12:00")
        ]
        
        for course in courses:
            query = """
                INSERT IGNORE INTO courses (course_id, course_name, course_code, credits, teacher_name, schedule)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            self.db.execute_query(query, course)
        
        # Insertar estudiantes de ejemplo
        students = [
            ("20210001", "Juan", "Pérez García", "juan.perez@urp.edu.pe", "Ing. Sistemas", "2024-I"),
            ("20210002", "María", "López Sánchez", "maria.lopez@urp.edu.pe", "Ing. Sistemas", "2024-I"),
            ("20210003", "Carlos", "Rodríguez Torres", "carlos.rodriguez@urp.edu.pe", "Ing. Sistemas", "2024-I"),
            ("20210004", "Ana", "Fernández Díaz", "ana.fernandez@urp.edu.pe", "Ing. Sistemas", "2024-I"),
            ("20210005", "Luis", "Martínez Castro", "luis.martinez@urp.edu.pe", "Ing. Sistemas", "2024-I")
        ]
        
        for student in students:
            query = """
                INSERT IGNORE INTO students (student_id, name, lastname, email, career, semester)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            self.db.execute_query(query, student)
        
        # Insertar catálogo de productos para canje
        items = [
            ("Almuerzo Gratis - Comedor URP", "Canjea tu almuerzo gratuito en el comedor universitario", 10, "Comida"),
            ("Café + Galletas", "Delicioso café con galletas", 5, "Bebida"),
            ("Libro de Texto", "Cupón para libro de texto", 30, "Material"),
            ("Impresiones B/N", "50 hojas impresas", 3, "Servicio"),
            ("Impresiones a Color", "20 hojas a color", 8, "Servicio"),
            ("Material de Oficina", "Cuaderno, lapiceros, folder", 15, "Material"),
            ("Bebida Energética", "Bebida energética del mercado", 7, "Bebida"),
            ("Snacks", "Paquete de snacks", 4, "Comida")
        ]
        
        for item in items:
            query = """
                INSERT IGNORE INTO redemption_catalog (item_name, item_description, item_cost, item_category)
                VALUES (%s, %s, %s, %s)
            """
            self.db.execute_query(query, item)
        
        print("✓ Datos de ejemplo insertados correctamente")
        return True
    
    def get_all_students(self) -> List[Dict[str, Any]]:
        """Obtiene todos los estudiantes."""
        query = "SELECT * FROM students ORDER BY student_id"
        return self.db.execute_query(query) or []
    
    def get_all_courses(self) -> List[Dict[str, Any]]:
        """Obtiene todos los cursos."""
        query = "SELECT * FROM courses ORDER BY course_id"
        return self.db.execute_query(query) or []
    
    def get_student_enrollments(self, student_id: str) -> List[Dict[str, Any]]:
        """Obtiene las matriculas de un estudiante."""
        query = """
            SELECT e.*, c.course_name, c.course_code, c.teacher_name, c.schedule
            FROM enrollments e
            JOIN courses c ON e.course_id = c.course_id
            WHERE e.student_id = %s
            ORDER BY e.semester
        """
        return self.db.execute_query(query, (student_id,)) or []
    
    def get_redemption_catalog(self) -> List[Dict[str, Any]]:
        """Obtiene el catálogo de productos para canje."""
        query = "SELECT * FROM redemption_catalog WHERE available = TRUE ORDER BY item_cost"
        return self.db.execute_query(query) or []
    
    def update_student_tokens(self, student_id: str, tokens: int, operation: str = "add") -> bool:
        """
        Actualiza los tokens de un estudiante.
        
        Args:
            student_id: ID del estudiante
            tokens: Cantidad de tokens
            operation: 'add' o 'subtract'
            
        Returns:
            True si fue exitoso, False en caso contrario
        """
        if operation == "add":
            query = "UPDATE students SET total_tokens = total_tokens + %s WHERE student_id = %s"
        else:
            query = "UPDATE students SET total_tokens = total_tokens - %s WHERE student_id = %s"
        
        result = self.db.execute_query(query, (tokens, student_id))
        return result is not None
    
    def save_block_to_db(self, block_data: Dict[str, Any]) -> bool:
        """
        Guarda un bloque en la base de datos.
        
        Args:
            block_data: Datos del bloque
            
        Returns:
            True si fue exitoso, False en caso contrario
        """
        import json
        query = """
            INSERT INTO blockchain_blocks 
            (block_index, block_timestamp, block_data, block_previous_hash, block_nonce, block_hash)
            VALUES (%s, FROM_UNIXTIME(%s), %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                block_data = VALUES(block_data),
                block_nonce = VALUES(block_nonce),
                block_hash = VALUES(block_hash)
        """
        params = (
            block_data["index"],
            block_data["timestamp"],
            json.dumps(block_data["data"]),
            block_data["previous_hash"],
            block_data["nonce"],
            block_data["hash"]
        )
        result = self.db.execute_query(query, params)
        return result is not None


# Instancia global de modelos
models = DatabaseModels()


def get_models() -> DatabaseModels:
    """Retorna la instancia global de modelos."""
    return models
