# Workflow Engine - Motor de Orquestração Multi-Squad

## Visão Geral

O WorkflowEngine é um motor de orquestração de processos multi-squad que permite coordenar a execução de workflows complexos entre diferentes equipes (squads) de forma automatizada e assíncrona.

## Características Principais

- **Orquestração Multi-Squad**: Coordena ações entre 5 squads (inventory, whatsapp, traffic, lead_scraper, google_ads)
- **Workflows Cross-Squad**: Executa processos que envolvem múltiplas equipes
- **Sistema de Condições**: Usa expressões lambda para lógica dinâmica
- **Retry e Error Handling**: Sistema robusto de retentativas e tratamento de erros
- **Monitoramento em Tempo Real**: Histórico de execução e métricas detalhadas
- **Delays e Dependências**: Suporte para delays entre steps e dependências complexas

## Estrutura

### Classes Principais

#### WorkflowEngine
Classe principal que gerencia a execução de workflows.

```python
class WorkflowEngine:
    def __init__(self, model_router, data_store):
        # Inicializa o motor com os serviços necessários
        
    def register_workflow(self, name: str, steps: List[WorkflowStep]):
        # Registra um novo workflow
        
    async def trigger(self, workflow_name: str, context: Dict[str, Any] = None) -> str:
        # Dispara a execução de um workflow
        
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        # Obtém o status de uma execução
```

#### WorkflowStep
Representa um passo individual em um workflow.

```python
@dataclass
class WorkflowStep:
    name: str                    # Nome do step
    squad: str                   # Squad responsável (inventory, whatsapp, etc.)
    action: str                  # Nome da ação a ser executada
    condition: Optional[str]     # Expressão lambda para condição
    delay_seconds: int = 0       # Delay antes da execução
    retry_on_failure: int = 0    # Número de retries em caso de falha
    depends_on: List[str] = []   # Steps dependentes
```

## Workflows Padrão

### 1. Recuperação de Carrinho Abandonado (`abandoned_cart_recovery`)

**Descrição**: Workflow automatizado para recuperar clientes que abandonaram carrinhos de compras.

**Steps**:
1. `check_inventory` - Verifica disponibilidade de estoque
2. `send_whatsapp_reminder` - Envia lembrete via WhatsApp (5 min delay)
3. `create_google_ads_audience` - Cria audiência no Google Ads (1 hora delay)
4. `launch_retargeting_campaign` - Lança campanha de retargeting

**Squads Envolvidas**: inventory → whatsapp → google_ads → traffic

**Contexto Esperado**:
```python
context = {
    "customer_phone": "+5511999999999",
    "customer_name": "João Silva",
    "abandoned_items": [...],
    "cart_value": 479.70
}
```

### 2. Emergência de Estoque (`stock_emergency`)

**Descrição**: Resposta automática a situações críticas de estoque.

**Steps**:
1. `analyze_stock_situation` - Analisa situação do estoque
2. `pause_google_ads` - Pausa campanhas do produto (condicional)
3. `notify_lead_scraper` - Notifica equipe de compras (1 min delay)
4. `send_whatsapp_alert` - Envia alerta via WhatsApp (30 min delay)

**Squads Envolvidas**: inventory → google_ads → lead_scraper → whatsapp

**Contexto Esperado**:
```python
context = {
    "product_id": "prod_123",
    "stock_level": 3,
    "min_threshold": 10
}
```

### 3. Nutrição de Novo Lead (`new_lead_nurture`)

**Descrição**: Processo de qualificação e nutrição de novos leads.

**Steps**:
1. `qualify_lead` - Qualifica o lead
2. `send_welcome_whatsapp` - Envia mensagem de boas-vindas (1 min delay)
3. `create_lead_audience` - Cria audiência no Google Ads (5 min delay)
4. `launch_lead_nurture_campaign` - Lança campanha de nutrição (24 horas delay)
5. `schedule_followup` - Agenda follow-up (48 horas delay)

**Squads Envolvidas**: lead_scraper → whatsapp → google_ads → traffic → whatsapp

**Contexto Esperado**:
```python
context = {
    "lead_data": {
        "name": "Maria Santos",
        "phone": "+5511888888888",
        "email": "maria@example.com",
        "source": "Facebook Ads"
    }
}
```

## Como Usar

### 1. Instalação e Configuração

```python
from core.workflow_engine import WorkflowEngine, WorkflowStep

# Criar instâncias dos serviços necessários
model_router = SeuModelRouter()  # Implementação real do ModelRouter
data_store = SeuDataStore()      # Implementação real do DataStore

# Criar WorkflowEngine
engine = WorkflowEngine(model_router, data_store)
```

### 2. Executar um Workflow Padrão

```python
# Preparar contexto
context = {
    "customer_phone": "+5511999999999",
    "customer_name": "João Silva",
    "abandoned_items": [
        {"id": "prod_1", "name": "Produto 1", "price": 100.0}
    ]
}

# Executar workflow
execution_id = await engine.trigger("abandoned_cart_recovery", context)

# Verificar status
status = engine.get_execution_status(execution_id)
print(f"Status: {status['status']}")
print(f"Steps executados: {len(status['steps_executed'])}")
```

### 3. Criar Workflow Personalizado

