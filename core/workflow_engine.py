"""
Workflow Engine - Motor de orquestração de processos multi-squad
Gerencia workflows cross-squad com execução coordenada e monitoramento
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any, Union
from enum import Enum
import traceback

# Configuração de logging
logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Status possíveis de um workflow"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class WorkflowStep:
    """Representa um passo individual em um workflow"""
    name: str
    squad: str  # inventory, whatsapp, traffic, lead_scraper, google_ads
    action: str  # Nome da ação a ser executada
    condition: Optional[str] = None  # Expressão lambda para condição
    delay_seconds: int = 0  # Delay antes da execução
    retry_on_failure: int = 0  # Número de retries em caso de falha
    depends_on: List[str] = field(default_factory=list)  # Steps dependentes
    
    def __post_init__(self):
        if isinstance(self.depends_on, str):
            self.depends_on = [self.depends_on]


@dataclass
class WorkflowExecution:
    """Registra a execução de um workflow"""
    workflow_name: str
    execution_id: str
    status: WorkflowStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    steps_executed: List[Dict[str, Any]] = field(default_factory=list)
    error_message: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StepExecution:
    """Registra a execução de um step individual"""
    step_name: str
    execution_id: str
    status: WorkflowStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    result: Any = None


class WorkflowEngine:
    """
    Motor de orquestração de workflows multi-squad
    Coordena a execução de processos complexos entre diferentes squads
    """
    
    def __init__(self, model_router, data_store):
        self.model_router = model_router
        self.data_store = data_store
        self.workflows: Dict[str, List[WorkflowStep]] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.step_executions: Dict[str, StepExecution] = {}
        self.running_workflows: Dict[str, asyncio.Task] = {}
        
        # Registrar workflows padrão
        self._register_default_workflows()
        
        logger.info("WorkflowEngine inicializado")
    
    def _register_default_workflows(self):
        """Registra os workflows padrão da Fase 1"""
        
        # Workflow 1: Recuperação de carrinho abandonado
        abandoned_cart_workflow = [
            WorkflowStep(
                name="check_inventory",
                squad="inventory",
                action="check_stock",
                condition="lambda context: len(context.get('abandoned_items', [])) > 0",
                retry_on_failure=2
            ),
            WorkflowStep(
                name="send_whatsapp_reminder",
                squad="whatsapp",
                action="send_abandoned_cart_message",
                depends_on=["check_inventory"],
                delay_seconds=300,  # 5 minutos
                retry_on_failure=3
            ),
            WorkflowStep(
                name="create_google_ads_audience",
                squad="google_ads",
                action="create_cart_abandoner_audience",
                depends_on=["send_whatsapp_reminder"],
                delay_seconds=3600  # 1 hora
            ),
            WorkflowStep(
                name="launch_retargeting_campaign",
                squad="traffic",
                action="launch_cart_recovery_campaign",
                depends_on=["create_google_ads_audience"],
                condition="lambda context: context.get('inventory_available', False)",
                retry_on_failure=2
            )
        ]
        
        # Workflow 2: Emergência de estoque
        stock_emergency_workflow = [
            WorkflowStep(
                name="analyze_stock_situation",
                squad="inventory",
                action="analyze_critical_stock",
                condition="lambda context: context.get('stock_level', 0) < context.get('min_threshold', 10)",
                retry_on_failure=2
            ),
            WorkflowStep(
                name="pause_google_ads",
                squad="google_ads",
                action="pause_product_campaigns",
                depends_on=["analyze_stock_situation"],
                condition="lambda context: context.get('critical_stock', False)",
                retry_on_failure=3
            ),
            WorkflowStep(
                name="notify_lead_scraper",
                squad="lead_scraper",
                action="prioritize_supplier_contacts",
                depends_on=["analyze_stock_situation"],
                delay_seconds=60  # 1 minuto
            ),
            WorkflowStep(
                name="send_whatsapp_alert",
                squad="whatsapp",
                action="send_stock_alert",
                depends_on=["notify_lead_scraper"],
                condition="lambda context: context.get('supplier_contacted', False)",
                delay_seconds=1800  # 30 minutos
            )
        ]
        
        # Workflow 3: Nutrição de novo lead
        new_lead_nurture_workflow = [
            WorkflowStep(
                name="qualify_lead",
                squad="lead_scraper",
                action="qualify_new_lead",
                condition="lambda context: context.get('lead_data') is not None",
                retry_on_failure=2
            ),
            WorkflowStep(
                name="send_welcome_whatsapp",
                squad="whatsapp",
                action="send_welcome_message",
                depends_on=["qualify_lead"],
                condition="lambda context: context.get('lead_qualified', False)",
                delay_seconds=60  # 1 minuto
            ),
            WorkflowStep(
                name="create_lead_audience",
                squad="google_ads",
                action="create_lead_audience",
                depends_on=["qualify_lead"],
                delay_seconds=300  # 5 minutos
            ),
            WorkflowStep(
                name="launch_lead_nurture_campaign",
                squad="traffic",
                action="launch_lead_nurture_campaign",
                depends_on=["create_lead_audience", "send_welcome_whatsapp"],
                condition="lambda context: context.get('welcome_sent', False)",
                delay_seconds=86400  # 24 horas
            ),
            WorkflowStep(
                name="schedule_followup",
                squad="whatsapp",
                action="schedule_followup_message",
                depends_on=["launch_lead_nurture_campaign"],
                delay_seconds=172800,  # 48 horas
                retry_on_failure=3
            )
        ]
        
        # Registrar workflows
        self.register_workflow("abandoned_cart_recovery", abandoned_cart_workflow)
        self.register_workflow("stock_emergency", stock_emergency_workflow)
        self.register_workflow("new_lead_nurture", new_lead_nurture_workflow)
        
        logger.info("Workflows padrão registrados com sucesso")
    
    def register_workflow(self, name: str, steps: List[WorkflowStep]):
        """
        Registra um novo workflow
        
        Args:
            name: Nome do workflow
            steps: Lista de steps do workflow
        """
        self.workflows[name] = steps
        logger.info(f"Workflow '{name}' registrado com {len(steps)} steps")
    
    async def trigger(self, workflow_name: str, context: Dict[str, Any] = None) -> str:
        """
        Dispara a execução de um workflow
        
        Args:
            workflow_name: Nome do workflow a executar
            context: Contexto inicial para o workflow
            
        Returns:
            ID da execução
            
        Raises:
            ValueError: Se o workflow não existir
        """
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow '{workflow_name}' não encontrado")
        
        execution_id = f"{workflow_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Criar registro de execução
        execution = WorkflowExecution(
            workflow_name=workflow_name,
            execution_id=execution_id,
            status=WorkflowStatus.PENDING,
            started_at=datetime.now(),
            context=context or {}
        )
        
        self.executions[execution_id] = execution
        
        # Iniciar execução assíncrona
        task = asyncio.create_task(self._execute_workflow(workflow_name, execution_id))
        self.running_workflows[execution_id] = task
        
        logger.info(f"Workflow '{workflow_name}' iniciado com execution_id: {execution_id}")
        
        return execution_id
    
    async def _execute_workflow(self, workflow_name: str, execution_id: str):
        """
        Executa um workflow completo
        
        Args:
            workflow_name: Nome do workflow
            execution_id: ID da execução
        """
        execution = self.executions[execution_id]
        steps = self.workflows[workflow_name]
        
        try:
            execution.status = WorkflowStatus.RUNNING
            logger.info(f"Iniciando execução do workflow '{workflow_name}' (ID: {execution_id})")
            
            # Executar steps
            for step in steps:
                # Verificar dependências
                if not await self._check_dependencies(step, execution):
                    logger.warning(f"Dependências não satisfeitas para step '{step.name}'")
                    continue
                
                # Verificar condição
                if not self._evaluate_condition(step.condition, execution.context):
                    logger.info(f"Condição não satisfeita para step '{step.name}', pulando...")
                    continue
                
                # Aguardar delay se necessário
                if step.delay_seconds > 0:
                    logger.info(f"Aguardando {step.delay_seconds} segundos antes de executar '{step.name}'")
                    await asyncio.sleep(step.delay_seconds)
                
                # Executar step
                step_result = await self._execute_step(step, execution_id, execution.context)
                
                # Registrar execução do step
                execution.steps_executed.append({
                    'step_name': step.name,
                    'status': step_result.status.value,
                    'started_at': step_result.started_at.isoformat(),
                    'completed_at': step_result.completed_at.isoformat() if step_result.completed_at else None,
                    'error_message': step_result.error_message,
                    'retry_count': step_result.retry_count
                })
                
                # Atualizar contexto com resultado
                if step_result.result:
                    execution.context[f"{step.name}_result"] = step_result.result
                
                # Verificar se o step falhou
                if step_result.status == WorkflowStatus.FAILED:
                    execution.status = WorkflowStatus.FAILED
                    execution.error_message = f"Step '{step.name}' falhou: {step_result.error_message}"
                    logger.error(f"Workflow '{workflow_name}' falhou no step '{step.name}': {step_result.error_message}")
                    break
            
            # Finalizar execução
            if execution.status != WorkflowStatus.FAILED:
                execution.status = WorkflowStatus.COMPLETED
                execution.completed_at = datetime.now()
                logger.info(f"Workflow '{workflow_name}' (ID: {execution_id}) concluído com sucesso")
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.now()
            logger.error(f"Erro na execução do workflow '{workflow_name}' (ID: {execution_id}): {e}")
            logger.error(traceback.format_exc())
        
        finally:
            # Limpar task do dicionário
            if execution_id in self.running_workflows:
                del self.running_workflows[execution_id]
    
    async def _check_dependencies(self, step: WorkflowStep, execution: WorkflowExecution) -> bool:
        """
        Verifica se as dependências de um step foram satisfeitas
        
        Args:
            step: Step a verificar
            execution: Execução atual do workflow
            
        Returns:
            True se todas as dependências foram satisfeitas
        """
        if not step.depends_on:
            return True
        
        for dep_name in step.depends_on:
            # Verificar se o step dependente foi executado com sucesso
            dep_executed = False
            for step_exec in execution.steps_executed:
                if step_exec['step_name'] == dep_name and step_exec['status'] == 'completed':
                    dep_executed = True
                    break
            
            if not dep_executed:
                return False
        
        return True
    
    def _evaluate_condition(self, condition: Optional[str], context: Dict[str, Any]) -> bool:
        """
        Avalia uma condição lambda
        
        Args:
            condition: Expressão lambda como string
            context: Contexto para avaliação
            
        Returns:
            True se a condição for satisfeita ou não existir
        """
        if not condition:
            return True
        
        try:
            # Avaliar expressão lambda
            func = eval(condition)
            return func(context)
        except Exception as e:
            logger.error(f"Erro ao avaliar condição '{condition}': {e}")
            return False
    
    async def _execute_step(self, step: WorkflowStep, execution_id: str, context: Dict[str, Any]) -> StepExecution:
        """
        Executa um step individual
        
        Args:
            step: Step a executar
            execution_id: ID da execução do workflow
            context: Contexto de execução
            
        Returns:
            Resultado da execução do step
        """
        step_execution_id = f"{execution_id}_{step.name}"
        
        step_execution = StepExecution(
            step_name=step.name,
            execution_id=step_execution_id,
            status=WorkflowStatus.RUNNING,
            started_at=datetime.now()
        )
        
        self.step_executions[step_execution_id] = step_execution
        
        try:
            logger.info(f"Executando step '{step.name}' do squad '{step.squad}'")
            
            # Preparar argumentos para a ação
            args = self._prepare_args(step.action, context)
            
            # Executar ação através do model router
            result = await self.model_router.execute_squad_action(
                squad=step.squad,
                action=step.action,
                **args
            )
            
            # Atualizar execução do step
            step_execution.status = WorkflowStatus.COMPLETED
            step_execution.completed_at = datetime.now()
            step_execution.result = result
            
            logger.info(f"Step '{step.name}' executado com sucesso")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Erro na execução do step '{step.name}': {error_msg}")
            
            # Tentar retry se configurado
            if step.retry_on_failure > 0 and step_execution.retry_count < step.retry_on_failure:
                step_execution.retry_count += 1
                step_execution.status = WorkflowStatus.RETRYING
                
                logger.info(f"Tentando retry {step_execution.retry_count}/{step.retry_on_failure} do step '{step.name}'")
                
                # Aguardar antes do retry (exponencial backoff)
                await asyncio.sleep(2 ** step_execution.retry_count)
                
                # Recursivamente tentar executar novamente
                return await self._execute_step(step, execution_id, context)
            
            # Falha definitiva
            step_execution.status = WorkflowStatus.FAILED
            step_execution.completed_at = datetime.now()
            step_execution.error_message = error_msg
        
        return step_execution
    
    def _prepare_args(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepara os argumentos para uma ação baseado no contexto
        
        Args:
            action: Nome da ação
            context: Contexto de execução
            
        Returns:
            Dicionário de argumentos
        """
        args = {}
        
        # Mapear ações para seus argumentos esperados
        action_args_map = {
            'check_stock': {
                'items': lambda ctx: ctx.get('abandoned_items', []),
                'context': lambda ctx: ctx
            },
            'send_abandoned_cart_message': {
                'customer_phone': lambda ctx: ctx.get('customer_phone'),
                'customer_name': lambda ctx: ctx.get('customer_name'),
                'items': lambda ctx: ctx.get('abandoned_items', [])
            },
            'create_cart_abandoner_audience': {
                'customer_data': lambda ctx: ctx.get('customer_data', {}),
                'items': lambda ctx: ctx.get('abandoned_items', [])
            },
            'launch_cart_recovery_campaign': {
                'audience_id': lambda ctx: ctx.get('create_google_ads_audience_result', {}).get('audience_id'),
                'products': lambda ctx: ctx.get('abandoned_items', [])
            },
            'analyze_critical_stock': {
                'product_id': lambda ctx: ctx.get('product_id'),
                'current_stock': lambda ctx: ctx.get('stock_level'),
                'min_threshold': lambda ctx: ctx.get('min_threshold', 10)
            },
            'pause_product_campaigns': {
                'product_id': lambda ctx: ctx.get('product_id'),
                'reason': lambda ctx: 'critical_stock'
            },
            'prioritize_supplier_contacts': {
                'product_id': lambda ctx: ctx.get('product_id'),
                'urgency_level': lambda ctx: 'high' if ctx.get('critical_stock', False) else 'medium'
            },
            'send_stock_alert': {
                'product_id': lambda ctx: ctx.get('product_id'),
                'stock_level': lambda ctx: ctx.get('stock_level'),
                'supplier_contacted': lambda ctx: ctx.get('supplier_contacted', False)
            },
            'qualify_new_lead': {
                'lead_data': lambda ctx: ctx.get('lead_data'),
                'qualification_criteria': lambda ctx: ctx.get('qualification_criteria', {})
            },
            'send_welcome_message': {
                'lead_phone': lambda ctx: ctx.get('lead_data', {}).get('phone'),
                'lead_name': lambda ctx: ctx.get('lead_data', {}).get('name'),
                'lead_source': lambda ctx: ctx.get('lead_data', {}).get('source')
            },
            'create_lead_audience': {
                'lead_data': lambda ctx: ctx.get('lead_data'),
                'qualification_score': lambda ctx: ctx.get('lead_qualified_result', {}).get('score')
            },
            'launch_lead_nurture_campaign': {
                'audience_id': lambda ctx: ctx.get('create_lead_audience_result', {}).get('audience_id'),
                'lead_score': lambda ctx: ctx.get('lead_qualified_result', {}).get('score')
            },
            'schedule_followup_message': {
                'lead_phone': lambda ctx: ctx.get('lead_data', {}).get('phone'),
                'lead_name': lambda ctx: ctx.get('lead_data', {}).get('name'),
                'campaign_performance': lambda ctx: ctx.get('launch_lead_nurture_campaign_result', {})
            }
        }
        
        # Obter mapeamento de argumentos para a ação
        arg_map = action_args_map.get(action, {})
        
        # Preparar argumentos
        for arg_name, value_func in arg_map.items():
            try:
                args[arg_name] = value_func(context)
            except Exception as e:
                logger.warning(f"Erro ao preparar argumento '{arg_name}' para ação '{action}': {e}")
                args[arg_name] = None
        
        return args
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém o status de uma execução de workflow
        
        Args:
            execution_id: ID da execução
            
        Returns:
            Status da execução ou None se não encontrado
        """
        execution = self.executions.get(execution_id)
        if not execution:
            return None
        
        return {
            'execution_id': execution_id,
            'workflow_name': execution.workflow_name,
            'status': execution.status.value,
            'started_at': execution.started_at.isoformat(),
            'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
            'steps_executed': execution.steps_executed,
            'error_message': execution.error_message,
            'context': execution.context
        }
    
    def list_executions(self, workflow_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lista execuções de workflows
        
        Args:
            workflow_name: Nome do workflow para filtrar (opcional)
            
        Returns:
            Lista de execuções
        """
        executions = []
        
        for execution_id, execution in self.executions.items():
            if workflow_name and execution.workflow_name != workflow_name:
                continue
            
            executions.append({
                'execution_id': execution_id,
                'workflow_name': execution.workflow_name,
                'status': execution.status.value,
                'started_at': execution.started_at.isoformat(),
                'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
                'steps_count': len(execution.steps_executed),
                'error_message': execution.error_message
            })
        
        # Ordenar por data de início (decrescente)
        executions.sort(key=lambda x: x['started_at'], reverse=True)
        
        return executions
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancela uma execução de workflow em andamento
        
        Args:
            execution_id: ID da execução a cancelar
            
        Returns:
            True se foi cancelado com sucesso
        """
        if execution_id not in self.running_workflows:
            return False
        
        task = self.running_workflows[execution_id]
        task.cancel()
        
        # Atualizar status da execução
        if execution_id in self.executions:
            self.executions[execution_id].status = WorkflowStatus.FAILED
            self.executions[execution_id].error_message = "Execução cancelada pelo usuário"
            self.executions[execution_id].completed_at = datetime.now()
        
        logger.info(f"Execução '{execution_id}' cancelada")
        return True
    
    def get_workflow_definition(self, workflow_name: str) -> Optional[List[Dict[str, Any]]]:
        """
        Obtém a definição de um workflow
        
        Args:
            workflow_name: Nome do workflow
            
        Returns:
            Definição do workflow ou None se não encontrado
        """
        if workflow_name not in self.workflows:
            return None
        
        steps = []
        for step in self.workflows[workflow_name]:
            steps.append({
                'name': step.name,
                'squad': step.squad,
                'action': step.action,
                'condition': step.condition,
                'delay_seconds': step.delay_seconds,
                'retry_on_failure': step.retry_on_failure,
                'depends_on': step.depends_on
            })
        
        return steps
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """
        Lista todos os workflows registrados
        
        Returns:
            Lista de workflows
        """
        workflows = []
        
        for name, steps in self.workflows.items():
            workflows.append({
                'name': name,
                'steps_count': len(steps),
                'squads_involved': list(set(step.squad for step in steps)),
                'description': self._get_workflow_description(name)
            })
        
        return workflows
    
    def _get_workflow_description(self, workflow_name: str) -> str:
        """Obtém descrição de um workflow"""
        descriptions = {
            'abandoned_cart_recovery': 'Recuperação automatizada de carrinhos abandonados',
            'stock_emergency': 'Resposta a emergências de estoque',
            'new_lead_nurture': 'Nutrição e qualificação de novos leads'
        }
        
        return descriptions.get(workflow_name, 'Workflow personalizado')
    
    def get_execution_metrics(self) -> Dict[str, Any]:
        """
        Obtém métricas de execução de workflows
        
        Returns:
            Métricas de execução
        """
        total_executions = len(self.executions)
        
        if total_executions == 0:
            return {
                'total_executions': 0,
                'successful_executions': 0,
                'failed_executions': 0,
                'success_rate': 0,
                'average_execution_time': 0
            }
        
        successful = sum(1 for e in self.executions.values() if e.status == WorkflowStatus.COMPLETED)
        failed = sum(1 for e in self.executions.values() if e.status == WorkflowStatus.FAILED)
        
        # Calcular tempo médio de execução
        execution_times = []
        for execution in self.executions.values():
            if execution.completed_at and execution.started_at:
                duration = (execution.completed_at - execution.started_at).total_seconds()
                execution_times.append(duration)
        
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        return {
            'total_executions': total_executions,
            'successful_executions': successful,
            'failed_executions': failed,
            'success_rate': (successful / total_executions) * 100,
            'average_execution_time': avg_execution_time,
            'active_executions': len(self.running_workflows)
        }