"""
Interfaz de línea de comandos (CLI) para el sistema de blockchain URP.
"""

import sys
from typing import Optional
from database import get_db
from models import get_models
from blockchain import get_blockchain
from student_manager import get_student_manager
from attendance import get_attendance_system
from datetime import datetime, date


class URPCLI:
    """Interfaz de línea de comandos para el sistema URP."""
    
    def __init__(self):
        """Inicializa la CLI."""
        self.db = get_db()
        self.models = get_models()
        self.blockchain = get_blockchain()
        self.student_manager = get_student_manager()
        self.attendance_system = get_attendance_system()
    
    def print_header(self, text: str):
        """Imprime un encabezado decorado."""
        print("\n" + "=" * 60)
        print(f"  {text}")
        print("=" * 60)
    
    def print_menu(self):
        """Muestra el menú principal."""
        self.print_header("BLOCKCHAIN URP - Sistema de Tokens por Asistencia")
        print("""
Opciones:
  1.  Inicializar Base de Datos
  2.  Ver Estudiantes
  3.  Ver Cursos
  4.  Agregar Estudiante
  5.  Agregar Curso
  6.  Matricular Estudiante en Curso
  7.  Registrar Asistencia
  8.  Procesar Asistencia Diaria (Otorgar Tokens)
  9.  Ver Balance de Tokens de Estudiante
  10. Ver Catálogo de Canje
  11. Canjear Tokens por Producto
  12. Ver Historial de Tokens de Estudiante
  13. Ver Blockchain
  14. Validar Blockchain
  0.  Salir
        """)
    
    def run(self):
        """Ejecuta el menú principal."""
        while True:
            self.print_menu()
            choice = input("\nSeleccione una opción: ").strip()
            
            if choice == "0":
                print("\n¡Hasta luego!")
                break
            elif choice == "1":
                self.initialize_database()
            elif choice == "2":
                self.show_students()
            elif choice == "3":
                self.show_courses()
            elif choice == "4":
                self.add_student()
            elif choice == "5":
                self.add_course()
            elif choice == "6":
                self.enroll_student()
            elif choice == "7":
                self.record_attendance()
            elif choice == "8":
                self.process_daily_attendance()
            elif choice == "9":
                self.show_token_balance()
            elif choice == "10":
                self.show_redemption_catalog()
            elif choice == "11":
                self.redeem_tokens()
            elif choice == "12":
                self.show_token_history()
            elif choice == "13":
                self.show_blockchain()
            elif choice == "14":
                self.validate_blockchain()
            else:
                print("\n✗ Opción inválida")
    
    def initialize_database(self):
        """Inicializa la base de datos."""
        self.print_header("Inicializar Base de Datos")
        
        if self.db.connect():
            if self.models.create_tables():
                self.models.insert_sample_data()
                print("\n✓ Base de datos inicializada correctamente")
            else:
                print("\n✗ Error al crear las tablas")
        else:
            print("\n✗ No se pudo conectar a la base de datos")
    
    def show_students(self):
        """Muestra todos los estudiantes."""
        self.print_header("Lista de Estudiantes")
        
        students = self.student_manager.get_all_students()
        
        if not students:
            print("\nNo hay estudiantes registrados")
            return
        
        print(f"\nTotal: {len(students)} estudiantes\n")
        print(f"{'ID':<12} {'Nombre':<25} {'Email':<30} {'Tokens':<8}")
        print("-" * 80)
        
        for s in students:
            print(f"{s['student_id']:<12} {s['name']} {s['lastname']:<15} {s['email']:<30} {s['total_tokens']:<8}")
    
    def show_courses(self):
        """Muestra todos los cursos."""
        self.print_header("Lista de Cursos")
        
        courses = self.student_manager.get_all_courses()
        
        if not courses:
            print("\nNo hay cursos registrados")
            return
        
        print(f"\nTotal: {len(courses)} cursos\n")
        print(f"{'ID':<10} {'Código':<10} {'Nombre':<30} {'Créditos':<10} {'Profesor':<20}")
        print("-" * 90)
        
        for c in courses:
            print(f"{c['course_id']:<10} {c['course_code']:<10} {c['course_name']:<30} {c['credits']:<10} {c['teacher_name'] or '-':<20}")
    
    def add_student(self):
        """Agrega un nuevo estudiante."""
        self.print_header("Agregar Estudiante")
        
        student_id = input("ID del estudiante: ").strip()
        name = input("Nombre: ").strip()
        lastname = input("Apellidos: ").strip()
        email = input("Email: ").strip()
        career = input("Carrera (opcional): ").strip() or None
        semester = input("Semestre (opcional): ").strip() or None
        
        if self.student_manager.create_student(student_id, name, lastname, email, career, semester):
            print("\n✓ Estudiante agregado correctamente")
        else:
            print("\n✗ Error al agregar estudiante")
    
    def add_course(self):
        """Agrega un nuevo curso."""
        self.print_header("Agregar Curso")
        
        course_id = input("ID del curso: ").strip()
        course_name = input("Nombre del curso: ").strip()
        course_code = input("Código: ").strip()
        credits = input("Créditos: ").strip()
        teacher = input("Profesor (opcional): ").strip() or None
        schedule = input("Horario (opcional): ").strip() or None
        
        try:
            credits = int(credits) if credits else 0
        except ValueError:
            credits = 0
        
        if self.student_manager.create_course(course_id, course_name, course_code, credits, teacher, schedule):
            print("\n✓ Curso agregado correctamente")
        else:
            print("\n✗ Error al agregar curso")
    
    def enroll_student(self):
        """Matricula a un estudiante en un curso."""
        self.print_header("Matricular Estudiante")
        
        student_id = input("ID del estudiante: ").strip()
        course_id = input("ID del curso: ").strip()
        semester = input("Semestre (ej: 2024-I): ").strip()
        academic_year = input("Año académico (ej: 2024): ").strip()
        
        if self.student_manager.enroll_student(student_id, course_id, semester, academic_year):
            print("\n✓ Matrícula realizada correctamente")
        else:
            print("\n✗ Error al matricular")
    
    def record_attendance(self):
        """Registra asistencia de un estudiante."""
        self.print_header("Registrar Asistencia")
        
        student_id = input("ID del estudiante: ").strip()
        course_id = input("ID del curso: ").strip()
        date_str = input("Fecha (YYYY-MM-DD) [default: hoy]: ").strip()
        
        attendance_date = date.today()
        if date_str:
            try:
                attendance_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                print("\n✗ Formato de fecha inválido")
                return
        
        present = input("¿Asistió? (S/N) [default: S]: ").strip().upper() != "N"
        
        if self.attendance_system.record_attendance(student_id, course_id, attendance_date, present):
            print("\n✓ Asistencia registrada")
        else:
            print("\n✗ Error al registrar asistencia")
    
    def process_daily_attendance(self):
        """Procesa la asistencia del día y otorga tokens."""
        self.print_header("Procesar Asistencia Diaria")
        
        date_str = input("Fecha (YYYY-MM-DD) [default: hoy]: ").strip()
        
        attendance_date = date.today()
        if date_str:
            try:
                attendance_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                print("\n✗ Formato de fecha inválido")
                return
        
        print(f"\nProcesando asistencia para {attendance_date}...")
        result = self.attendance_system.check_daily_attendance(attendance_date)
        
        print(f"\n✓ Procesamiento completado:")
        print(f"  - Total estudiantes: {result['total_students']}")
        print(f"  - Tokens otorgados: {result['rewards_given']}")
        
        if result['students_with_rewards']:
            print("\n  Estudiantes que recibieron tokens:")
            for student in result['students_with_rewards']:
                print(f"    - {student['name']}: +{student['tokens']} token")
    
    def show_token_balance(self):
        """Muestra el balance de tokens de un estudiante."""
        self.print_header("Balance de Tokens")
        
        student_id = input("ID del estudiante: ").strip()
        
        balance = self.attendance_system.get_student_token_balance(student_id)
        
        # Obtener nombre del estudiante
        student = self.student_manager.get_student_info(student_id)
        if student:
            name = f"{student['name']} {student['lastname']}"
        else:
            name = "Desconocido"
        
        print(f"\nEstudiante: {name} ({student_id})")
        print(f"Balance de Tokens: {balance}")
    
    def show_redemption_catalog(self):
        """Muestra el catálogo de productos para canje."""
        self.print_header("Catálogo de Canje")
        
        catalog = self.attendance_system.get_redemption_catalog()
        
        if not catalog:
            print("\nNo hay productos disponibles")
            return
        
        print(f"\n{'ID':<6} {'Nombre':<35} {'Costo':<8} {'Categoría':<15}")
        print("-" * 70)
        
        for item in catalog:
            print(f"{item['item_id']:<6} {item['item_name']:<35} {item['item_cost']:<8} {item['item_category']:<15}")
    
    def redeem_tokens(self):
        """Canjea tokens por un producto."""
        self.print_header("Canjear Tokens")
        
        student_id = input("ID del estudiante: ").strip()
        
        # Mostrar balance actual
        balance = self.attendance_system.get_student_token_balance(student_id)
        print(f"Balance actual: {balance} tokens\n")
        
        # Mostrar catálogo
        self.show_redemption_catalog()
        
        item_id = input("\nID del producto a canjear: ").strip()
        
        try:
            item_id = int(item_id)
        except ValueError:
            print("\n✗ ID inválido")
            return
        
        result = self.attendance_system.redeem_tokens(student_id, item_id)
        
        if result["success"]:
            print(f"\n✓ {result['message']}")
            print(f"  Tokens restantes: {result['remaining_balance']}")
        else:
            print(f"\n✗ {result['message']}")
    
    def show_token_history(self):
        """Muestra el historial de tokens de un estudiante."""
        self.print_header("Historial de Tokens")
        
        student_id = input("ID del estudiante: ").strip()
        
        history = self.attendance_system.get_student_token_history(student_id)
        
        if not history:
            print("\nNo hay transacciones registradas")
            return
        
        print(f"\n{'Fecha':<12} {'Tipo':<12} {'Descripción':<40} {'Cantidad':<10}")
        print("-" * 80)
        
        for h in history:
            desc = h.get("item") or h.get("description") or ""
            amount = h["amount"]
            t_type = "Recompensa" if h["type"] == "reward" else "Canje"
            print(f"{str(h['date'])[:10]:<12} {t_type:<12} {desc:<40} {amount:<10}")
    
    def show_blockchain(self):
        """Muestra la blockchain."""
        self.print_header("Blockchain URP")
        
        chain = self.blockchain.to_list()
        
        print(f"\nTotal de bloques: {len(chain)}\n")
        
        for block in chain:
            print(f"Bloque #{block['index']}")
            print(f"  Hash: {block['hash'][:20]}...")
            print(f"  Anterior: {block['previous_hash'][:20]}...")
            print(f"  Fecha: {block['timestamp_formatted']}")
            print(f"  Datos: {block['data']}")
            print()
    
    def validate_blockchain(self):
        """Valida la integridad de la blockchain."""
        self.print_header("Validar Blockchain")
        
        is_valid = self.blockchain.is_chain_valid()
        
        if is_valid:
            print("\n✓ La blockchain es válida")
        else:
            print("\n✗ La blockchain ha sido alterada - ES INVÁLIDA")


def run_cli():
    """Función principal para ejecutar la CLI."""
    # Conectar a la base de datos
    db = get_db()
    if db.connect():
        # Crear las tablas si no existen
        models = get_models()
        models.create_tables()
        models.insert_sample_data()
    
    # Ejecutar la CLI
    cli = URPCLI()
    cli.run()
    
    # Desconectar
    db.disconnect()


if __name__ == "__main__":
    run_cli()