```python
# Definir steps do workflow
meu_workflow = [
    WorkflowStep(
        name="primeiro_step",
        squad="inventory",
        action="minha_acao",
        condition="lambda context: context.get('condicao', False)",
        delay_seconds=60,
        retry_on_failure=3
    ),
    WorkflowStep(
        name="segundo_step",
        squad="whatsapp",
        action="outra_acao",
        depends_on=["primeiro_step"],
        delay_seconds=300
    )
]

# Registrar workflow
engine.register_workflow("meu_workflow_personalizado", meu_workflow)

# Executar
execution_id = await engine.trigger("meu_workflow_personalizado", context)
```

### 4. Monitoramento e Métricas

```python
# Obter métricas gerais
metrics = engine.get_execution_metrics()
print(f"Taxa de sucesso: {metrics['success_rate']:.1f}%")
print(f"Execuções ativas: {metrics['active_executions']}")

# Listar execuções
executions = engine.list_executions()
for execution in executions:
    print(f"{execution['execution_id']}: {execution['status']}")

# Listar workflows disponíveis
workflows = engine.list_workflows()
for workflow in workflows:
    print(f"{workflow['name']}: {workflow['description']}")
```

## Sistema de Condições

As condições são expressões lambda que são avaliadas em tempo de execução:

```python
# Condição simples
condition="lambda context: context.get('stock_level', 0) < 10"

# Condição complexa
condition="lambda context: context.get('customer_type') == 'premium' and context.get('cart_value', 0) > 500"

# Condição com múltiplos fatores
condition="lambda context: len(context.get('abandoned_items', [])) > 0 and context.get('customer_active', False)"
```

## Sistema de Retry

Configure retentativas automáticas para lidar com falhas temporárias:

```python
WorkflowStep(
    name="acao_critica",
    squad="google_ads",
    action="criar_campanha",
    retry_on_failure=3,  # Tentar até 3 vezes
    delay_seconds=60     # Aguardar 1 minuto entre tentativas
)
```

O sistema usa backoff exponencial entre as tentativas.

## Dependências entre Steps

Defina dependências para garantir ordem de execução:

```python
WorkflowStep(
    name="step_2",
    squad="whatsapp",
    action="enviar_mensagem",
    depends_on=["step_1"]  # Aguarda step_1 ser concluído
)
```

## Integração com Squads

O WorkflowEngine se integra com 5 squads principais:

### 1. Inventory Squad
- **Ações**: `check_stock`, `analyze_critical_stock`
- **Responsabilidade**: Gerenciamento de estoque e produtos

### 2. WhatsApp Squad
- **Ações**: `send_abandoned_cart_message`, `send_welcome_message`, `send_stock_alert`, `schedule_followup_message`
- **Responsabilidade**: Comunicação com clientes via WhatsApp

### 3. Traffic Squad
- **Ações**: `launch_cart_recovery_campaign`, `launch_lead_nurture_campaign`
- **Responsabilidade**: Gerenciamento de campanhas de tráfego

### 4. Lead Scraper Squad
- **Ações**: `qualify_new_lead`, `prioritize_supplier_contacts`
- **Responsabilidade**: Captação e qualificação de leads

### 5. Google Ads Squad
- **Ações**: `create_cart_abandoner_audience`, `create_lead_audience`, `pause_product_campaigns`
- **Responsabilidade**: Gerenciamento de campanhas no Google Ads

## Tratamento de Erros

O WorkflowEngine implementa várias camadas de tratamento de erros:

1. **Validação de Entrada**: Verifica existência de workflows e parâmetros
2. **Tratamento de Exceções**: Captura e registra erros durante execução
3. **Sistema de Retry**: Retentativas automáticas com backoff exponencial
4. **Logs Detalhados**: Registra todos os eventos para debugging
5. **Status de Falha**: Marca execuções como falhas quando apropriado

## Performance e Escalabilidade

- **Execução Assíncrona**: Todos os workflows são executados de forma assíncrona
- **Gestão de Memória**: Execuções completas são armazenadas de forma eficiente
- **Monitoramento em Tempo Real**: Métricas atualizadas em tempo real
- **Cancelamento de Execuções**: Suporte para cancelar execuções em andamento

## Exemplos de Uso

Consulte os arquivos de exemplo:
- `examples/workflow_usage_example.py` - Exemplos completos de uso
- `test_workflow_engine.py` - Testes e demonstrações

## Próximos Passos

1. **Integrar com ModelRouter Real**: Substitua as implementações de exemplo pelas integrações reais
2. **Configurar DataStore**: Implemente persistência de dados real
3. **Customizar Workflows**: Crie workflows específicos para seu negócio
4. **Monitorar Performance**: Use as métricas para otimizar execuções
5. **Escalar Horizontalmente**: Considere implementar suporte para múltiplas instâncias

## Suporte e Troubleshooting

### Logs
O WorkflowEngine registra logs detalhados em todos os níveis (DEBUG, INFO, WARNING, ERROR).

### Debugging
- Use `get_execution_status()` para verificar detalhes de execuções
- Verifique logs para identificar pontos de falha
- Use `list_executions()` para ver histórico completo

### Problemas Comuns
1. **Workflow não encontrado**: Verifique se o workflow foi registrado corretamente
2. **Condições não avaliadas**: Verifique sintaxe das expressões lambda
3. **Dependências não satisfeitas**: Confira nomes dos steps dependentes
4. **Timeouts em ações**: Ajuste valores de delay e retry conforme necessário