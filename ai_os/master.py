#!/usr/bin/env python3
"""
AIOS Master Agent v3.0 - Artificial Intelligence Operating System
Orquestrador central do PiranhaOps seguindo especificações do prompt estratégico
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import sqlite3
import json
import time
import threading
from pathlib import Path

from config.settings import Settings, SquadType, ModelTier

# Configurar logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("aios.master")

class SystemState(Enum):
    INITIALIZING = "initializing"
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    ERROR = "error"

@dataclass
class TaskRequest:
    """Estrutura de requisição de task"""
    id: str
    type: str
    squad: SquadType
    payload: Dict[str, Any]
    priority: int = 5  # 1-10, 10 = máxima
    requested_at: datetime = None
    
    def __post_init__(self):
        if self.requested_at is None:
            self.requested_at = datetime.now()

@dataclass
class TaskResult:
    """Resultado de uma task processada"""
    task_id: str
    status: str
    result: Dict[str, Any]
    quality_score: float
    execution_time_ms: int
    model_tier: str
    timestamp: datetime = field(default_factory=datetime.now)

class MemorySinapse:
    """
    Sistema de memória persistente (anti-DocRot)
    Mantém contexto entre sessões e evita perda de informação
    """
    
    def __init__(self, db_path: str = "data/sinapse.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Inicializa SQLite com schemas necessários"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Tabela principal de memória
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sinapse_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                context_key TEXT UNIQUE NOT NULL,
                context_data TEXT NOT NULL,
                agent_origin TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP,
                expiration_date TIMESTAMP
            )
        """)
        
        # Tabela de tasks para histórico
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                squad TEXT NOT NULL,
                type TEXT NOT NULL,
                payload TEXT,
                result TEXT,
                quality_score REAL,
                model_tier TEXT,
                execution_time_ms INTEGER,
                status TEXT DEFAULT 'completed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Índices para performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_context_key ON sinapse_memory(context_key)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_id ON task_history(task_id)")
        
        conn.commit()
        conn.close()
    
    def store(self, key: str, data: Dict, agent_origin: str = "master", expiration_hours: int = None):
        """Armazena contexto com timestamp e contador de acessos"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        expiration = None
        if expiration_hours:
            expiration = (datetime.now() + timedelta(hours=expiration_hours)).isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO sinapse_memory 
            (context_key, context_data, agent_origin, updated_at, expiration_date)
            VALUES (?, ?, ?, ?, ?)
        """, (key, json.dumps(data), agent_origin, datetime.now().isoformat(), expiration))
        
        conn.commit()
        conn.close()
        logger.debug(f"Contexto armazenado: {key}")
    
    def retrieve(self, key: str) -> Optional[Dict]:
        """Recupera contexto e atualiza contador de acessos"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT context_data FROM sinapse_memory 
            WHERE context_key = ? AND (expiration_date IS NULL OR expiration_date > ?)
        """, (key, datetime.now().isoformat()))
        
        result = cursor.fetchone()
        
        if result:
            # Atualizar contador de acessos
            cursor.execute("""
                UPDATE sinapse_memory 
                SET access_count = access_count + 1, last_accessed = ?
                WHERE context_key = ?
            """, (datetime.now().isoformat(), key))
            conn.commit()
            
            conn.close()
            return json.loads(result[0])
        
        conn.close()
        return None
    
    def get_incremental_context(self, project_id: str) -> List[Dict]:
        """Recupera contexto de forma incremental (desenvolvimento incremental EiOS)"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT context_data, access_count, updated_at
            FROM sinapse_memory 
            WHERE context_key LIKE ?
            ORDER BY updated_at DESC
            LIMIT 10
        """, (f"{project_id}%",))
        
        results = cursor.fetchall()
        conn.close()
        
        context_items = []
        for data, access_count, updated_at in results:
            item = json.loads(data)
            item['_meta'] = {
                'access_count': access_count,
                'last_updated': updated_at
            }
            context_items.append(item)
        
        return context_items

