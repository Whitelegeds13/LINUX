"""
Módulo de implementación de Blockchain para el sistema de tokens de la URP.
"""

import hashlib
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime


class Block:
    """Representa un bloque en la blockchain."""
    
    def __init__(self, index: int, timestamp: float, data: Dict[str, Any], 
                 previous_hash: str, nonce: int = 0):
        """
        Inicializa un bloque.
        
        Args:
            index: Índice del bloque en la cadena
            timestamp: Marca de tiempo de creación
            data: Datos del bloque (asistencias, transacciones, etc.)
            previous_hash: Hash del bloque anterior
            nonce: Número usado para la prueba de trabajo
        """
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """
        Calcula el hash del bloque usando SHA-256.
        
        Returns:
            Hash del bloque en formato hexadecimal
        """
        block_content = (
            str(self.index) +
            str(self.timestamp) +
            json.dumps(self.data, sort_keys=True) +
            self.previous_hash +
            str(self.nonce)
        )
        return hashlib.sha256(block_content.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el bloque a un diccionario."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "timestamp_formatted": datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Block':
        """Crea un bloque desde un diccionario."""
        block = Block(
            index=data["index"],
            timestamp=data["timestamp"],
            data=data["data"],
            previous_hash=data["previous_hash"],
            nonce=data["nonce"]
        )
        block.hash = data["hash"]
        return block


class Blockchain:
    """Implementación de la blockchain para tokens de asistencia URP."""
    
    DIFFICULTY = 2  # Dificultad de la prueba de trabajo
    
    def __init__(self):
        """Inicializa la blockchain con el bloque génesis."""
        self.chain: List[Block] = [self.create_genesis_block()]
    
    def create_genesis_block(self) -> Block:
        """
        Crea el bloque génesis (primer bloque de la cadena).
        
        Returns:
            El bloque génesis
        """
        return Block(
            index=0,
            timestamp=time.time(),
            data={
                "type": "genesis",
                "description": "Bloque génesis - Inicio de la Blockchain URP",
                "university": "Universidad Ricardo Palma"
            },
            previous_hash="0",
            nonce=0
        )
    
    def get_latest_block(self) -> Block:
        """Retorna el último bloque de la cadena."""
        return self.chain[-1]
    
    def add_block(self, data: Dict[str, Any]) -> Block:
        """
        Añade un nuevo bloque a la cadena con prueba de trabajo.
        
        Args:
            data: Datos a incluir en el bloque
            
        Returns:
            El nuevo bloque añadido
        """
        previous_block = self.get_latest_block()
        new_block = Block(
            index=previous_block.index + 1,
            timestamp=time.time(),
            data=data,
            previous_hash=previous_block.hash,
            nonce=0
        )
        
        # Prueba de trabajo (Proof of Work)
        new_block = self.proof_of_work(new_block)
        
        self.chain.append(new_block)
        return new_block
    
    def proof_of_work(self, block: Block) -> Block:
        """
        Implementa la prueba de trabajo (minería del bloque).
        
        Args:
            block: Bloque a minar
            
        Returns:
            Bloque minado con el nonce correcto
        """
        target = "0" * self.DIFFICULTY
        
        while block.hash[:self.DIFFICULTY] != target:
            block.nonce += 1
            block.hash = block.calculate_hash()
        
        return block
    
    def is_chain_valid(self) -> bool:
        """
        Valida la integridad de toda la blockchain.
        
        Returns:
            True si la cadena es válida, False en caso contrario
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Verificar que el hash del bloque actual es correcto
            if current_block.hash != current_block.calculate_hash():
                print(f"✗ Hash inválido en bloque {i}")
                return False
            
            # Verificar que el hash anterior coincide
            if current_block.previous_hash != previous_block.hash:
                print(f"✗ Enlace inválido entre bloques {i-1} e {i}")
                return False
        
        return True
    
    def to_list(self) -> List[Dict[str, Any]]:
        """Convierte toda la cadena a una lista de diccionarios."""
        return [block.to_dict() for block in self.chain]
    
    def get_block_count(self) -> int:
        """Retorna el número de bloques en la cadena."""
        return len(self.chain)
    
    def find_blocks_by_type(self, block_type: str) -> List[Block]:
        """
        Busca bloques por tipo de datos.
        
        Args:
            block_type: Tipo de bloque a buscar
            
        Returns:
            Lista de bloques que coinciden
        """
        return [
            block for block in self.chain 
            if block.data.get("type") == block_type
        ]
    
    def find_blocks_by_student(self, student_id: str) -> List[Block]:
        """
        Busca bloques relacionados con un estudiante específico.
        
        Args:
            student_id: ID del estudiante
            
        Returns:
            Lista de bloques relacionados con el estudiante
        """
        results = []
        for block in self.chain:
            data = block.data
            if data.get("student_id") == student_id:
                results.append(block)
            elif data.get("type") == "daily_attendance":
                # Buscar en la lista de estudiantes
                students = data.get("students", [])
                if any(s.get("student_id") == student_id for s in students):
                    results.append(block)
        return results
    
    def find_token_transactions(self, student_id: str) -> List[Dict[str, Any]]:
        """
        Busca todas las transacciones de tokens de un estudiante.
        
        Args:
            student_id: ID del estudiante
            
        Returns:
            Lista de transacciones de tokens
        """
        transactions = []
        for block in self.chain:
            data = block.data
            
            # Transacciones de reward (otorgar tokens)
            if data.get("type") == "token_reward":
                if data.get("student_id") == student_id:
                    transactions.append({
                        "type": "reward",
                        "amount": data.get("tokens", 0),
                        "date": block.to_dict()["timestamp_formatted"],
                        "block_index": block.index
                    })
            
            # Transacciones de redención (canjeo)
            if data.get("type") == "token_redemption":
                if data.get("student_id") == student_id:
                    transactions.append({
                        "type": "redemption",
                        "item": data.get("item", ""),
                        "cost": data.get("cost", 0),
                        "date": block.to_dict()["timestamp_formatted"],
                        "block_index": block.index
                    })
        
        return transactions


# Instancia global de la blockchain
blockchain = Blockchain()


def get_blockchain() -> Blockchain:
    """Retorna la instancia global de la blockchain."""
    return blockchain
