# Blockchain URP - Universidad Ricardo Palma

Sistema de blockchain en Python para gestionar tokens de asistencia para estudiantes de la Universidad Ricardo Palma.

## Descripción

Este sistema implementa una blockchain que registra la asistencia de los estudiantes y otorga tokens cuando un estudiante asiste a todos sus cursos matriculados en un día.

### Características

- **Blockchain propia**: Implementación de blockchain con prueba de trabajo (Proof of Work)
- **Gestión de estudiantes**: Registro y gestión de estudiantes
- **Gestión de cursos**: Registro de cursos y matrículas
- **Control de asistencia**: Registro diario de asistencia por curso
- **Recompensas**: 1 token por día si el estudiante asiste a todos sus cursos
- **Canje de tokens**: Catálogo de productos para canjear tokens (almuerzos, bebidas, materiales, etc.)
- **Integración con MySQL**: Almacenamiento persistente en base de datos

## Requisitos

- Python 3.8+
- MySQL Server 8.0+
- mysql-connector-python

## Instalación

1. Clonar el repositorio:
```bash
git clone <repo-url>
cd LINUX
```

2. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

3. Asegurarse de que MySQL esté ejecutándose con las credenciales:
   - Usuario: `root`
   - Contraseña: `123456`

## Uso

Ejecutar el programa:
```bash
python main.py
```

### Opciones del menú

1. **Inicializar Base de Datos** - Crea las tablas necesarias
2. **Ver Estudiantes** - Lista todos los estudiantes registrados
3. **Ver Cursos** - Lista todos los cursos disponibles
4. **Agregar Estudiante** - Registra un nuevo estudiante
5. **Agregar Curso** - Registra un nuevo curso
6. **Matricular Estudiante en Curso** - Matricula a un estudiante
7. **Registrar Asistencia** - Registra asistencia a un curso
8. **Procesar Asistencia Diaria** - Otorga tokens a quienes asistieron a todos sus cursos
9. **Ver Balance de Tokens** - Consulta tokens de un estudiante
10. **Ver Catálogo de Canje** - Muestra productos disponibles
11. **Canjear Tokens** - Canjea tokens por productos
12. **Ver Historial de Tokens** - Historial de transacciones
13. **Ver Blockchain** - Muestra la cadena de bloques
14. **Validar Blockchain** - Verifica integridad de la cadena

## Estructura del Proyecto

```
├── main.py                 # Punto de entrada del programa
├── database.py             # Módulo de conexión a MySQL
├── blockchain.py           # Implementación de la blockchain
├── models.py               # Modelos/tablas de base de datos
├── student_manager.py      # Gestión de estudiantes y cursos
├── attendance.py          # Sistema de asistencia y recompensas
├── cli.py                  # Interfaz de línea de comandos
└── requirements.txt        # Dependencias Python
```

## Sistema de Tokens

### Cómo obtener tokens

1. El estudiante debe estar matriculado en cursos
2. Cada día, el sistema verifica la asistencia a todos los cursos
3. Si el estudiante asistió a TODOS sus cursos, recibe **1 token**

### Canje de tokens

Los tokens pueden canjearse por productos del catálogo:
- Almuerzo Gratis - 10 tokens
- Café + Galletas - 5 tokens
- Libro de Texto - 30 tokens
- Impresiones B/N - 3 tokens
- Y más...

## Configuración de Base de Datos

El sistema se conecta a MySQL con las siguientes credenciales por defecto:
- Host: localhost
- Usuario: root
- Contraseña: 123456
- Base de datos: urp_blockchain (se crea automáticamente)

## Blockchain

La blockchain utiliza:
- **Algoritmo de hash**: SHA-256
- **Prueba de trabajo**: Difficulty = 2 (dos ceros al inicio)
- **Datos almacenados**: Recompensas de tokens, redenciones, genesis block

## Universidad Ricardo Palma

Sistema diseñado para la Universidad Ricardo Palma, Perú.
