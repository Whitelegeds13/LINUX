"""
Modulo de gestion de asistencia y recompensas de tokens para la URP.
"""

from database import get_db
from models import get_models
from blockchain import get_blockchain
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
import uuid


class AttendanceSystem:
    """Sistema de gestion de asistencia y recompensas de tokens."""
    
    TOKENS_PER_DAY = 1  # Token por dia si asiste a todos los cursos
    
    def __init__(self):
        """Inicializa el sistema de asistencia."""
        self.db = get_db()
        self.models = get_models()
        self.blockchain = get_blockchain()
    
    def record_attendance(self, student_id: str, course_id: str, 
                        attendance_date: date = None, present: bool = True) -> bool:
        """
        Registra la asistencia de un estudiante a un curso.
        
        Args:
            student_id: ID del estudiante
            course_id: ID del curso
            attendance_date: Fecha de asistencia (default: hoy)
            present: Si esta presente o no
            
        Returns:
            True si fue exitoso, False en caso contrario
        """
        if attendance_date is None:
            attendance_date = date.today()
        
        query = """
            INSERT INTO daily_attendance (student_id, course_id, attendance_date, present)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE present = VALUES(present)
        """
        result = self.db.execute_query(query, (student_id, course_id, attendance_date, present))
        
        if result:
            print(f"[OK] Asistencia registrada: {student_id} - {course_id} - {attendance_date}")
        return result is not None
    
    def check_daily_attendance(self, attendance_date: date = None) -> Dict[str, Any]:
        """
        Verifica la asistencia del dia para todos los estudiantes matriculados
        y otorga tokens a quienes asistieron a todos sus cursos.
        
        Utiliza una consulta optimizada con JOIN para evitar el problema N+1.
        
        Args:
            attendance_date: Fecha a verificar (default: hoy)
            
        Returns:
            Diccionario con el resultado del analisis
        """
        if attendance_date is None:
            attendance_date = date.today()
        
        # Obtener estudiantes con asistencia perfecta usando consulta optimizada
        students_with_reward = self._get_students_with_perfect_attendance(attendance_date)
        
        rewards_given = []
        
        # Otorgar tokens a los estudiantes con asistencia perfecta
        for student in students_with_reward:
            student_id = student["student_id"]
            
            # Otorgar token
            success = self._reward_student(student_id, attendance_date)
            if success:
                rewards_given.append({
                    "student_id": student_id,
                    "name": f"{student['name']} {student['lastname']}",
                    "tokens": self.TOKENS_PER_DAY
                })
        
        return {
            "date": attendance_date.isoformat(),
            "total_students": len(students_with_reward),
            "rewards_given": len(rewards_given),
            "students_with_rewards": rewards_given,
            "students_without_courses": 0
        }
    
    def _get_students_with_perfect_attendance(self, attendance_date: date) -> List[Dict[str, Any]]:
        """
        Obtiene estudiantes que asistieron a TODOS sus cursos en una fecha especifica.
        Utiliza una consulta optimizada con subconsultas para evitar el problema N+1.
        
        Args:
            attendance_date: Fecha a verificar
            
        Returns:
            Lista de estudiantes con asistencia perfecta
        """
        # Consulta optimizada: obtener estudiantes donde la cantidad de cursos
        # con asistencia es igual a la cantidad de cursos matriculados
        query = """
            SELECT s.student_id, s.name, s.lastname, s.email, s.total_tokens
            FROM students s
            WHERE (
                -- Cantidad de cursos donde asistio
                SELECT COUNT(DISTINCT da.course_id)
                FROM daily_attendance da
                WHERE da.student_id = s.student_id 
                AND da.attendance_date = %s 
                AND da.present = TRUE
            ) = (
                -- Cantidad de cursos matriculados
                SELECT COUNT(DISTINCT e.course_id)
                FROM enrollments e
                WHERE e.student_id = s.student_id
            )
            AND (
                -- Debe tener al menos un curso con asistencia registrada
                SELECT COUNT(DISTINCT da2.course_id)
                FROM daily_attendance da2
                WHERE da2.student_id = s.student_id
                AND da2.attendance_date = %s
                AND da2.present = TRUE
            ) > 0
        """
        return self.db.execute_query(query, (attendance_date, attendance_date)) or []
    
    def _get_student_courses_for_date(self, student_id: str, attendance_date: date) -> List[Dict[str, Any]]:
        """Obtiene los cursos de un estudiante para una fecha especifica."""
        query = """
            SELECT c.* 
            FROM enrollments e
            JOIN courses c ON e.course_id = c.course_id
            WHERE e.student_id = %s
        """
        return self.db.execute_query(query, (student_id,)) or []
    
    def _check_all_courses_attendance(self, student_id: str, courses: List[Dict], 
                                      attendance_date: date) -> bool:
        """Verifica si el estudiante asistio a todos sus cursos."""
        for course in courses:
            query = """
                SELECT present FROM daily_attendance 
                WHERE student_id = %s AND course_id = %s AND attendance_date = %s
            """
            results = self.db.execute_query(query, (student_id, course["course_id"], attendance_date))
            
            if not results or not results[0]["present"]:
                return False
        
        return True
    
    def _reward_student(self, student_id: str, reward_date: date) -> bool:
        """
        Otorga tokens a un estudiante y registra en la blockchain.
        
        Args:
            student_id: ID del estudiante
            reward_date: Fecha de la recompensa
            
        Returns:
            True si fue exitoso, False en caso contrario
        """
        # Generar un ID unico para el token (no se puede copiar)
        unique_token_id = str(uuid.uuid4())
        
        # Crear bloque en la blockchain con token unico
        block_data = {
            "type": "token_reward",
            "token_id": unique_token_id,  # ID unico del token
            "student_id": student_id,
            "tokens": self.TOKENS_PER_DAY,
            "reward_date": reward_date.isoformat(),
            "description": f"Token unico otorgado por asistir a todos los cursos el {reward_date}"
        }
        
        new_block = self.blockchain.add_block(block_data)
        
        # Guardar en la base de datos con el token unico
        self.db.execute_query("""
            INSERT INTO token_rewards (token_id, student_id, tokens, reward_date, reason, block_hash)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (unique_token_id, student_id, self.TOKENS_PER_DAY, reward_date, 
              f"Token unico {unique_token_id}", new_block.hash))
        
        # Actualizar total de tokens del estudiante
        self.models.update_student_tokens(student_id, self.TOKENS_PER_DAY, "add")
        
        print(f"[OK] Token unico {unique_token_id} otorgado a {student_id}")
        return True
    
    def get_student_attendance_history(self, student_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de asistencia de un estudiante.
        
        Args:
            student_id: ID del estudiante
            
        Returns:
            Lista de registros de asistencia
        """
        query = """
            SELECT a.*, c.course_name, c.course_code
            FROM daily_attendance a
            JOIN courses c ON a.course_id = c.course_id
            WHERE a.student_id = %s
            ORDER BY a.attendance_date DESC, c.course_name
        """
        return self.db.execute_query(query, (student_id,)) or []
    
    def get_student_token_balance(self, student_id: str) -> int:
        """
        Obtiene el balance de tokens de un estudiante.
        
        Args:
            student_id: ID del estudiante
            
        Returns:
            Cantidad de tokens del estudiante
        """
        query = "SELECT total_tokens FROM students WHERE student_id = %s"
        results = self.db.execute_query(query, (student_id,))
        return results[0]["total_tokens"] if results else 0
    
    def get_student_token_history(self, student_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de tokens de un estudiante.
        
        Args:
            student_id: ID del estudiante
            
        Returns:
            Lista de transacciones de tokens
        """
        # Rewards
        rewards = self.db.execute_query("""
            SELECT reward_id as id, tokens as amount, reward_date as date, 
                   reason as description, 'reward' as type
            FROM token_rewards
            WHERE student_id = %s
            ORDER BY reward_date DESC
        """, (student_id,)) or []
        
        # Redemptions
        redemptions = self.db.execute_query("""
            SELECT redemption_id as id, item_name as item, item_cost as amount,
                   redemption_date as date, description, 'redemption' as type
            FROM token_redemptions
            WHERE student_id = %s
            ORDER BY redemption_date DESC
        """, (student_id,)) or []
        
        # Combinar y ordenar
        all_transactions = rewards + redemptions
        all_transactions.sort(key=lambda x: x["date"], reverse=True)
        
        return all_transactions
    
    def redeem_tokens(self, student_id: str, item_id: int) -> Dict[str, Any]:
        """
        Canjea tokens por un producto del catalogo.
        
        Args:
            student_id: ID del estudiante
            item_id: ID del producto a canjear
            
        Returns:
            Diccionario con el resultado del canje
        """
        # Obtener informacion del producto
        items = self.db.execute_query("""
            SELECT * FROM redemption_catalog WHERE item_id = %s AND available = TRUE
        """, (item_id,))
        
        if not items:
            return {"success": False, "message": "Producto no disponible"}
        
        item = items[0]
        item_cost = item["item_cost"]
        
        # Verificar balance del estudiante
        current_balance = self.get_student_token_balance(student_id)
        
        if current_balance < item_cost:
            return {
                "success": False, 
                "message": f"Tokens insuficientes. Balance: {current_balance}, Costo: {item_cost}"
            }
        
        # Realizar el canje
        # 1. Crear bloque en la blockchain
        block_data = {
            "type": "token_redemption",
            "student_id": student_id,
            "item": item["item_name"],
            "cost": item_cost,
            "description": f"Canje de tokens por {item['item_name']}"
        }
        
        new_block = self.blockchain.add_block(block_data)
        
        # 2. Registrar en la base de datos
        self.db.execute_query("""
            INSERT INTO token_redemptions (student_id, item_name, item_cost)
            VALUES (%s, %s, %s)
        """, (student_id, item["item_name"], item_cost))
        
        # 3. Actualizar balance
        self.models.update_student_tokens(student_id, item_cost, "subtract")
        
        return {
            "success": True,
            "message": f"Canje exitoso: {item['item_name']}",
            "item": item["item_name"],
            "cost": item_cost,
            "remaining_balance": current_balance - item_cost,
            "block_hash": new_block.hash
        }
    
    def get_redemption_catalog(self) -> List[Dict[str, Any]]:
        """Obtiene el catalogo de productos para canje."""
        return self.models.get_redemption_catalog()
    
    def get_blockchain_for_student(self, student_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene los bloques de la blockchain relacionados con un estudiante.
        
        Args:
            student_id: ID del estudiante
            
        Returns:
            Lista de bloques relacionados
        """
        return self.blockchain.find_token_transactions(student_id)


# Instancia global del sistema de asistencia
attendance_system = AttendanceSystem()


def get_attendance_system() -> AttendanceSystem:
    """Retorna la instancia global del sistema de asistencia."""
    return attendance_system
