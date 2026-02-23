#!/usr/bin/env python3
"""
Agent Monitor - Sistema de Monitoramento de Agentes e Tasks
Visualização em tempo real do trabalho dos agentes AIOS
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import sqlite3
import threading
import time

logger = logging.getLogger("aios.agent_monitor")

class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Agent:
    """Representa um agente do sistema"""
    id: str
    name: str
    squad: str
    status: AgentStatus
    current_task_id: Optional[str] = None
    tasks_completed: int = 0
    tasks_failed: int = 0
    avg_quality_score: float = 0.0
    last_activity: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Task:
    """Representa uma task executada por um agente"""
    id: str
    agent_id: str
    type: str
    description: str
    priority: TaskPriority
    status: AgentStatus
    payload: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    quality_score: float = 0.0
    execution_time_ms: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class AgentMonitor:
    """
    Monitoramento completo de agentes e tasks
    Fornece visualização em tempo real e histórico
    """
    
    def __init__(self, db_path: str = "data/agent_monitor.db"):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        # Estado em memória para performance
        self.agents: Dict[str, Agent] = {}
        self.running_tasks: Dict[str, Task] = {}
        self.recent_tasks: List[Task] = []
        self.metrics_history: List[Dict] = []
        
        # Locks para thread safety
        self.agents_lock = threading.Lock()
        self.tasks_lock = threading.Lock()
        
        # Iniciar monitoramento em background
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._background_monitor, daemon=True)
        self.monitor_thread.start()
        
        logger.info("🤖 Agent Monitor inicializado")
    
    def _init_database(self):
        """Inicializa SQLite com schemas de agentes e tasks"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de agentes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                squad TEXT NOT NULL,
                status TEXT NOT NULL,
                current_task_id TEXT,
                tasks_completed INTEGER DEFAULT 0,
                tasks_failed INTEGER DEFAULT 0,
                avg_quality_score REAL DEFAULT 0.0,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de tasks
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                type TEXT NOT NULL,
                description TEXT NOT NULL,
                priority INTEGER NOT NULL,
                status TEXT NOT NULL,
                payload TEXT,
                result TEXT,
                quality_score REAL DEFAULT 0.0,
                execution_time_ms INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES agents(id)
            )
        """)
        
        # Índices para performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_id ON tasks(agent_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_status ON tasks(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_created ON tasks(created_at)")
        
        conn.commit()
        conn.close()
    
    # ===== AGENT MANAGEMENT =====
    
    def register_agent(self, agent_id: str, name: str, squad: str) -> Agent:
        """Registra um novo agente no sistema"""
        with self.agents_lock:
            agent = Agent(
                id=agent_id,
                name=name,
                squad=squad,
                status=AgentStatus.IDLE
            )
            
            self.agents[agent_id] = agent
            
            # Persistir no banco
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO agents (id, name, squad, status)
                VALUES (?, ?, ?, ?)
            """, (agent_id, name, squad, AgentStatus.IDLE.value))
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Agente registrado: {agent_id} ({name}) - Squad: {squad}")
            return agent
    
    def update_agent_status(self, agent_id: str, status: AgentStatus, task_id: Optional[str] = None):
        """Atualiza status de um agente"""
        with self.agents_lock:
            if agent_id not in self.agents:
                logger.warning(f"Agente não encontrado: {agent_id}")
                return
            
            agent = self.agents[agent_id]
            old_status = agent.status
            agent.status = status
            agent.current_task_id = task_id
            agent.last_activity = datetime.now()
            
            # Persistir mudança
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE agents 
                SET status = ?, current_task_id = ?, last_activity = ?
                WHERE id = ?
            """, (status.value, task_id, datetime.now(), agent_id))
            conn.commit()
            conn.close()
            
            logger.debug(f"🔄 Agente {agent_id}: {old_status.value} → {status.value}")
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Retorna dados de um agente específico"""
        with self.agents_lock:
            return self.agents.get(agent_id)
    
    def get_all_agents(self) -> List[Agent]:
        """Retorna lista de todos os agentes"""
        with self.agents_lock:
            return list(self.agents.values())
    
    def get_agents_by_squad(self, squad: str) -> List[Agent]:
        """Retorna agentes de um squad específico"""
        with self.agents_lock:
            return [agent for agent in self.agents.values() if agent.squad == squad]
    
    # ===== TASK MANAGEMENT =====
    
    def create_task(self, task_id: str, agent_id: str, task_type: str, 
                   description: str, priority: TaskPriority, payload: Dict[str, Any]) -> Task:
        """Cria uma nova task"""
        with self.tasks_lock:
            task = Task(
                id=task_id,
                agent_id=agent_id,
                type=task_type,
                description=description,
                priority=priority,
                status=AgentStatus.RUNNING,
                payload=payload,
                started_at=datetime.now()
            )
            
            self.running_tasks[task_id] = task
            
            # Atualizar agente
            self.update_agent_status(agent_id, AgentStatus.RUNNING, task_id)
            
            # Persistir no banco
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tasks (id, agent_id, type, description, priority, status, payload, started_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (task_id, agent_id, task_type, description, priority.value, 
                  AgentStatus.RUNNING.value, json.dumps(payload), datetime.now()))
            conn.commit()
            conn.close()
            
            logger.info(f"📝 Task criada: {task_id} para agente {agent_id} - {description}")
            return task
    
    def complete_task(self, task_id: str, result: Dict[str, Any], quality_score: float, execution_time_ms: int):
        """Completa uma task e atualiza estatísticas"""
        with self.tasks_lock:
            if task_id not in self.running_tasks:
                logger.warning(f"Task não encontrada em execução: {task_id}")
                return
            
            task = self.running_tasks[task_id]
            
            # Atualizar task
            task.status = AgentStatus.COMPLETED
            task.result = result
            task.quality_score = quality_score
            task.execution_time_ms = execution_time_ms
            task.completed_at = datetime.now()
            
            # Mover para histórico
            del self.running_tasks[task_id]
            self.recent_tasks.append(task)
            
            # Limitar histórico (últimas 1000 tasks)
            if len(self.recent_tasks) > 1000:
                self.recent_tasks.pop(0)
            
            # Atualizar agente
            agent = self.agents.get(task.agent_id)
            if agent:
                agent.tasks_completed += 1
                agent.avg_quality_score = (agent.avg_quality_score * (agent.tasks_completed - 1) + quality_score) / agent.tasks_completed
                self.update_agent_status(task.agent_id, AgentStatus.IDLE)
            
            # Persistir conclusão
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tasks 
                SET status = ?, result = ?, quality_score = ?, execution_time_ms = ?, completed_at = ?
                WHERE id = ?
            """, (AgentStatus.COMPLETED.value, json.dumps(result), quality_score, 
                  execution_time_ms, datetime.now(), task_id))
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Task completada: {task_id} - Qualidade: {quality_score:.2f} - Tempo: {execution_time_ms}ms")
    
    def fail_task(self, task_id: str, error: str):
        """Marca uma task como falhada"""
        with self.tasks_lock:
            if task_id not in self.running_tasks:
                logger.warning(f"Task não encontrada em execução: {task_id}")
                return
            
            task = self.running_tasks[task_id]
            task.status = AgentStatus.FAILED
            task.result = {"error": error}
            task.completed_at = datetime.now()
            
            # Mover para histórico
            del self.running_tasks[task_id]
            self.recent_tasks.append(task)
            
            # Limitar histórico
            if len(self.recent_tasks) > 1000:
                self.recent_tasks.pop(0)
            
            # Atualizar agente
            agent = self.agents.get(task.agent_id)
            if agent:
                agent.tasks_failed += 1
                self.update_agent_status(task.agent_id, AgentStatus.IDLE)
            
            # Persistir falha
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tasks 
                SET status = ?, result = ?, completed_at = ?
                WHERE id = ?
            """, (AgentStatus.FAILED.value, json.dumps({"error": error}), datetime.now(), task_id))
            conn.commit()
            conn.close()
            
            logger.error(f"❌ Task falhou: {task_id} - Erro: {error}")
    
    def get_running_tasks(self) -> List[Task]:
        """Retorna tasks em execução"""
        with self.tasks_lock:
            return list(self.running_tasks.values())
    
    def get_recent_tasks(self, limit: int = 50) -> List[Task]:
        """Retorna tasks recentes (últimas N)"""
        with self.tasks_lock:
            return self.recent_tasks[-limit:]
    
    def get_agent_tasks(self, agent_id: str, limit: int = 20) -> List[Task]:
        """Retorna tasks de um agente específico"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM tasks 
            WHERE agent_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (agent_id, limit))
        
        tasks = []
        for row in cursor.fetchall():
            task = Task(
                id=row[0],
                agent_id=row[1],
                type=row[2],
                description=row[3],
                priority=TaskPriority(row[4]),
                status=AgentStatus(row[5]),
                payload=json.loads(row[6]) if row[6] else {},
                result=json.loads(row[7]) if row[7] else None,
                quality_score=row[8],
                execution_time_ms=row[9],
                created_at=datetime.fromisoformat(row[10]),
                started_at=datetime.fromisoformat(row[11]) if row[11] else None,
                completed_at=datetime.fromisoformat(row[12]) if row[12] else None
            )
            tasks.append(task)
        
        conn.close()
        return tasks
    
    # ===== MONITORAMENTO EM TEMPO REAL =====
    
    def get_realtime_metrics(self) -> Dict[str, Any]:
        """Retorna métricas em tempo real"""
        with self.agents_lock:
            with self.tasks_lock:
                total_agents = len(self.agents)
                active_agents = len([a for a in self.agents.values() if a.status == AgentStatus.RUNNING])
                total_tasks = len(self.recent_tasks) + len(self.running_tasks)
                
                # Calcular qualidade média
                if self.recent_tasks:
                    avg_quality = sum(t.quality_score for t in self.recent_tasks if t.quality_score > 0) / len([t for t in self.recent_tasks if t.quality_score > 0])
                else:
                    avg_quality = 0.0
                
                # Tasks por status
                running_count = len(self.running_tasks)
                completed_count = len([t for t in self.recent_tasks if t.status == AgentStatus.COMPLETED])
                failed_count = len([t for t in self.recent_tasks if t.status == AgentStatus.FAILED])
                
                return {
                    "timestamp": datetime.now().isoformat(),
                    "agents": {
                        "total": total_agents,
                        "active": active_agents,
                        "idle": total_agents - active_agents
                    },
                    "tasks": {
                        "running": running_count,
                        "recent_completed": completed_count,
                        "recent_failed": failed_count,
                        "total_processed": total_tasks
                    },
                    "quality": {
                        "average_score": round(avg_quality, 2),
                        "threshold": 0.85  # Quality gate threshold
                    }
                }
    
    def _background_monitor(self):
        """Monitoramento contínuo em background"""
        while self.monitoring_active:
            try:
                # Coletar métricas a cada 5 segundos
                metrics = self.get_realtime_metrics()
                self.metrics_history.append(metrics)
                
                # Limitar histórico (últimas 1000 entradas)
                if len(self.metrics_history) > 1000:
                    self.metrics_history.pop(0)
                
                # Log de status geral
                if len(self.metrics_history) % 12 == 0:  # A cada 1 minuto
                    logger.info(f"📊 Status Geral: {metrics['agents']['active']}/{metrics['agents']['total']} agentes ativos, {metrics['tasks']['running']} tasks rodando")
                
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"❌ Erro no monitoramento: {e}")
                time.sleep(5)
    
    def get_performance_analytics(self, hours: int = 24) -> Dict[str, Any]:
        """Retorna análise de performance das últimas N horas"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tasks por squad
        cursor.execute("""
            SELECT squad, status, COUNT(*) as count
            FROM tasks t
            JOIN agents a ON t.agent_id = a.id
            WHERE t.created_at > ?
            GROUP BY squad, status
        """, (cutoff_time.isoformat(),))
        
        squad_performance = {}
        for row in cursor.fetchall():
            squad, status, count = row
            if squad not in squad_performance:
                squad_performance[squad] = {"completed": 0, "failed": 0, "total": 0}
            
            if status == AgentStatus.COMPLETED.value:
                squad_performance[squad]["completed"] += count
            elif status == AgentStatus.FAILED.value:
                squad_performance[squad]["failed"] += count
            squad_performance[squad]["total"] += count
        
        # Performance geral
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN status = ? THEN 1 END) as completed,
                COUNT(CASE WHEN status = ? THEN 1 END) as failed,
                AVG(quality_score) as avg_quality,
                AVG(execution_time_ms) as avg_time
            FROM tasks
            WHERE created_at > ? AND quality_score > 0
        """, (AgentStatus.COMPLETED.value, AgentStatus.FAILED.value, cutoff_time.isoformat()))
        
        row = cursor.fetchone()
        total_tasks = row[0] or 0
        completed_tasks = row[1] or 0
        failed_tasks = row[2] or 0
        avg_quality = row[3] or 0.0
        avg_time = row[4] or 0.0
        
        conn.close()
        
        return {
            "period_hours": hours,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": (completed_tasks / max(total_tasks, 1)) * 100,
            "average_quality": round(avg_quality, 2),
            "average_execution_time_ms": round(avg_time, 0),
            "squad_performance": squad_performance,
            "efficiency_score": self._calculate_efficiency_score(completed_tasks, failed_tasks, avg_quality, avg_time)
        }
    
    def _calculate_efficiency_score(self, completed: int, failed: int, avg_quality: float, avg_time: float) -> float:
        """Calcula score de eficiência baseado em múltiplos fatores"""
        # Fatores: taxa de sucesso (40%), qualidade (30%), velocidade (30%)
        success_rate = completed / max(completed + failed, 1)
        quality_factor = min(avg_quality / 0.85, 1.0)  # Normalizado para 85%
        speed_factor = min(3000 / max(avg_time, 1), 1.0)  # Ideal < 3s
        
        efficiency = (success_rate * 0.4) + (quality_factor * 0.3) + (speed_factor * 0.3)
        return round(efficiency * 100, 1)
    
    # ===== ALERTAS E NOTIFICAÇÕES =====
    
    def check_for_alerts(self) -> List[Dict[str, Any]]:
        """Verifica condições que requerem alertas"""
        alerts = []
        
        with self.agents_lock:
            with self.tasks_lock:
                # Alerta: muitos agentes inativos
                total_agents = len(self.agents)
                inactive_agents = len([a for a in self.agents.values() if a.status == AgentStatus.IDLE])
                
                if total_agents > 0 and inactive_agents > total_agents * 0.7:
                    alerts.append({
                        "type": "performance",
                        "severity": "warning",
                        "message": f"{inactive_agents}/{total_agents} agentes inativos - considerar redistribuição de workload",
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Alerta: taxa de falha alta nas últimas 100 tasks
                recent_tasks = self.recent_tasks[-100:]
                if len(recent_tasks) >= 50:  # Mínimo para análise
                    failed_recent = len([t for t in recent_tasks if t.status == AgentStatus.FAILED])
                    failure_rate = failed_recent / len(recent_tasks)
                    
                    if failure_rate > 0.2:  # >20% falha
                        alerts.append({
                            "type": "quality",
                            "severity": "critical",
                            "message": f"Taxa de falha alta: {failure_rate:.1%} nas últimas 100 tasks",
                            "timestamp": datetime.now().isoformat()
                        })
                
                # Alerta: qualidade média baixa
                if recent_tasks:
                    avg_quality = sum(t.quality_score for t in recent_tasks if t.quality_score > 0) / len([t for t in recent_tasks if t.quality_score > 0])
                    if avg_quality < 0.7:  # < 70%
                        alerts.append({
                            "type": "quality",
                            "severity": "warning",
                            "message": f"Qualidade média baixa: {avg_quality:.1%} - abaixo do threshold de 85%",
                            "timestamp": datetime.now().isoformat()
                        })
        
        return alerts
    
    def stop_monitoring(self):
        """Para o monitoramento em background"""
        self.monitoring_active = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        logger.info("🛑 Monitoramento de agentes finalizado")

# Instância global
_agent_monitor = None

def get_agent_monitor() -> AgentMonitor:
    """Singleton para Agent Monitor"""
    global _agent_monitor
    if _agent_monitor is None:
        _agent_monitor = AgentMonitor()
    return _agent_monitor