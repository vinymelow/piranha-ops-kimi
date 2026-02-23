#!/usr/bin/env python3
"""
Exemplo de uso do WorkflowEngine
Demonstra como integrar e usar o motor de orquestração em aplicações reais
"""

import asyncio
import logging
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.workflow_engine import WorkflowEngine, WorkflowStep, WorkflowStatus

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class RealModelRouter:
    """
    Exemplo de ModelRouter real que integra com os squads
    Esta classe deve ser substituída pela implementação real do seu ModelRouter
    """
    
    def __init__(self):
        # Inicializar integrações com os squads
        self.squads = {
            'inventory': self._init_inventory_squad(),
            'whatsapp': self._init_whatsapp_squad(),
            'traffic': self._init_traffic_squad(),
            'lead_scraper': self._init_lead_scraper_squad(),
            'google_ads': self._init_google_ads_squad()
        }
    
    def _init_inventory_squad(self):
        """Inicializa integração com squad de inventário"""
        # Retornar cliente/configuração do squad de inventário
        return {"api_key": "inventory_key", "endpoint": "https://inventory.api"}
    
    def _init_whatsapp_squad(self):
        """Inicializa integração com squad de WhatsApp"""
        return {"api_key": "whatsapp_key", "endpoint": "https://whatsapp.api"}
    
    def _init_traffic_squad(self):
        """Inicializa integração com squad de tráfego"""
        return {"api_key": "traffic_key", "endpoint": "https://traffic.api"}
    
    def _init_lead_scraper_squad(self):
        """Inicializa integração com squad de lead scraper"""
        return {"api_key": "lead_scraper_key", "endpoint": "https://lead-scraper.api"}
    
    def _init_google_ads_squad(self):
        """Inicializa integração com squad de Google Ads"""
        return {"api_key": "google_ads_key", "endpoint": "https://google-ads.api"}
    
    async def execute_squad_action(self, squad: str, action: str, **kwargs):
        """
        Executa uma ação em um squad específico
        
        Args:
            squad: Nome do squad (inventory, whatsapp, traffic, lead_scraper, google_ads)
            action: Nome da ação a executar
            **kwargs: Argumentos para a ação
            
        Returns:
            Resultado da execução da ação
        """
        logger.info(f"Executando ação '{action}' no squad '{squad}'")
        
        if squad not in self.squads:
            raise ValueError(f"Squad '{squad}' não encontrado")
        
        # Aqui você implementaria a lógica real de integração com cada squad
        # Por enquanto, vamos retornar respostas mockadas para demonstração
        
        if squad == 'inventory':
            return await self._execute_inventory_action(action, **kwargs)
        elif squad == 'whatsapp':
            return await self._execute_whatsapp_action(action, **kwargs)
        elif squad == 'traffic':
            return await self._execute_traffic_action(action, **kwargs)
        elif squad == 'lead_scraper':
            return await self._execute_lead_scraper_action(action, **kwargs)
        elif squad == 'google_ads':
            return await self._execute_google_ads_action(action, **kwargs)
        else:
            raise ValueError(f"Ação não implementada para squad '{squad}'")
    
    async def _execute_inventory_action(self, action: str, **kwargs):
        """Executa ações do squad de inventário"""
        if action == 'check_stock':
            # Verificar estoque dos itens
            items = kwargs.get('items', [])
            return {
                'stock_available': True,
                'items_checked': len(items),
                'low_stock_items': []
            }
        elif action == 'analyze_critical_stock':
            # Analisar situação crítica de estoque
            return {
                'critical_stock': True,
                'current_level': kwargs.get('current_stock', 0),
                'recommendation': 'Comprar mais unidades urgentemente'
            }
        else:
            raise ValueError(f"Ação '{action}' não implementada para inventory")
    
    async def _execute_whatsapp_action(self, action: str, **kwargs):
        """Executa ações do squad de WhatsApp"""
        if action == 'send_abandoned_cart_message':
            # Enviar mensagem de carrinho abandonado
            customer_phone = kwargs.get('customer_phone')
            items = kwargs.get('items', [])
            return {
                'message_sent': True,
                'message_id': f"msg_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'recipient': customer_phone,
                'items_count': len(items)
            }
        elif action == 'send_welcome_message':
            # Enviar mensagem de boas-vindas
            lead_phone = kwargs.get('lead_phone')
            return {
                'welcome_sent': True,
                'message_id': f"welcome_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'recipient': lead_phone
            }
        elif action == 'send_stock_alert':
            # Enviar alerta de estoque
            return {
                'alert_sent': True,
                'recipients': ['manager@company.com', 'inventory@company.com'],
                'alert_type': 'critical_stock'
            }
        elif action == 'schedule_followup_message':
            # Agendar mensagem de follow-up
            return {
                'scheduled': True,
                'schedule_time': (datetime.now() + timedelta(hours=48)).isoformat(),
                'message_type': 'followup'
            }
        else:
            raise ValueError(f"Ação '{action}' não implementada para whatsapp")
    
    async def _execute_traffic_action(self, action: str, **kwargs):
        """Executa ações do squad de tráfego"""
        if action == 'launch_cart_recovery_campaign':
            # Lançar campanha de recuperação de carrinho
            return {
                'campaign_id': f"cart_recovery_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'status': 'active',
                'target_audience': 'cart_abandoners',
                'budget': 100.0
            }
        elif action == 'launch_lead_nurture_campaign':
            # Lançar campanha de nutrição de leads
            return {
                'campaign_id': f"lead_nurture_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'status': 'active',
                'target_audience': 'qualified_leads',
                'budget': 150.0
            }
        else:
            raise ValueError(f"Ação '{action}' não implementada para traffic")
    
    async def _execute_lead_scraper_action(self, action: str, **kwargs):
        """Executa ações do squad de lead scraper"""
        if action == 'qualify_new_lead':
            # Qualificar novo lead
            lead_data = kwargs.get('lead_data', {})
            qualification_criteria = kwargs.get('qualification_criteria', {})
            
            # Simular qualificação baseada em critérios
            score = 85  # Score mockado
            
            return {
                'lead_qualified': True,
                'score': score,
                'qualification_reason': 'Meets all criteria',
                'lead_data': lead_data
            }
        elif action == 'prioritize_supplier_contacts':
            # Priorizar contatos com fornecedores
            return {
                'supplier_contacted': True,
                'suppliers_list': ['supplier_1', 'supplier_2', 'supplier_3'],
                'urgency_level': kwargs.get('urgency_level', 'medium')
            }
        else:
            raise ValueError(f"Ação '{action}' não implementada para lead_scraper")
    
    async def _execute_google_ads_action(self, action: str, **kwargs):
        """Executa ações do squad de Google Ads"""
        if action == 'create_cart_abandoner_audience':
            # Criar audiência de carrinho abandonado
            return {
                'audience_id': f"cart_abandoner_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'audience_size': 1000,
                'audience_type': 'cart_abandoners'
            }
        elif action == 'create_lead_audience':
            # Criar audiência de leads
            return {
                'audience_id': f"lead_audience_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'qualified_leads': 1,
                'audience_size': 1
            }
        elif action == 'pause_product_campaigns':
            # Pausar campanhas de produto
            return {
                'campaigns_paused': 3,
                'product_id': kwargs.get('product_id'),
                'reason': kwargs.get('reason', 'unknown')
            }
        else:
            raise ValueError(f"Ação '{action}' não implementada para google_ads")


