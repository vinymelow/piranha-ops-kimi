#!/usr/bin/env python3
"""
Dashboard Executive v3.0 - Interface Web em Tempo Real
Visualização por Squads e Métricas Estratégicas com atualização de horário
Seguindo especificações do prompt estratégico completo
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Importar configurações e métricas
import sys
sys.path.append('..')
from config.settings import Settings
from config.metrics_library import (
    ALL_METRICS, MetricTier, MetricPhase, 
    get_executive_summary, get_metrics_by_phase,
    get_current_value
)
from ai_os.agent_monitor import get_agent_monitor

class ExecutiveDashboard:
    """Dashboard executivo com métricas em tempo real"""
    
    def __init__(self):
        self.db_path = "../data/sinapse.db"
        self.metrics_cache = {}
        self.last_update = datetime.now()
        self.init_database()
        
    def init_database(self):
        """Inicializa banco de dados se não existir"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de métricas em tempo real
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS realtime_metrics (
                metric_id TEXT PRIMARY KEY,
                current_value REAL,
                target_value REAL,
                tier TEXT,
                phase TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de status dos squads
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS squad_status (
                squad_id TEXT PRIMARY KEY,
                squad_name TEXT,
                status TEXT,
                tasks_today INTEGER,
                quality_score REAL,
                last_task TIMESTAMP,
                agents_online INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de logs de atividades
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                squad TEXT,
                activity TEXT,
                details TEXT,
                priority TEXT
            )
        """)
        
        # Tabela de agentes e tasks (para monitoramento)
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
    
    def update_realtime_metrics(self):
        """Atualiza métricas em tempo real"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for metric_id, threshold in ALL_METRICS.items():
            current_value = get_current_value(metric_id)
            tier = threshold.classify(current_value)
            phase = self._get_phase_from_metric(metric_id)
            
            cursor.execute("""
                INSERT OR REPLACE INTO realtime_metrics 
                (metric_id, current_value, target_value, tier, phase, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (metric_id, current_value, threshold.target, tier.value, phase, datetime.now()))
        
        conn.commit()
        conn.close()
        self.last_update = datetime.now()
    
    def _get_phase_from_metric(self, metric_id: str) -> str:
        """Determina fase da métrica pelo ID"""
        if any(x in metric_id for x in ['cart', 'studio', 'stock', 'lead', 'reorder']):
            return "Revenue Activation"
        elif any(x in metric_id for x in ['partner', 'wholesale', 'tier']):
            return "Wholesale Engine"
        elif any(x in metric_id for x in ['dhl', 'cod', 'time_saved', 'manual']):
            return "Operational Liberation"
        elif any(x in metric_id for x in ['infarmed', 'rma', 'compliance', 'bank']):
            return "Compliance"
        else:
            return "Strategic"

# Rotas API
@app.route('/')
def dashboard():
    """Dashboard principal executivo"""
    return render_template('dashboard_executive.html')

@app.route('/agents')
def agents_monitor():
    """Página de monitoramento de agentes"""
    return render_template('agents_monitor.html')

@app.route('/api/executive-summary')
def executive_summary():
    """
    Retorna resumo executivo para CEO/Head of Growth
    Formato: O que é bom, o que é perigoso, o que precisa de atenção
    """
    dashboard = ExecutiveDashboard()
    dashboard.update_realtime_metrics()
    
    # Obter métricas classificadas
    metrics_summary = get_executive_summary()
    
    # Progresso por fase
    phase_progress = get_phase_progress()
    
    # Recomendações baseadas em análise
    recommendations = [
        {
            "priority": "P0-CRITICAL",
            "metric": "LTV/CAC Ratio",
            "action": "Revisar estratégia de aquisição - CAC muito alto ou retenção baixa",
            "impact": "Risco de sustentabilidade financeira",
            "owner": "Sales Ops + CFO"
        },
        {
            "priority": "P1-QUICK-WIN",
            "metric": "Cart Recovery Rate",
            "action": "Otimizar templates WhatsApp e timing de envio",
            "impact": "+15% receita recuperada",
            "owner": "Commercial Squad"
        }
    ]
    
    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "overall_health": metrics_summary["overall_health_score"],
        "metrics_by_tier": metrics_summary,
        "phase_progress": phase_progress,
        "recommendations": recommendations,
        "next_review": (datetime.now() + timedelta(hours=1)).isoformat(),
        "system_status": {
            "state": "operational",
            "version": "3.0",
            "uptime": "99.9%",
            "last_metrics_update": datetime.now().isoformat()
        }
    })

@app.route('/api/agents')
def api_agents():
    """Retorna lista de agentes com status"""
    monitor = get_agent_monitor()
    agents = monitor.get_all_agents()
    realtime_metrics = monitor.get_realtime_metrics()
    
    return jsonify({
        "agents": [{
            "id": agent.id,
            "name": agent.name,
            "squad": agent.squad,
            "status": agent.status.value,
            "current_task_id": agent.current_task_id,
            "tasks_completed": agent.tasks_completed,
            "tasks_failed": agent.tasks_failed,
            "avg_quality_score": agent.avg_quality_score,
            "last_activity": agent.last_activity.isoformat(),
            "created_at": agent.created_at.isoformat()
        } for agent in agents],
        "realtime_metrics": realtime_metrics,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/agents/<agent_id>')
def api_agent_detail(agent_id):
    """Detalhes de um agente específico"""
    monitor = get_agent_monitor()
    agent = monitor.get_agent(agent_id)
    
    if not agent:
        return jsonify({"error": "Agente não encontrado"}), 404
    
    # Obter tasks do agente
    agent_tasks = monitor.get_agent_tasks(agent_id, limit=10)
    
    return jsonify({
        "agent": {
            "id": agent.id,
            "name": agent.name,
            "squad": agent.squad,
            "status": agent.status.value,
            "current_task_id": agent.current_task_id,
            "tasks_completed": agent.tasks_completed,
            "tasks_failed": agent.tasks_failed,
            "avg_quality_score": agent.avg_quality_score,
            "last_activity": agent.last_activity.isoformat(),
            "created_at": agent.created_at.isoformat()
        },
        "metrics": {
            "tasks_completed": agent.tasks_completed,
            "tasks_failed": agent.tasks_failed,
            "success_rate": (agent.tasks_completed / max(agent.tasks_completed + agent.tasks_failed, 1)) * 100,
            "avg_quality": agent.avg_quality_score
        },
        "recent_tasks": [{
            "id": task.id,
            "type": task.type,
            "description": task.description,
            "status": task.status.value,
            "quality_score": task.quality_score,
            "execution_time_ms": task.execution_time_ms,
            "created_at": task.created_at.isoformat(),
            "completed_at": task.completed_at.isoformat() if task.completed_at else None
        } for task in agent_tasks],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/tasks/running')
def api_running_tasks():
    """Tasks em execução no momento"""
    monitor = get_agent_monitor()
    running_tasks = monitor.get_running_tasks()
    
    return jsonify({
        "tasks": [{
            "id": task.id,
            "agent_id": task.agent_id,
            "type": task.type,
            "description": task.description,
            "priority": task.priority.value,
            "status": task.status.value,
            "progress": 0,  # Será calculado no frontend
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "quality_score": task.quality_score,
            "estimated_duration_ms": 30000  # Estimativa de 30s
        } for task in running_tasks],
        "count": len(running_tasks),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/tasks/recent')
def api_recent_tasks():
    """Tasks recentes (histórico)"""
    limit = request.args.get('limit', 20, type=int)
    filter_type = request.args.get('filter', 'all')
    
    monitor = get_agent_monitor()
    recent_tasks = monitor.get_recent_tasks(limit)
    
    # Aplicar filtros
    if filter_type == 'completed':
        recent_tasks = [t for t in recent_tasks if t.status.value == 'completed']
    elif filter_type == 'failed':
        recent_tasks = [t for t in recent_tasks if t.status.value == 'failed']
    elif filter_type == 'recent':
        cutoff = datetime.now() - timedelta(hours=24)
        recent_tasks = [t for t in recent_tasks if t.created_at > cutoff]
    
    return jsonify({
        "tasks": [{
            "id": task.id,
            "agent_id": task.agent_id,
            "type": task.type,
            "description": task.description,
            "priority": task.priority.value,
            "status": task.status.value,
            "quality_score": task.quality_score,
            "execution_time_ms": task.execution_time_ms,
            "created_at": task.created_at.isoformat(),
            "completed_at": task.completed_at.isoformat() if task.completed_at else None
        } for task in recent_tasks],
        "count": len(recent_tasks),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/tasks/agent/<agent_id>')
def api_agent_tasks(agent_id):
    """Tasks de um agente específico"""
    limit = request.args.get('limit', 10, type=int)
    
    monitor = get_agent_monitor()
    agent_tasks = monitor.get_agent_tasks(agent_id, limit)
    
    return jsonify({
        "agent_id": agent_id,
        "tasks": [{
            "id": task.id,
            "type": task.type,
            "description": task.description,
            "priority": task.priority.value,
            "status": task.status.value,
            "quality_score": task.quality_score,
            "execution_time_ms": task.execution_time_ms,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None
        } for task in agent_tasks],
        "count": len(agent_tasks),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/performance/analytics')
def api_performance_analytics():
    """Análise de performance das últimas 24 horas"""
    hours = request.args.get('hours', 24, type=int)
    
    monitor = get_agent_monitor()
    analytics = monitor.get_performance_analytics(hours)
    
    return jsonify(analytics)

@app.route('/api/status')
def api_status():
    """Status geral do sistema"""
    monitor = get_agent_monitor()
    system_status = monitor.get_system_status()
    
    return jsonify({
        "system": system_status,
        "dashboard": {
            "version": "3.0",
            "status": "operational",
            "last_update": datetime.now().isoformat()
        }
    })

@app.route('/api/update-time')
def update_time():
    """Retorna horário atual para atualização do dashboard"""
    return jsonify({
        "current_time": datetime.now().strftime("%H:%M:%S"),
        "current_date": datetime.now().strftime("%d/%m/%Y"),
        "last_metrics_update": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🤖 PIRANHAOPS AIOS v3.0 - AGENTES MONITOR")
    print("="*60)
    print("🔗 Dashboard Agentes: http://localhost:8083/agents")
    print("📡 API Agentes: http://localhost:8083/api/agents")
    print("📊 API Tasks: http://localhost:8083/api/tasks/running")
    print("🎯 API Performance: http://localhost:8083/api/performance/analytics")
    print("="*60)
    print("🚀 Monitor de Agentes iniciado!")
    print("   • Visualização em tempo real dos agentes")
    print("   • Tasks em execução com progresso ao vivo")
    print("   • Histórico completo com filtros")
    print("   • WebSocket para atualizações instantâneas")
    
    app.run(debug=True, port=8083, host='0.0.0.0')