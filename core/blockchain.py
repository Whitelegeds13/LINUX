"""
Modulo de implementacion de Blockchain para el sistema de tokens de la URP.
"""

import hashlib
import json
import time
import uuid
from typing import List, Dict, Any
from datetime import datetime


class Block:
    """Representa un bloque en la blockchain."""
    
    def __init__(self, index: int, timestamp: float, data: Dict[str, Any], 
                 previous_hash: str, nonce: int = 0):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calcula el hash del bloque usando SHA-256."""
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
    """Implementacion de la blockchain para tokens de asistencia URP."""
    
    DIFFICULTY = 2  # Dificultad de la prueba de trabajo
    
    def __init__(self, load_from_db=True):
        """Inicializa la blockchain con el bloque genesis."""
        # Intentar cargar desde la base de datos
        if load_from_db:
            self.chain = self._load_from_db()
            if not self.chain:
                self.chain = [self.create_genesis_block()]
        else:
            self.chain = [self.create_genesis_block()]
    
    def _load_from_db(self):
        """Carga la cadena desde la base de datos."""
        try:
            from .models import BlockchainBlock
            blocks = BlockchainBlock.objects.all().order_by('block_index')
            if not blocks.exists():
                return None
            
            chain = []
            for block_record in blocks:
                block = Block(
                    index=block_record.block_index,
                    timestamp=block_record.block_timestamp.timestamp(),
                    data=block_record.block_data,
                    previous_hash=block_record.block_previous_hash,
                    nonce=block_record.block_nonce
                )
                block.hash = block_record.block_hash
                chain.append(block)
            
            return chain if chain else None
        except Exception:
            # Si hay error (base de datos no disponible), retornar None
            return None
    
    def save_to_db(self):
        """Guarda la cadena completa en la base de datos."""
        try:
            from .models import BlockchainBlock
            from django.utils import timezone
            
            for block in self.chain:
                BlockchainBlock.objects.update_or_create(
                    block_index=block.index,
                    defaults={
                        'block_timestamp': timezone.make_aware(datetime.fromtimestamp(block.timestamp)),
                        'block_data': block.data,
                        'block_previous_hash': block.previous_hash,
                        'block_nonce': block.nonce,
                        'block_hash': block.hash
                    }
                )
            return True
        except Exception:
            return False
    
    def _save_block_to_db(self, block):
        """Guarda un solo bloque en la base de datos."""
        try:
            from .models import BlockchainBlock
            from django.utils import timezone
            
            BlockchainBlock.objects.update_or_create(
                block_index=block.index,
                defaults={
                    'block_timestamp': timezone.make_aware(datetime.fromtimestamp(block.timestamp)),
                    'block_data': block.data,
                    'block_previous_hash': block.previous_hash,
                    'block_nonce': block.nonce,
                    'block_hash': block.hash
                }
            )
            return True
        except Exception:
            return False
    
    def create_genesis_block(self) -> Block:
        """Crea el bloque genesis (primer bloque de la cadena)."""
        return Block(
            index=0,
            timestamp=time.time(),
            data={
                "type": "genesis",
                "description": "Bloque genesis - Inicio de la Blockchain URP",
                "university": "Universidad Ricardo Palma"
            },
            previous_hash="0",
            nonce=0
        )
    
    def get_latest_block(self) -> Block:
        """Retorna el ultimo bloque de la cadena."""
        return self.chain[-1]
    
    def add_block(self, data: Dict[str, Any]) -> Block:
        """Anade un nuevo bloque a la cadena con prueba de trabajo."""
        previous_block = self.get_latest_block()
        
        # Generar un nonce unico basado en UUID para mayor seguridad
        unique_nonce = f"{uuid.uuid4().hex[:8]}{int(time.time() * 1000000)}"
        
        new_block = Block(
            index=previous_block.index + 1,
            timestamp=time.time(),
            data=data,
            previous_hash=previous_block.hash,
            nonce=0
        )
        
        # Anadir el nonce unico a los datos del bloque
        new_block.data["nonce_unique"] = unique_nonce
        
        # Prueba de trabajo (Proof of Work)
        new_block = self.proof_of_work(new_block)
        
        self.chain.append(new_block)
        
        # Guardar en base de datos
        self._save_block_to_db(new_block)
        
        return new_block
    
    def proof_of_work(self, block: Block) -> Block:
        """Implementa la prueba de trabajo (mineria del bloque)."""
        target = "0" * self.DIFFICULTY
        
        while block.hash[:self.DIFFICULTY] != target:
            block.nonce += 1
            block.hash = block.calculate_hash()
        
        return block
    
    def is_chain_valid(self) -> bool:
        """Valida la integridad de toda la blockchain."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Verificar que el hash del bloque actual es correcto
            if current_block.hash != current_block.calculate_hash():
                print(f"[X] Hash invalido en bloque {i}")
                return False
            
            # Verificar que el hash anterior coincide
            if current_block.previous_hash != previous_block.hash:
                print(f"[X] Enlace invalido entre bloques {i-1} e {i}")
                return False
        
        return True
    
    def to_list(self) -> List[Dict[str, Any]]:
        """Convierte toda la cadena a una lista de diccionarios."""
        return [block.to_dict() for block in self.chain]
    
    def get_block_count(self) -> int:
        """Retorna el numero de bloques en la cadena."""
        return len(self.chain)
    
    def find_token_transactions(self, student_id: str) -> List[Dict[str, Any]]:
        """Busca todas las transacciones de tokens de un estudiante."""
        transactions = []
        for block in self.chain:
            data = block.data
            
            # Transacciones de reward (otorgar tokens)
            if data.get("type") == "token_reward":
                if data.get("student_id") == student_id:
                    transactions.append({
                        "type": "reward",
                        "token_id": data.get("token_id", ""),
                        "amount": data.get("tokens", 0),
                        "date": block.to_dict()["timestamp_formatted"],
                        "block_index": block.index
                    })
            
            # Transacciones de redencion (canjeo)
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


# Instancia global de la blockchain (se carga desde la base de datos si esta disponible)
blockchain = Blockchain(load_from_db=True)


def get_blockchain() -> Blockchain:
    """Retorna la instancia global de la blockchain."""
    global blockchain
    # Verificar si la cadena esta vacia y hay datos en la BD
    if blockchain.get_block_count() == 1:  # Solo genesis
        blockchain = Blockchain(load_from_db=True)
    return blockchain