class RealDataStore:
    """
    Exemplo de DataStore real que persiste dados de execução
    Esta classe deve ser substituída pela implementação real do seu DataStore
    """
    
    def __init__(self, db_connection=None):
        self.db_connection = db_connection or {}
        self.workflow_executions = {}
    
    def store_workflow_execution(self, execution_id: str, data: dict):
        """Armazena execução de workflow"""
        self.workflow_executions[execution_id] = {
            'data': data,
            'stored_at': datetime.now().isoformat()
        }
        logger.info(f"Execução '{execution_id}' armazenada no banco de dados")
    
    def get_workflow_execution(self, execution_id: str):
        """Recupera execução de workflow"""
        return self.workflow_executions.get(execution_id)
    
    def list_workflow_executions(self, workflow_name: str = None):
        """Lista execuções de workflow"""
        executions = []
        for exec_id, data in self.workflow_executions.items():
            if workflow_name and data['data'].get('workflow_name') != workflow_name:
                continue
            executions.append({
                'execution_id': exec_id,
                'data': data['data'],
                'stored_at': data['stored_at']
            })
        return executions


async def example_abandoned_cart_recovery():
    """Exemplo de uso: Recuperação de carrinho abandonado"""
    logger.info("\n" + "="*60)
    logger.info("EXEMPLO: Recuperação de Carrinho Abandonado")
    logger.info("="*60)
    
    # Criar instâncias reais (substitua pelas suas implementações)
    model_router = RealModelRouter()
    data_store = RealDataStore()
    
    # Criar WorkflowEngine
    engine = WorkflowEngine(model_router, data_store)
    
    # Preparar contexto do cliente com carrinho abandonado
    context = {
        "customer_phone": "+5511999999999",
        "customer_name": "João Silva",
        "customer_data": {
            "email": "joao.silva@example.com",
            "phone": "+5511999999999",
            "first_name": "João",
            "last_name": "Silva"
        },
        "abandoned_items": [
            {
                "id": "prod_123",
                "name": "Tênis Nike Air Max",
                "price": 299.90,
                "quantity": 1,
                "image_url": "https://example.com/images/tenis-nike.jpg"
            },
            {
                "id": "prod_456",
                "name": "Camiseta Adidas Sport",
                "price": 89.90,
                "quantity": 2,
                "image_url": "https://example.com/images/camiseta-adidas.jpg"
            }
        ],
        "cart_value": 479.70,
        "abandon_time": "2024-01-15T14:30:00Z",
        "last_visit": "2024-01-15T14:25:00Z"
    }
    
    # Executar workflow
    logger.info("Disparando workflow de recuperação de carrinho abandonado...")
    execution_id = await engine.trigger("abandoned_cart_recovery", context)
    
    logger.info(f"Workflow iniciado com ID: {execution_id}")
    logger.info("Aguardando execução dos steps (com delays)...")
    
    # Aguardar um pouco para ver os delays em ação
    await asyncio.sleep(5)
    
    # Verificar status
    status = engine.get_execution_status(execution_id)
    logger.info(f"\nStatus da execução:")
    logger.info(f"  - Status: {status['status']}")
    logger.info(f"  - Steps executados: {len(status['steps_executed'])}")
    logger.info(f"  - Contexto final: {status['context']}")
    
    return execution_id


