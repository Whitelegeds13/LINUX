"""
Módulo de conexión a MySQL para el sistema de blockchain de la Universidad Ricardo Palma.
"""

import mysql.connector
from mysql.connector import Error
from typing import Optional, Dict, Any, List
import hashlib
import json
import os
import re


class MySQLConnection:
    """Clase para manejar la conexión a la base de datos MySQL."""
    
    def __init__(self, host: str = None, user: str = None, 
                 password: str = None, database: str = "urp_blockchain"):
        """
        Inicializa la conexión a MySQL.
        
        Args:
            host: Host del servidor MySQL
            user: Usuario de MySQL
            password: Contraseña de MySQL
            database: Nombre de la base de datos
        """
        self.host = host or os.getenv("DB_HOST", "localhost")
        self.user = user or os.getenv("DB_USER", "root")
        self.password = password or os.getenv("DB_PASSWORD", "123456")
        self.database = database
        self.connection: Optional[mysql.connector.connection.MySQLConnection] = None
    
    def _validate_database_name(self, db_name: str) -> bool:
        """
        Valida el nombre de la base de datos para prevenir SQL injection.
        
        Args:
            db_name: Nombre de la base de datos a validar
            
        Returns:
            True si el nombre es válido, False en caso contrario
        """
        # Solo permite caracteres alfanuméricos y guiones bajos
        return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', db_name))
    
    def connect(self) -> bool:
        """
        Establece la conexión a la base de datos.
        
        Returns:
            True si la conexión fue exitosa, False en caso contrario
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            print(f"[OK] Conectado a MySQL en {self.host}")
            return True
        except Error as e:
            print(f"[X] Error al conectar a MySQL: {e}")
            # Intentar crear la base de datos si no existe
            try:
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password
                )
                cursor = self.connection.cursor()
                # Validar nombre de base de datos para prevenir SQL injection
                if not self._validate_database_name(self.database):
                    print(f"[!] Nombre de base de datos invalido: {self.database}")
                    return False
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
                cursor.close()
                self.connection.close()
                
                # Reconectar con la base de datos
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
                print(f"[OK] Base de datos '{self.database}' creada y conectada")
                return True
            except Error as e:
                print(f"[X] Error al crear la base de datos: {e}")
                return False
    
    def disconnect(self):
        """Cierra la conexión a la base de datos."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("[OK] Desconectado de MySQL")
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[List[Dict[str, Any]]]:
        """
        Ejecuta una consulta SQL y retorna los resultados.
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros de la consulta
            
        Returns:
            Lista de diccionarios con los resultados o None si hay error
        """
        if not self.connection or not self.connection.is_connected():
            print("[X] No hay conexion a la base de datos")
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if query.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()
                cursor.close()
                return results
            else:
                self.connection.commit()
                cursor.close()
                return [{"affected_rows": cursor.rowcount}]
        except Error as e:
            print(f"[X] Error al ejecutar consulta: {e}")
            return None
    
    def execute_many(self, query: str, data: List[tuple]) -> bool:
        """
        Ejecuta una consulta SQL con múltiples valores.
        
        Args:
            query: Consulta SQL a ejecutar
            data: Lista de tuplas con los valores
            
        Returns:
            True si fue exitoso, False en caso contrario
        """
        if not self.connection or not self.connection.is_connected():
            print("[X] No hay conexion a la base de datos")
        
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, data)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"[X] Error al ejecutar consulta multiple: {e}")
            return False


# Instancia global de conexión
db = MySQLConnection(
    user=os.getenv("DB_USER", "root"), 
    password=os.getenv("DB_PASSWORD", "123456")
)


def get_db() -> MySQLConnection:
    """Retorna la instancia global de la base de datos."""
    return db
