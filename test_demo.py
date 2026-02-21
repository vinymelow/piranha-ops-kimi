#!/usr/bin/env python3
"""
Teste direto do Demo PiranhaOps
Executa os 3 cenários sem input interativo
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orchestrator import PiranhaOps

def test_demo_direct():
    """Executa demo completo diretamente"""
    print("🚀 Iniciando teste direto do Demo PiranhaOps...")
    
    try:
        # Criar instância
        ops = PiranhaOps()
        
        # Executar demo diretamente
        print("\n" + "="*70)
        print("🎭 EXECUTANDO DEMO COMPLETO")
        print("="*70)
        
        ops.run_demo()
        
        print("\n✅ Teste demo concluído!")
        
    except Exception as e:
        print(f"\n❌ Erro durante demo: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_demo_direct()
    sys.exit(0 if success else 1)