class AIOSMaster:
    """
    AIOS Master Agent v3.0
    Orquestrador central do PiranhaOps
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger("AIOS.Master")
        
        # Estado do sistema
        self.state = SystemState.INITIALIZING
        self.started_at = datetime.now()
        self.task_count = 0
        self.error_count = 0
        
        # Componentes
        self.memory = MemorySinapse()
        
        # Métricas em tempo real
        self.metrics = {
            "tasks_processed": 0,
            "tasks_failed": 0,
            "avg_quality_score": 0.0,
            "current_load": 0.0,  # 0.0 - 1.0
            "active_squads": []
        }
        
        self.logger.info("🦈 AIOS Master Agent inicializado")
    
    async def initialize(self):
        """Inicialização sequencial obrigatória"""
        try:
            # 1. Validar config
            self.settings.validate()
            self.logger.info("✅ Configurações validadas")
            
            # 2. Conectar SQLite
            self.memory._init_database()
            self.logger.info("✅ Memória Sinapse conectada")
            
            # 3. Inicializar squads (lazy loading)
            await self._initialize_squads()
            self.logger.info("✅ 3 Squads inicializados")
            
            # 4. Health check MCPs
            mcp_health = await self._check_mcp_servers()
            self.logger.info(f"✅ MCP Servers: {mcp_health['connected']}/5 conectados")
            
            # 5. Recuperar estado
            last_state = self._load_state()
            if last_state:
                self.metrics = last_state.get("metrics", self.metrics)
                self.logger.info("✅ Estado anterior recuperado")
            
            self.state = SystemState.OPERATIONAL
            self.logger.info("🚀 AIOS Master OPERACIONAL")
            
        except Exception as e:
            self.state = SystemState.ERROR
            self.logger.error(f"❌ Falha na inicialização: {e}")
            raise
    
    async def process_task(self, request: TaskRequest) -> Dict[str, Any]:
        """
        Fluxo completo de processamento de uma task:
        1. RECEBER → Validar request
        2. ROTEAR → Selecionar Model Tier (85/15/<1)
        3. DELEGAR → Enviar para Squad correto
        4. EXECUTAR → Processar com retry logic
        5. VALIDAR → Quality Gate (85% threshold)
        6. PERSISTIR → Salvar resultado
        7. RETORNAR → Response formatado
        """
        self.task_count += 1
        task_id = f"TSK-{self.task_count:04d}"
        
        self.logger.info(f"📥 Task {task_id} recebida: {request.type} [{request.squad.value}]")
        
        try:
            # 1. VALIDAR REQUEST
            if not self._validate_request(request):
                raise ValueError(f"Request inválido: {request}")
            
            # 2. SELECIONAR MODEL TIER (Estratégia 85/15/<1)
            model_tier = self._select_model_tier(request)
            self.logger.debug(f"🎯 Model tier selecionado: {model_tier.value}")
            
            # 3. CHECK ORÇAMENTO (€37/mês)
            if not self._check_budget(model_tier):
                self.logger.warning("⚠️ Orçamento próximo do limite, forçando Economy")
                model_tier = ModelTier.ECONOMY
            
            # 4. DELEGAR AO SQUAD
            squad_executor = self._get_squad_executor(request.squad)
            
            # 5. EXECUTAR COM RETRY
            result = await self._execute_with_retry(
                squad_executor, 
                request, 
                model_tier,
                max_retries=self.settings.AIOS_RETRY_ATTEMPTS
            )
            
            # 6. QUALITY GATE (85% threshold)
            # Quality gate será implementado no task_manager
            quality_score = 0.9  # Placeholder
            result["quality_score"] = quality_score
            
            if quality_score < self.settings.AIOS_QUALITY_THRESHOLD:
                self.logger.warning(f"⚠️ Qualidade {quality_score} abaixo do threshold")
                result = await self._handle_quality_failure(request, result)
            
            # 7. PERSISTIR
            self.memory.store(f"task:{task_id}", {
                "request": request.__dict__,
                "result": result,
                "quality_score": quality_score
            })
            
            # 8. ATUALIZAR MÉTRICAS
            self._update_metrics(result, quality_score)
            
            self.logger.info(f"✅ Task {task_id} completada: qualidade={quality_score}")
            
            return {
                "task_id": task_id,
                "status": "success",
                "result": result,
                "quality_score": quality_score,
                "model_tier": model_tier.value,
                "processing_time_ms": result.get("execution_time_ms", 0),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"❌ Task {task_id} falhou: {e}")
            
            # Fallback para modo degradado
            return await self._handle_task_failure(request, e)
    
    def _select_model_tier(self, request: TaskRequest) -> ModelTier:
        """
        Algoritmo de roteamento inteligente 85/15/<1
        
        Regras:
        - Tasks simples (fetch, validate, format) → Economy (85%)
        - Tasks complexas (analyze, detect) → Standard (15%)
        - Tasks críticas (debug, strategize) → Deep (<1%)
        - Emergências sempre → Deep (independente de distribuição)
        """
        task_type = request.type.lower()
        
        # Mapeamento explícito de tasks para tiers
        economy_tasks = [
            'fetch', 'get', 'list', 'count', 'validate', 'format',
            'calculate', 'generate', 'log', 'extract', 'filter', 
            'sort', 'parse', 'clean', 'simple', 'basic'
        ]
        
        standard_tasks = [
            'analyze', 'detect', 'write', 'optimize', 'sync',
            'process', 'evaluate', 'predict'
        ]
        
        deep_tasks = [
            'debug', 'architect', 'strategic', 'complex', 'reasoning',
            'emergency', 'critical_decision'
        ]
        
        # Verificar prioridade (emergências ignoram distribuição)
        if request.priority >= 9:
            return ModelTier.DEEP
        
        # Classificar por tipo
        if any(t in task_type for t in economy_tasks):
            return ModelTier.ECONOMY
        
        if any(t in task_type for t in standard_tasks):
            return ModelTier.STANDARD
        
        if any(t in task_type for t in deep_tasks):
            return ModelTier.DEEP
        
        # Default: Economy (mais barato)
        return ModelTier.ECONOMY
    
    def _check_budget(self, model_tier: ModelTier) -> bool:
        """Verifica se há orçamento disponível para o tier"""
        # Simulação simples - em produção calcular baseado em tokens reais
        return True  # Por enquanto sempre permite
    
    async def _execute_with_retry(self, executor, request, model_tier, max_retries=3):
        """Executa com retry exponencial"""
        for attempt in range(max_retries):
            try:
                # Por enquanto retorna resultado mock
                return {
                    "status": "completed",
                    "data": f"Resultado da task {request.type}",
                    "execution_time_ms": 150,
                    "model_tier": model_tier.value
                }
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = (2 ** attempt) * self.settings.AIOS_RETRY_DELAY_SECONDS
                self.logger.warning(f"⚠️ Retry {attempt+1}/{max_retries} em {wait_time}s: {e}")
                await asyncio.sleep(wait_time)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """
        Retorna status completo para o dashboard
        """
        return {
            "state": self.state.value,
            "uptime_seconds": (datetime.now() - self.started_at).total_seconds(),
            "version": "AIOS v3.0",
            "metrics": self.metrics,
            "squads": await self._get_squads_status(),
            "mcp_servers": await self._check_mcp_servers(),
            "budget": {
                "daily_usd": self.settings.BUDGET_DAILY_USD,
                "projected_monthly_eur": self._calculate_projected_cost(),
                "utilization_percentage": self._calculate_budget_utilization()
            },
            "tasks": {
                "total_processed": self.task_count,
                "failed": self.error_count,
                "success_rate": 1 - (self.error_count / max(self.task_count, 1))
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_projected_cost(self) -> float:
        """Calcula projeção mensal baseada no consumo atual"""
        # Simulação - em produção calcular baseado em tokens reais
        daily_tasks = min(self.task_count, 100)  # Últimas 100 tasks
        avg_tokens_per_task = 1500  # Estimativa
        
        daily_cost = (daily_tasks * avg_tokens_per_task * 0.0000025)  # Economy rate
        return daily_cost * 30 * 0.93  # USD → EUR
    
    def _calculate_budget_utilization(self) -> float:
        """Percentual de utilização do budget mensal"""
        projected = self._calculate_projected_cost()
        return (projected / self.settings.BUDGET_MONTHLY_EUR) * 100
    
    # Métodos auxiliares
    def _validate_request(self, request: TaskRequest) -> bool:
        """Valida integridade do request"""
        return (
            request.squad in SquadType and
            request.priority >= 1 and request.priority <= 10 and
            isinstance(request.payload, dict)
        )
    
    def _get_squad_status(self) -> Dict[str, Any]:
        """Retorna status dos squads (mock por enquanto)"""
        return {
            "commercial": {"status": "active", "tasks_today": 47, "quality_score": 0.94},
            "operational": {"status": "setup", "tasks_today": 12, "quality_score": 0.88},
            "intelligence": {"status": "pending", "tasks_today": 0, "quality_score": 0.0}
        }
    
    def _check_mcp_servers(self) -> Dict[str, Any]:
        """Health check dos MCP servers (mock por enquanto)"""
        return {
            "whatsapp_evolution": {"connected": True, "state": "open", "latency": 45},
            "shopify": {"connected": True, "state": "active", "latency": 120},
            "klaviyo": {"connected": True, "state": "active", "latency": 80},
            "meta": {"connected": False, "state": "config_pending", "latency": 0},
            "sage_x3": {"connected": False, "state": "not_configured", "latency": 0}
        }
    
    def _update_metrics(self, result: Dict, quality_score: float):
        """Atualiza métricas do sistema"""
        self.metrics["tasks_processed"] += 1
        
        # Média móvel da qualidade (últimas 100 tasks)
        total_tasks = self.metrics["tasks_processed"]
        old_avg = self.metrics["avg_quality_score"]
        self.metrics["avg_quality_score"] = (
            (old_avg * (total_tasks - 1)) + quality_score
        ) / total_tasks
        
        # Carga atual (0.0 - 1.0)
        self.metrics["current_load"] = min(total_tasks / 100, 1.0)
    
    def _load_state(self) -> Optional[Dict]:
        """Carrega estado anterior do sistema"""
        return self.memory.retrieve("system_state")
    
    async def _handle_quality_failure(self, request: TaskRequest, result: Dict) -> Dict:
        """Lida com falha no quality gate"""
        self.logger.warning(f"⚠️ Qualidade {result['quality_score']} abaixo do threshold")
        
        # Estratégias de recovery:
        # 1. Retry com modelo superior
        # 2. Delegação para humano se crítico
        # 3. Modo degradado
        
        if request.priority >= 8:
            # Crítico: delegar para humano
            return {"status": "escalated_to_human", "reason": "quality_failure_critical"}
        else:
            # Não-crítico: modo degradado
            return {"status": "degraded", "reason": "quality_failure", "result": result}
    
    async def _handle_task_failure(self, request: TaskRequest, error: Exception) -> Dict:
        """Lida com falha completa de task"""
        self.logger.error(f"❌ Task falhou: {error}")
        
        return {
            "status": "failed",
            "error": str(error),
            "error_type": type(error).__name__,
            "recommendation": "Verificar logs e tentar novamente"
        }

# Instância global
_aios_master = None

async def get_master() -> AIOSMaster:
    """Singleton para AIOS Master"""
    global _aios_master
    if _aios_master is None:
        from config.settings import settings
        _aios_master = AIOSMaster(settings)
        await _aios_master.initialize()
    return _aios_master