async def example_custom_workflow():
    """Exemplo de criação de workflow personalizado"""
    logger.info("\n" + "="*60)
    logger.info("EXEMPLO: Workflow Personalizado")
    logger.info("="*60)
    
    # Criar instâncias
    model_router = RealModelRouter()
    data_store = RealDataStore()
    
    # Criar WorkflowEngine
    engine = WorkflowEngine(model_router, data_store)
    
    # Definir workflow personalizado para campanha de Black Friday
    black_friday_workflow = [
        WorkflowStep(
            name="analyze_inventory",
            squad="inventory",
            action="analyze_black_friday_stock",
            condition="lambda context: context.get('event_type') == 'black_friday'",
            retry_on_failure=2
        ),
        WorkflowStep(
            name="create_bf_audiences",
            squad="google_ads",
            action="create_black_friday_audiences",
            depends_on=["analyze_inventory"],
            delay_seconds=300  # 5 minutos
        ),
        WorkflowStep(
            name="prepare_whatsapp_campaigns",
            squad="whatsapp",
            action="prepare_bf_messages",
            depends_on=["analyze_inventory"],
            delay_seconds=600  # 10 minutos
        ),
        WorkflowStep(
            name="launch_bf_campaigns",
            squad="traffic",
            action="launch_black_friday_campaigns",
            depends_on=["create_bf_audiences", "prepare_whatsapp_campaigns"],
            condition="lambda context: context.get('inventory_ready', False)",
            delay_seconds=1800  # 30 minutos
        ),
        WorkflowStep(
            name="monitor_performance",
            squad="traffic",
            action="monitor_campaign_performance",
            depends_on=["launch_bf_campaigns"],
            delay_seconds=3600  # 1 hora
        )
    ]
    
    # Registrar workflow personalizado
    engine.register_workflow("black_friday_campaign", black_friday_workflow)
    
    logger.info("Workflow personalizado 'black_friday_campaign' registrado com sucesso!")
    logger.info(f"Steps do workflow: {len(black_friday_workflow)}")
    
    # Preparar contexto
    context = {
        "event_type": "black_friday",
        "campaign_date": "2024-11-29",
        "expected_traffic": 10000,
        "special_products": ["prod_1", "prod_2", "prod_3"],
        "discount_percentage": 50,
        "inventory_ready": True
    }
    
    # Executar workflow personalizado
    logger.info("Disparando workflow de Black Friday...")
    execution_id = await engine.trigger("black_friday_campaign", context)
    
    logger.info(f"Workflow iniciado com ID: {execution_id}")
    
    # Aguardar um pouco
    await asyncio.sleep(2)
    
    # Verificar definição do workflow
    definition = engine.get_workflow_definition("black_friday_campaign")
    logger.info(f"\nDefinição do workflow:")
    for i, step in enumerate(definition, 1):
        logger.info(f"  {i}. {step['name']} ({step['squad']}) -> {step['action']}")
        if step['depends_on']:
            logger.info(f"     Depende de: {', '.join(step['depends_on'])}")
        if step['condition']:
            logger.info(f"     Condição: {step['condition']}")
        if step['delay_seconds'] > 0:
            logger.info(f"     Delay: {step['delay_seconds']} segundos")
    
    return execution_id


async def main():
    """Função principal com exemplos de uso"""
    logger.info("Iniciando exemplos de uso do WorkflowEngine")
    
    try:
        # Exemplo 1: Recuperação de carrinho abandonado
        await example_abandoned_cart_recovery()
        
        # Exemplo 2: Workflow personalizado
        await example_custom_workflow()
        
        logger.info("\n✅ Todos os exemplos foram executados com sucesso!")
        logger.info("\nPróximos passos:")
        logger.info("1. Substitua RealModelRouter pela sua implementação real")
        logger.info("2. Substitua RealDataStore pelo seu sistema de persistência real")
        logger.info("3. Configure os squads com suas APIs reais")
        logger.info("4. Monitore as execuções e ajuste os workflows conforme necessário")
        
    except Exception as e:
        logger.error(f"❌ Erro durante os exemplos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Import necessário para o exemplo
    from datetime import timedelta
    asyncio.run(main())