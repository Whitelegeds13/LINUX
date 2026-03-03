# Blockchain URP - Documento de Arquitectura

## Descripcion del Proyecto

**Blockchain URP** es una aplicacion blockchain basada en Python para la Universidad Ricardo Palma que registra la asistencia de estudiantes y recompensa con tokens a quienes asisten a todos sus cursos en un dia.

---

## Arquitectura del Sistema

```mermaid
flowchart TB
    subgraph Capa_Presentacion["Capa de Presentacion"]
        CLI[cli.py<br/>Clase URPCLI]
    end
    
    subgraph Capa_Logica["Capa de Logica de Negocio"]
        SM[student_manager.py<br/>Gestor de Estudiantes]
        AS[attendance.py<br/>Sistema de Asistencia]
        BC[blockchain.py<br/>Blockchain]
    end
    
    subgraph Capa_Datos["Capa de Datos"]
        DB[database.py<br/>Conexion MySQL]
        MOD[models.py<br/>Modelos de BD]
    end
    
    subgraph BD_Externa["Base de Datos Externa"]
        MYSQL[(MySQL<br/>Servidor)]
    end
    
    CLI --> SM
    CLI --> AS
    CLI --> BC
    CLI --> MOD
    
    SM --> DB
    AS --> DB
    AS --> BC
    AS --> MOD
    BC --> MOD
    MOD --> DB
    
    DB --> MYSQL
```

---

## Descripcion de Modulos

### 1. Capa de Presentacion

| Modulo | Responsabilidad |
|--------|-----------------|
| main.py | Punto de entrada; muestra banner y ejecuta CLI |
| cli.py | Interfaz de linea de comandos con 14 opciones de menu |

---

### 2. Capa de Logica de Negocio

| Modulo | Responsabilidad |
|--------|-----------------|
| student_manager.py | Gestiona estudiantes, cursos y matriculas |
| attendance.py | Registra asistencia, procesa recompensas diarias, maneja canje de tokens |
| blockchain.py | Implementa blockchain con Prueba de Trabajo |

---

### 3. Capa de Datos

| Modulo | Responsabilidad |
|--------|-----------------|
| database.py | Gestor de conexion MySQL con proteccion contra SQL injection |
| models.py | Creacion de tablas, datos de ejemplo, operaciones CRUD |

---

## Esquema de Base de Datos

```mermaid
erDiagram
    students {
        string student_id PK
        string name
        string lastname
        string email UK
        string career
        string semester
        string wallet_address UK
        int total_tokens
        timestamp created_at
        timestamp updated_at
    }
    
    courses {
        string course_id PK
        string course_name
        string course_code UK
        int credits
        string teacher_name
        string schedule
        timestamp created_at
    }
    
    enrollments {
        int enrollment_id PK
        string student_id FK
        string course_id FK
        string semester
        string academic_year
        timestamp enrolled_at
    }
    
    daily_attendance {
        int attendance_id PK
        string student_id FK
        string course_id FK
        date attendance_date
        boolean present
        timestamp recorded_at
    }
    
    token_rewards {
        int reward_id PK
        string student_id FK
        int tokens
        date reward_date
        string reason
        string block_hash
        timestamp created_at
    }
    
    token_redemptions {
        int redemption_id PK
        string student_id FK
        string item_name
        int item_cost
        timestamp redemption_date
    }
    
    redemption_catalog {
        int item_id PK
        string item_name
        text item_description
        int item_cost
        string item_category
        boolean available
        timestamp created_at
    }
    
    blockchain_blocks {
        int block_index PK
        timestamp block_timestamp
        json block_data
        string block_previous_hash
        int block_nonce
        string block_hash UK
        timestamp created_at
    }
    
    students ||--o{ enrollments : "tiene"
    students ||--o{ daily_attendance : "registra"
    students ||--o{ token_rewards : "recibe"
    students ||--o{ token_redemptions : "canjea"
    courses ||--o{ enrollments : "contiene"
    courses ||--o{ daily_attendance : "controla"
```

---

## Flujo de Datos

### Flujo de Recompensa de Tokens
```mermaid
sequenceDiagram
    participant Usuario
    participant CLI
    participant Asistencia as Sistema de Asistencia
    participant Blockchain
    participant BaseDatos as Base de Datos
    
    Usuario->>CLI: Procesar Asistencia Diaria
    CLI->>Asistencia: verificar_asistencia_diaria(fecha)
    Asistencia->>BaseDatos: Obtener estudiantes
    BaseDatos-->>Asistencia: Lista de estudiantes
    Asistencia->>BaseDatos: Obtener cursos del estudiante
    Asistencia->>BaseDatos: Verificar asistencia por curso
    Asistencia->>Blockchain: agregar_bloque(recompensa)
    Blockchain-->>Asistencia: Nuevo bloque con hash
    Asistencia->>BaseDatos: Insertar recompensa
    Asistencia->>BaseDatos: Actualizar tokens
    Asistencia-->>CLI: Resultados
    CLI-->>Usuario: Mostrar recompensas
```

### Flujo de Canje de Tokens
```mermaid
sequenceDiagram
    participant Usuario
    participant CLI
    participant Asistencia as Sistema de Asistencia
    participant Blockchain
    participant BaseDatos as Base de Datos
    
    Usuario->>CLI: Canjear tokens
    CLI->>Asistencia: canjear_tokens(id_estudiante, id_producto)
    Asistencia->>BaseDatos: Obtener costo del producto
    Asistencia->>BaseDatos: Verificar saldo del estudiante
    alt Saldo suficiente
        Asistencia->>Blockchain: agregar_bloque(canje)
        Asistencia->>BaseDatos: Insertar registro de canje
        Asistencia->>BaseDatos: Actualizar tokens
        Asistencia-->>CLI: Exito
    else Saldo insuficiente
        Asistencia-->>CLI: Error
    end
    CLI-->>Usuario: Mostrar resultado
```

---

## Caracteristicas Principales

1. **Implementacion de Blockchain**
   - Hashing SHA-256
   - Prueba de Trabajo con dificultad 2
   - Bloque genesis
   - Validacion de cadena

2. **Sistema de Tokens**
   - 1 token por dia por asistencia perfecta
   - Catalogo de productos para canje
   - Historial de transacciones

3. **Integracion con MySQL**
   - Creacion automatica de base de datos
   - Restricciones de clave foranea
   - Datos de ejemplo precargados

---

## Configuracion

| Parametro | Valor por Defecto | Variable de Entorno |
|-----------|-------------------|---------------------|
| Host | localhost | DB_HOST |
| Usuario | root | DB_USER |
| Contrasena | 123456 | DB_PASSWORD |
| Base de datos | urp_blockchain | - |

---

## Estructura de Archivos

```
LINUX/
├── main.py                 # Punto de entrada
├── database.py             # Conexion a MySQL
├── models.py              # Tablas de BD
├── blockchain.py          # Implementacion de blockchain
├── student_manager.py     # Gestion de estudiantes
├── attendance.py          # Sistema de asistencia
├── cli.py                 # Interfaz de comandos
├── requirements.txt       # Dependencias
└── README.md             # Documentacion
```

---

## Tablas de Base de Datos

El sistema utiliza 8 tablas en MySQL:

1. **students** - Informacion de estudiantes
2. **courses** - Catalogo de cursos
3. **enrollments** - Matriculas de estudiantes
4. **daily_attendance** - Registro de asistencia diaria
5. **token_rewards** - Recompensas de tokens otorgados
6. **token_redemptions** - Canjes de tokens realizados
7. **redemption_catalog** - Productos disponibles para canje
8. **blockchain_blocks** - Bloques de la blockchain
