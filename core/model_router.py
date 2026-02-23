"""
Roteador inteligente de modelos Moonshot
Implementa estratégia: 85% economy, 15% standard, <1% deep
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuração de um modelo"""
    id: str
    input_price: float  # $ por 1M tokens
    output_price: float
    description: str

class ModelRouter:
    """
    Roteador que seleciona automaticamente o melhor modelo
    baseado no tipo de tarefa e orçamento
    """
    
    MODELS = {
        'economy': ModelConfig(
            id='kimi-k2-turbo-preview',
            input_price=0.50,
            output_price=2.00,
            description='Coleta, formatação, cálculos simples'
        ),
        'standard': ModelConfig(
            id='kimi-k2-0905-preview',
            input_price=2.00,
            output_price=10.00,
            description='Análise, insights, escrita criativa'
        ),
        'deep': ModelConfig(
            id='kimi-k2-thinking',
            input_price=3.00,
            output_price=15.00,
            description='Debug complexo, arquitetura, estratégia'
        )
    }
    
    # Mapeamento tarefa → modelo (OTIMIZADO para 85%/15%/<1%)
    # Economy: 17 tarefas (85%) | Standard: 3 tarefas (15%) | Deep: 1 tarefa (<1%)
    TASK_MODEL_MAP = {
        # Economy (85% do uso) - 17 tarefas simples
        'fetch_meta_data': 'economy',
        'format_metrics': 'economy',
        'check_status': 'economy',
        'count_alerts': 'economy',
        'list_campaigns': 'economy',
        'calculate_baseline': 'economy',
        'generate_csv': 'economy',
        'log_event': 'economy',
        'validate_data': 'economy',
        'extract_numbers': 'economy',
        'simple_math': 'economy',
        'filter_data': 'economy',
        'sort_list': 'economy',
        'parse_json': 'economy',
        'clean_text': 'economy',
        'count_words': 'economy',
        'basic_summary': 'economy',
        
        # Standard (15% do uso) - 3 tarefas complexas
        'analyze_performance': 'standard',
        'detect_anomalies': 'standard',
        'write_alert': 'standard',
        
        # Deep (<1% do uso) - 1 tarefa estratégica
        'debug_error': 'deep',
        'architect_system': 'deep',
        'predictive_analysis': 'deep',
        'strategic_decision': 'deep',
        'complex_reasoning': 'deep'
    }
    
    def __init__(self, client: Any, daily_budget: float = 1.0):
        self.client = client
        self.session_stats = {
            'economy': {'calls': 0, 'tokens_in': 0, 'tokens_out': 0, 'cost': 0.0},
            'standard': {'calls': 0, 'tokens_in': 0, 'tokens_out': 0, 'cost': 0.0},
            'deep': {'calls': 0, 'tokens_in': 0, 'tokens_out': 0, 'cost': 0.0}
        }
        self.daily_budget = daily_budget
        self.daily_spent = 0.0
        self.call_history = []  # Para análise de padrões
        self._budget_warning_shown = False
        
        logger.info(f"🎯 ModelRouter inicializado - Budget: ${daily_budget}/dia")
    
    def select_model(self, task_type: str, force_model: Optional[str] = None) -> tuple:
        """
        Seleciona modelo apropriado
        
        Args:
            task_type: Tipo da tarefa (ex: 'fetch_meta_data')
            force_model: Forçar modelo específico (economy/standard/deep)
        
        Returns:
            (model_id, model_key, config)
        """
        if force_model:
            model_key = force_model
        else:
            model_key = self.TASK_MODEL_MAP.get(task_type, 'economy')
        
        # Se orçamento acabando, força economy (exceto para tarefas críticas)
        if self.daily_spent > (self.daily_budget * 0.8) and model_key != 'economy':
            if task_type not in ['debug_error', 'strategic_decision']:  # Manter deep para críticas
                logger.warning(f"⚠️ Orçamento acabando! Forçando economy para {task_type}")
                model_key = 'economy'
        
        # Se orçamento quase esgotado, bloqueia deep
        if self.daily_spent > (self.daily_budget * 0.95) and model_key == 'deep':
            logger.error(f"❌ Orçamento quase esgotado! Bloqueando modelo deep")
            model_key = 'standard'
        
        config = self.MODELS[model_key]
        return config.id, model_key, config
    
    def call(self, task_type: str, messages: List[Dict], 
             force_model: Optional[str] = None, **kwargs) -> Any:
        """
        Executa chamada à API com modelo selecionado
        
        Args:
            task_type: Tipo da tarefa para seleção automática
            messages: Mensagens para o modelo
            force_model: Opcional - forçar modelo específico
            **kwargs: Parâmetros adicionais (temperature, max_tokens, etc)
        """
        model_id, model_key, config = self.select_model(task_type, force_model)
        
        # Verificar orçamento antes de executar
        estimated_cost = self._estimate_cost(messages, kwargs.get('max_tokens', 1000), config)
        if self.daily_spent + estimated_cost > self.daily_budget:
            logger.error(f"❌ Orçamento diário excedido! (${self.daily_spent:.2f} / ${self.daily_budget:.2f})")
            logger.error(f"   Custo estimado: ${estimated_cost:.4f}")
            raise Exception(f"Daily budget exceeded: ${self.daily_spent:.2f}/${self.daily_budget:.2f}")
        
        try:
            logger.debug(f"🎯 {task_type} → {model_id} (est: ${estimated_cost:.4f})")
            
            # Registrar chamada para análise
            self.call_history.append({
                'timestamp': datetime.now(),
                'task_type': task_type,
                'model_key': model_key,
                'estimated_cost': estimated_cost
            })
            
            response = self.client.chat.completions.create(
                model=model_id,
                messages=messages,
                **kwargs
            )
            
            # Registrar uso real
            self._track_usage(model_key, response.usage, config)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Erro em {model_id}: {e}")
            
            # Fallback para economy se falhar (exceto se já for economy)
            if model_key != 'economy':
                logger.info(f"🔄 Fallback para economy em {task_type}...")
                return self.call(task_type, messages, force_model='economy', **kwargs)
            
            # Se economy também falhar, raise o erro
            raise
    
    def _estimate_cost(self, messages: List[Dict], max_tokens: int, config: ModelConfig) -> float:
        """Estima custo da chamada"""
        # Estimativa melhorada
        input_text = ' '.join([str(m.get('content', '')) for m in messages])
        estimated_input = len(input_text.encode('utf-8')) // 4  # Aproximação: 4 bytes = 1 token
        
        # Ajustar para tarefas específicas
        task_multiplier = 1.0
        if 'analyze' in config.description.lower():
            task_multiplier = 1.5
        elif 'debug' in config.description.lower():
            task_multiplier = 2.0
        
        input_cost = (estimated_input / 1_000_000) * config.input_price
        output_cost = (max_tokens / 1_000_000) * config.output_price * task_multiplier
        
        return input_cost + output_cost
    
    def _track_usage(self, model_key: str, usage: Any, config: ModelConfig):
        """Registra estatísticas de uso"""
        tokens_in = usage.prompt_tokens
        tokens_out = usage.completion_tokens
        
        cost = (tokens_in / 1_000_000 * config.input_price) + \
               (tokens_out / 1_000_000 * config.output_price)
        
        self.session_stats[model_key]['calls'] += 1
        self.session_stats[model_key]['tokens_in'] += tokens_in
        self.session_stats[model_key]['tokens_out'] += tokens_out
        self.session_stats[model_key]['cost'] += cost
        self.daily_spent += cost
        
        logger.info(f"💰 {model_key}: ${cost:.4f} | {tokens_in:,}+{tokens_out:,} tokens | "
                   f"Total dia: ${self.daily_spent:.2f}")
        
        # Alertas de orçamento
        if not self._budget_warning_shown and self.daily_spent > (self.daily_budget * 0.9):
            logger.warning(f"⚠️ ALERTA: 90% do orçamento diário utilizado!")
            self._budget_warning_shown = True
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas completas"""
        total_cost = sum(s['cost'] for s in self.session_stats.values())
        total_calls = sum(s['calls'] for s in self.session_stats.values())
        
        distribution = {}
        if total_calls > 0:
            for key in self.session_stats:
                pct = (self.session_stats[key]['calls'] / total_calls) * 100
                distribution[key] = round(pct, 1)
        
        # Análise de padrões recentes (últimas 100 chamadas)
        recent_calls = self.call_history[-100:] if len(self.call_history) > 100 else self.call_history
        recent_distribution = {'economy': 0, 'standard': 0, 'deep': 0}
        for call in recent_calls:
            recent_distribution[call['model_key']] += 1
        
        if recent_calls:
            for key in recent_distribution:
                recent_distribution[key] = round((recent_distribution[key] / len(recent_calls)) * 100, 1)
        
        return {
            'by_model': self.session_stats,
            'total_cost_usd': total_cost,
            'total_calls': total_calls,
            'distribution': distribution,
            'recent_distribution': recent_distribution,
            'daily_spent': self.daily_spent,
            'daily_budget': self.daily_budget,
            'budget_remaining': self.daily_budget - self.daily_spent,
            'budget_utilization': (self.daily_spent / self.daily_budget * 100) if self.daily_budget > 0 else 0,
            'projected_monthly': (self.daily_spent * 30),
            'projected_monthly_eur': (self.daily_spent * 30 * 0.93),  # Câmbio aproximado
            'call_history_count': len(self.call_history)
        }
    
    def print_report(self):
        """Imprime relatório formatado"""
        stats = self.get_stats()
        
        print("\n" + "="*70)
        print("📊 RELATÓRIO DE USO - PIRANHAOPS")
        print("="*70)
        
        for model_key, data in stats['by_model'].items():
            if data['calls'] > 0:
                pct = stats['distribution'].get(model_key, 0)
                recent_pct = stats['recent_distribution'].get(model_key, 0)
                print(f"\n🔹 {model_key.upper()} ({pct}% total, {recent_pct}% recente)")
                print(f"   Chamadas: {data['calls']}")
                print(f"   Tokens: {data['tokens_in']:,} in / {data['tokens_out']:,} out")
                print(f"   Custo: ${data['cost']:.3f}")
                if data['calls'] > 0:
                    avg_cost = data['cost'] / data['calls']
                    print(f"   Custo médio: ${avg_cost:.4f}/chamada")
        
        print(f"\n{'='*70}")
        print(f"💵 TOTAL SESSÃO: ${stats['total_cost_usd']:.3f}")
        print(f"📅 TOTAL DIA: ${stats['daily_spent']:.2f} / ${stats['daily_budget']:.2f}")
        print(f"💳 RESTANTE HOJE: ${stats['budget_remaining']:.2f}")
        print(f"📊 UTILIZAÇÃO: {stats['budget_utilization']:.1f}%")
        print(f"📈 PROJEÇÃO MENSAL: ${stats['projected_monthly']:.2f} (~€{stats['projected_monthly_eur']:.2f})")
        print("="*70)
        
        # Alertas de orçamento
        if stats['budget_remaining'] < 0.20:
            print("⚠️  ALERTA: Orçamento diário quase esgotado!")
        elif stats['projected_monthly'] > 40:
            print("⚠️  ALERTA: Projeção mensal acima de €50! Considere otimizar.")
        elif stats['projected_monthly'] < 20:
            print("💡 DICA: Volume baixo, considere aumentar automações")
        
        # Análise de distribuição
        if stats['recent_distribution']:
            economy_pct = stats['recent_distribution'].get('economy', 0)
            if economy_pct < 70:
                print(f"📈 ECONOMY está em {economy_pct}% - abaixo do target 85%")
            elif economy_pct > 90:
                print(f"⚡ ECONOMY está em {economy_pct}% - ótima otimização!")
    
    def reset_daily_stats(self):
        """Reseta estatísticas diárias (para testes)"""
        self.daily_spent = 0.0
        self._budget_warning_shown = False
        logger.info("📊 Estatísticas diárias resetadas")
    
    def get_recommendations(self) -> List[str]:
        """Retorna recomendações baseadas em uso"""
        stats = self.get_stats()
        recommendations = []
        
        # Análise de distribuição
        if stats['recent_distribution'].get('economy', 0) < 80:
            recommendations.append("Aumentar uso de tarefas economy para otimizar custos")
        
        if stats['projected_monthly'] > 35:
            recommendations.append("Considerar redução de tarefas standard/deep")
        
        if stats['budget_utilization'] > 90:
            recommendations.append("Orçamento diário no limite - revisar automações")
        
        if len(self.call_history) > 1000:
            recommendations.append("Volume alto - considerar cache ou otimizações")
        
        return recommendations if recommendations else ["Performance dentro dos parâmetros ideais"]