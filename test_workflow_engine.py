#!/usr/bin/env python3
"""
Script de teste para o WorkflowEngine
Demonstra o funcionamento do motor de orquestração com workflows cross-squad
"""

import asyncio
import logging
from datetime import datetime
from core.workflow_engine import WorkflowEngine, WorkflowStep, WorkflowStatus

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class MockModelRouter:
    """Mock do ModelRouter para testes"""
    
    async def execute_squad_action(self, squad: str, action: str, **kwargs):
        """Mock da execução de ação do squad"""
        logger.info(f"Mock: Executando ação '{action}' do squad '{squad}' com args: {kwargs}")
        
        # Simular diferentes respostas baseado na ação
        if action == "check_stock":
            return {"stock_available": True, "items_in_stock": kwargs.get("items", [])}
        elif action == "send_abandoned_cart_message":
            return {"message_sent": True, "message_id": "msg_123"}
        elif action == "create_cart_abandoner_audience":
            return {"audience_id": "aud_123", "audience_size": 100}
        elif action == "launch_cart_recovery_campaign":
            return {"campaign_id": "camp_123", "status": "active"}
        elif action == "analyze_critical_stock":
            return {"critical_stock": True, "current_level": 5}
        elif action == "pause_product_campaigns":
            return {"campaigns_paused": 3}
        elif action == "prioritize_supplier_contacts":
            return {"supplier_contacted": True, "suppliers_list": ["supplier1", "supplier2"]}
        elif action == "send_stock_alert":
            return {"alert_sent": True, "recipients": ["manager@company.com"]}
        elif action == "qualify_new_lead":
            return {"lead_qualified": True, "score": 85}
        elif action == "send_welcome_message":
            return {"welcome_sent": True, "message_id": "welcome_123"}
        elif action == "create_lead_audience":
            return {"audience_id": "lead_aud_123", "qualified_leads": 1}
        elif action == "launch_lead_nurture_campaign":
            return {"campaign_id": "nurture_123", "status": "active"}
        elif action == "schedule_followup_message":
            return {"scheduled": True, "schedule_time": "2024-01-01 10:00:00"}
        else:
            return {"success": True, "action": action}


class MockDataStore:
    """Mock do DataStore para testes"""
    
    def __init__(self):
        self.data = {}
    
    def store_workflow_execution(self, execution_id: str, data: dict):
        """Mock do armazenamento de execução"""
        self.data[f"workflow_{execution_id}"] = data
        logger.info(f"Mock: Execução '{execution_id}' armazenada")


async def test_abandoned_cart_recovery():
    """Testa o workflow de recuperação de carrinho abandonado"""
    logger.info("\n" + "="*60)
    logger.info("TESTANDO: Workflow de Recuperação de Carrinho Abandonado")
    logger.info("="*60)
    
    # Criar mocks
    model_router = MockModelRouter()
    data_store = MockDataStore()
    
    # Criar WorkflowEngine
    engine = WorkflowEngine(model_router, data_store)
    
    # Contexto do teste
    context = {
        "customer_phone": "+5511999999999",
        "customer_name": "João Silva",
        "customer_data": {"email": "joao@example.com", "phone": "+5511999999999"},
        "abandoned_items": [
            {"id": "prod_1", "name": "Tênis Nike", "price": 299.90},
            {"id": "prod_2", "name": "Camiseta Adidas", "price": 89.90}
        ]
    }
    
    # Executar workflow
    execution_id = await engine.trigger("abandoned_cart_recovery", context)
    
    # Aguardar execução completar
    await asyncio.sleep(2)
    
    # Verificar status
    status = engine.get_execution_status(execution_id)
    logger.info(f"Status da execução: {status['status']}")
    logger.info(f"Steps executados: {len(status['steps_executed'])}")
    
    for step in status['steps_executed']:
        logger.info(f"  - {step['step_name']}: {step['status']}")
    
    return execution_id


