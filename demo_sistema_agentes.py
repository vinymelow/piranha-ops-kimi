#!/usr/bin/env python3
"""
Demo do Sistema de Monitoramento de Agentes - PiranhaOps AIOS v3.0

Este script demonstra o sistema completo de monitoramento de agentes em tempo real,
mostrando as funcionalidades implementadas e os dados em tempo real.
"""

import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path

class DemoAgentMonitor:
    def __init__(self):
        self.data_file = Path(__file__).parent / "demo_agentes_dados.json"
        self.load_demo_data()
        
    def load_demo_data(self):
        """Carrega dados demo do arquivo JSON"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar dados demo: {e}")
            self.data = self.create_mock_data()
    
    def create_mock_data(self):
        """Cria dados mock se não existirem"""
        return {
            "agents": [
                {
                    "id": "commercial-agent-01",
                    "name": "Cart Recovery Bot",
                    "squad": "commercial",
                    "status": "running",
                    "tasks_completed": 47,
                    "tasks_failed": 2,
                    "avg_quality_score": 0.94,
                    "last_activity": datetime.now().isoformat()
                }
            ],
            "running_tasks": [],
            "task_history": [],
            "stats": {
                "total_agents": 1,
                "active_agents": 1,
                "total_tasks_today": 10,
                "avg_quality_score": 0.94
            }
        }
    
    def simulate_real_time_updates(self):
        """Simula atualizações em tempo real dos agentes"""
        print("🤖 Iniciando simulação de atualizações em tempo real...")
        print("=" * 80)
        
        try:
            while True:
                self.update_agents_status()
                self.simulate_new_tasks()
                self.update_task_progress()
                self.print_status()
                
                # Aguardar 5 segundos para próxima atualização
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Simulação interrompida pelo usuário")
            self.print_final_summary()
    
    def update_agents_status(self):
        """Atualiza status dos agentes"""
        for agent in self.data["agents"]:
            # Simular mudanças aleatórias de status
            if random.random() > 0.8:
                possible_status = ["running", "online", "idle"]
                agent["status"] = random.choice(possible_status)
            
            # Atualizar última atividade
            agent["last_activity"] = datetime.now().isoformat()
            
            # Incrementar tasks completadas aleatoriamente
            if random.random() > 0.7:
                agent["tasks_completed"] += 1
                if random.random() > 0.9:  # Pequena chance de falha
                    agent["tasks_failed"] += 1
            
            # Ajustar qualidade ligeiramente
            quality_change = random.uniform(-0.02, 0.02)
            agent["avg_quality_score"] = max(0.7, min(1.0, agent["avg_quality_score"] + quality_change))
    
    def simulate_new_tasks(self):
        """Simula criação de novas tasks"""
        # 30% de chance de nova task
        if random.random() > 0.7:
            task_types = [
                "Cart Recovery", "Lead Processing", "Stock Alert",
                "Data Analysis", "Partner Management", "Compliance Check"
            ]
            
            priorities = [1, 2, 3, 4, 5]
            
            new_task = {
                "id": f"task-{random.randint(1000, 9999)}",
                "agent_id": random.choice([a["id"] for a in self.data["agents"]]),
                "type": random.choice(task_types),
                "description": f"Nova task de {random.choice(task_types).lower()}",
                "priority": random.choice(priorities),
                "status": "running",
                "quality_score": random.uniform(0.8, 0.98),
                "started_at": datetime.now().isoformat()
            }
            
            self.data["running_tasks"].append(new_task)
            print(f"✅ Nova task criada: {new_task['type']} (Priority: {new_task['priority']})")
    
    def update_task_progress(self):
        """Atualiza progresso das tasks em execução"""
        completed_tasks = []
        
        for task in self.data["running_tasks"]:
            # 20% de chance de completar
            if random.random() > 0.8:
                task["status"] = "completed"
                task["completed_at"] = datetime.now().isoformat()
                completed_tasks.append(task)
                
                # Adicionar ao histórico
                self.data["task_history"].insert(0, task)
                
                print(f"✅ Task completada: {task['type']} (Quality: {task['quality_score']:.2f})")
        
        # Remover tasks completadas da lista de execução
        for task in completed_tasks:
            self.data["running_tasks"].remove(task)
    
    def print_status(self):
        """Imprime status atual dos agentes"""
        print(f"\n📊 Status Update - {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 50)
        
        # Estatísticas gerais
        total_agents = len(self.data["agents"])
        active_agents = len([a for a in self.data["agents"] if a["status"] == "running"])
        total_tasks = sum(a["tasks_completed"] for a in self.data["agents"])
        avg_quality = sum(a["avg_quality_score"] for a in self.data["agents"]) / total_agents
        
        print(f"📈 Agentes: {active_agents}/{total_agents} ativos")
        print(f"📋 Tasks em execução: {len(self.data['running_tasks'])}")
        print(f"✅ Tasks completadas: {total_tasks}")
        print(f"🎯 Qualidade média: {avg_quality:.2f}")
        
        # Status por agente
        print(f"\n🤖 Agentes Detalhados:")
        for agent in self.data["agents"]:
            status_icon = {
                "running": "⚡",
                "online": "🟢", 
                "idle": "⏸️",
                "offline": "🔴"
            }.get(agent["status"], "❓")
            
            print(f"  {status_icon} {agent['name']}: {agent['tasks_completed']} tasks | Qualidade: {agent['avg_quality_score']:.2f}")
        
        # Tasks em execução
        if self.data["running_tasks"]:
            print(f"\n⚡ Tasks em Execução:")
            for task in self.data["running_tasks"]:
                print(f"  📝 {task['type']} - {task['agent_id']} (Priority: {task['priority']})")
    
    def print_final_summary(self):
        """Imprime resumo final da simulação"""
        print("\n" + "=" * 80)
        print("📊 RESUMO FINAL DA SIMULAÇÃO")
        print("=" * 80)
        
        total_agents = len(self.data["agents"])
        total_tasks = sum(a["tasks_completed"] for a in self.data["agents"])
        total_failed = sum(a["tasks_failed"] for a in self.data["agents"])
        avg_quality = sum(a["avg_quality_score"] for a in self.data["agents"]) / total_agents
        
        print(f"Total de Agentes: {total_agents}")
        print(f"Total de Tasks Completadas: {total_tasks}")
        print(f"Total de Tasks Falhadas: {total_failed}")
        print(f"Taxa de Sucesso: {((total_tasks - total_failed) / total_tasks * 100):.1f}%")
        print(f"Qualidade Média: {avg_quality:.3f}")
        print(f"Tasks no Histórico: {len(self.data['task_history'])}")
        
        print(f"\n✅ Sistema de Monitoramento de Agentes funcionando perfeitamente!")
        print(f"🌐 Visualização disponível em: http://localhost:8087/visualizacao_agentes.html")
    
    def export_current_state(self):
        """Exporta estado atual para arquivo JSON"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            print(f"💾 Estado atual exportado para: {self.data_file}")
        except Exception as e:
            print(f"Erro ao exportar dados: {e}")
    
    def run_demo(self):
        """Executa demonstração completa do sistema"""
        print("🤖 PiranhaOps AIOS v3.0 - Demo de Monitoramento de Agentes")
        print("=" * 80)
        print("📋 Funcionalidades demonstradas:")
        print("  ✅ Monitoramento em tempo real de agentes")
        print("  ✅ Visualização de tasks em execução")
        print("  ✅ Histórico de execuções com qualidade")
        print("  ✅ Atualizações automáticas a cada 5 segundos")
        print("  ✅ Simulação de falhas e recuperações")
        print("  ✅ Cálculo de métricas de performance")
        print("=" * 80)
        print("\n🌐 Abra o navegador em: http://localhost:8087/visualizacao_agentes.html")
        print("📝 Pressione Ctrl+C para parar a simulação\n")
        
        # Iniciar simulação
        try:
            self.simulate_real_time_updates()
        finally:
            # Exportar estado final
            self.export_current_state()

if __name__ == "__main__":
    demo = DemoAgentMonitor()
    demo.run_demo()