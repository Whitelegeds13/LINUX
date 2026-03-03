"""
Script principal para ejecutar el sistema de Blockchain URP.

Universidad Ricardo Palma - Sistema de Tokens por Asistencia
"""

import sys
import os

# Añadir el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli import run_cli


def main():
    """Función principal del programa."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         BLOCKCHAIN URP - Universidad Ricardo Palma          ║
║                                                              ║
║    Sistema de Tokens por Asistencia de Alumnos               ║
║                                                              ║
║    Cada día que un alumno asista a todos sus cursos          ║
║    matriculados, recibirá 1 token.                            ║
║                                                              ║
║    Los tokens pueden canjearse por:                          ║
║    - Almuerzo gratis                                         ║
║    - Comida, bebidas, materiales y más                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        run_cli()
    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido por el usuario")
    except Exception as e:
        print(f"\n✗ Error inesperado: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