async def test_stock_emergency():
    """Testa o workflow de emergência de estoque"""
    logger.info("\n" + "="*60)
    logger.info("TESTANDO: Workflow de Emergência de Estoque")
    logger.info("="*60)
    
    # Criar mocks
    model_router = MockModelRouter()
    data_store = MockDataStore()
    
    # Criar WorkflowEngine
    engine = WorkflowEngine(model_router, data_store)
    
    # Contexto do teste
    context = {
        "product_id": "prod_123",
        "stock_level": 3,
        "min_threshold": 10
    }
    
    # Executar workflow
    execution_id = await engine.trigger("stock_emergency", context)
    
    # Aguardar execução completar
    await asyncio.sleep(2)
    
    # Verificar status
    status = engine.get_execution_status(execution_id)
    logger.info(f"Status da execução: {status['status']}")
    logger.info(f"Steps executados: {len(status['steps_executed'])}")
    
    for step in status['steps_executed']:
        logger.info(f"  - {step['step_name']}: {step['status']}")
    
    return execution_id


async def test_new_lead_nurture():
    """Testa o workflow de nutrição de novo lead"""
    logger.info("\n" + "="*60)
    logger.info("TESTANDO: Workflow de Nutrição de Novo Lead")
    logger.info("="*60)
    
    # Criar mocks
    model_router = MockModelRouter()
    data_store = MockDataStore()
    
    # Criar WorkflowEngine
    engine = WorkflowEngine(model_router, data_store)
    
    # Contexto do teste
    context = {
        "lead_data": {
            "name": "Maria Santos",
            "phone": "+5511888888888",
            "email": "maria@example.com",
            "source": "Facebook Ads",
            "interests": ["moda", "esportes"]
        },
        "qualification_criteria": {
            "min_budget": 100,
            "interests_required": ["moda"]
        }
    }
    
    # Executar workflow
    execution_id = await engine.trigger("new_lead_nurture", context)
    
    # Aguardar execução completar
    await asyncio.sleep(2)
    
    # Verificar status
    status = engine.get_execution_status(execution_id)
    logger.info(f"Status da execução: {status['status']}")
    logger.info(f"Steps executados: {len(status['steps_executed'])}")
    
    for step in status['steps_executed']:
        logger.info(f"  - {step['step_name']}: {step['status']}")
    
    return execution_id


async def test_workflow_metrics():
    """Testa as métricas de workflow"""
    logger.info("\n" + "="*60)
    logger.info("TESTANDO: Métricas de Workflow")
    logger.info("="*60)
    
    # Criar mocks
    model_router = MockModelRouter()
    data_store = MockDataStore()
    
    # Criar WorkflowEngine
    engine = WorkflowEngine(model_router, data_store)
    
    # Executar alguns workflows
    await engine.trigger("abandoned_cart_recovery", {
        "customer_phone": "+5511999999999",
        "customer_name": "Teste 1",
        "abandoned_items": [{"id": "prod_1", "name": "Produto 1"}]
    })
    
    await engine.trigger("stock_emergency", {
        "product_id": "prod_123",
        "stock_level": 3,
        "min_threshold": 10
    })
    
    await engine.trigger("new_lead_nurture", {
        "lead_data": {"name": "Teste Lead", "phone": "+5511111111111"}
    })
    
    # Aguardar execuções completarem
    await asyncio.sleep(3)
    
    # Obter métricas
    metrics = engine.get_execution_metrics()
    logger.info("Métricas de Execução:")
    for key, value in metrics.items():
        logger.info(f"  {key}: {value}")
    
    # Listar workflows
    workflows = engine.list_workflows()
    logger.info("\nWorkflows Registrados:")
    for workflow in workflows:
        logger.info(f"  - {workflow['name']}: {workflow['description']}")
        logger.info(f"    Steps: {workflow['steps_count']}, Squads: {workflow['squads_involved']}")


async def main():
    """Função principal de teste"""
    logger.info("Iniciando testes do WorkflowEngine")
    
    try:
        # Testar workflows individuais
        await test_abandoned_cart_recovery()
        await test_stock_emergency()
        await test_new_lead_nurture()
        
        # Testar métricas
        await test_workflow_metrics()
        
        logger.info("\n✅ Todos os testes foram concluídos com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())