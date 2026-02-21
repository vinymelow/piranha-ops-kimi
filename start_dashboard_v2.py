#!/usr/bin/env python3
"""
🦈 PiranhaOps AIOS v2.0 - Dashboard Starter
Script para iniciar o dashboard com Design System Piranha
"""

import subprocess
import time
import sys
import os
import signal

def kill_process_on_port(port):
    """Mata processos rodando em uma porta específica"""
    try:
        # Para macOS/Linux
        result = subprocess.run(['lsof', '-ti', f':{port}'], 
                              capture_output=True, text=True)
        if result.stdout:
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        print(f"🛑 Processo PID {pid} na porta {port} finalizado")
                        time.sleep(1)
                    except (ProcessLookupError, ValueError):
                        pass
    except Exception as e:
        print(f"⚠️  Não foi possível verificar processos na porta {port}: {e}")

def start_dashboard():
    """Inicia o dashboard v2.0"""
    
    print("\n" + "="*60)
    print("🦈 INICIANDO PIRANHAOPS AIOS v2.0")
    print("="*60)
    
    # Matar processos nas portas que vamos usar
    print("🧹 Limpando portas...")
    kill_process_on_port(8080)
    kill_process_on_port(8082)
    time.sleep(2)
    
    # Mudar para o diretório do dashboard
    dashboard_dir = os.path.join(os.path.dirname(__file__), 'dashboard')
    os.chdir(dashboard_dir)
    
    print("🚀 Iniciando servidor Flask com Design System Piranha...")
    print("📡 Porta: 8082")
    print("🎨 Design System: Piranha (preto #0A0A0A, vermelho #E30613)")
    print("🛒 Features: Cart Recovery, AIOS Master, Quality Gate")
    print("\n" + "="*60)
    
    try:
        # Iniciar o servidor Flask
        subprocess.run([sys.executable, 'server_v2.py'])
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
    finally:
        print("\n✅ Dashboard finalizado")

if __name__ == "__main__":
    start_dashboard()