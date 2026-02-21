#!/usr/bin/env python3
"""
PiranhaOps - Sistema de Operações B2B com IA
Versão: 1.0.0 (Mock Mode)
Orquestrador principal que integra todos os componentes
"""

import os
import sys
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Adicionar diretórios ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config.settings import Settings
    from core.model_router import ModelRouter
    from integrations.meta_ads_mock import MetaAdsMock
    from agents.traffic_manager import TrafficManagerPro
    from core.data_store import DataStore  # Adicionado para persistência
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Certifique-se de que todos os arquivos estão nos diretórios corretos")
    sys.exit(1)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('piranha_ops.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PiranhaOps:
    """
    Sistema principal de orquestração
    Integra ModelRouter, MetaAdsMock e TrafficManagerPro
    """
    
    def __init__(self):
        print("🚀 Inicializando PiranhaOps v1.0.0...")
        
        # Configurações
        try:
            self.config = Settings.from_env()
            self.config.validate()
            print(f"   ✅ Configurações carregadas - Modo: {self.config.MODE}")
        except Exception as e:
            print(f"   ❌ Erro nas configurações: {e}")
            sys.exit(1)
        
        print(f"   💰 Budget diário: ${self.config.BUDGET_DAILY_USD}")
        print(f"   ⏰ Intervalo: {self.config.CHECK_INTERVAL_MINUTES} minutos")
        
        # Cliente Moonshot
        try:
            if self.config.is_mock() or not self.config.MOONSHOT_API_KEY:
                # Modo mock ou sem API key
                print("   ⚠️  Modo mock/simulação ativado")
                self.client = None
            else:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=self.config.MOONSHOT_API_KEY,
                    base_url=self.config.MOONSHOT_BASE_URL
                )
                print("   ✅ API Moonshot conectada")
        except Exception as e:
            print(f"   ⚠️  API Moonshot não disponível: {e}")
            print("   📝 Continuando em modo simulação...")
            self.client = None
        
        # Roteador de modelos
        self.router = ModelRouter(self.client, self.config.BUDGET_DAILY_USD)
        print("   ✅ ModelRouter inicializado")
        
        # Integrações mock
        self.meta_mock = MetaAdsMock(self.config.META_AD_ACCOUNT_ID)
        print("   ✅ MetaAdsMock inicializado")
        
        # Agentes
        self.traffic_manager = TrafficManagerPro(self.router, self.meta_mock)
        print("   ✅ TrafficManagerPro inicializado")
        
        # Persistência de dados
        self.store = DataStore()
        print("   ✅ DataStore inicializado para baseline e histórico")
        
        # Estado do sistema
        self.is_running = False
        self.cycle_count = 0
        self.start_time = None
        
        print("\n✅ Sistema PiranhaOps pronto!")
        print("=" * 70)
    
    def run_demo(self):
        """Executa demonstração completa com 3 cenários"""
        print("\n" + "="*70)
        print("🎭 DEMO PIRANHAOPS - 3 CENÁRIOS DE TESTE")
        print("="*70)
        print("Este demo vai testar:")
        print("  ✅ Sistema de roteamento 85% economy / 15% standard / <1% deep")
        print("  ✅ Detecção de anomalias em diferentes cenários")
        print("  ✅ Geração de alertas inteligentes")
        print("  ✅ Cálculo de custos e orçamento")
        print("  ✅ Fluxo Economy → Standard → Deep")
        print()
        
        scenarios = [
            ('normal', 'Operação Normal', 'Performance dentro dos padrões esperados'),
            ('crisis', 'Crise de Performance', 'Múltiplas campanhas underperforming - esperado: alertas'),
            ('boom', 'Performance Excelente', 'Todas as campanhas acima do target')
        ]
        
        results = []
        
        for i, (scenario, title, description) in enumerate(scenarios, 1):
            print(f"\n{'='*70}")
            print(f"CENÁRIO {i}: {title}")
            print(f"Descrição: {description}")
            print(f"{'='*70}")
            
            try:
                # Resetar estatísticas para cenário limpo
                self.router.reset_daily_stats()
                
                # Executar análise
                result = self.traffic_manager.analyze(
                    date_range="last_7d",
                    use_mock=True,
                    force_scenario=scenario
                )
                
                results.append(result)
                self._print_demo_result(result, title)
                
                # 💾 Persistir dados para baseline histórico
                print(f"  💾 Salvando dados para baseline...")
                self.store.save_campaign_snapshot({
                    'summary': result['raw_data_summary'],
                    'campaigns': result.get('raw_data', {}).get('campaigns', []),
                    'scenario': scenario
                })
                
                # 🚨 Persistir alertas
                for alert in result.get('alerts', []):
                    self.store.save_alert(alert)
                
                print(f"  ✅ Dados salvos com sucesso!")
                
                # Pequena pausa entre cenários
                if i < len(scenarios):
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"❌ Erro no cenário {scenario}: {e}")
                print(f"❌ Erro no cenário {scenario}: {e}")
        
        # Relatório final consolidado
        self._print_demo_summary(results)
        
        print("\n✅ Demo completo!")
        print("💡 Próximo passo: Obter chaves reais e trocar MODE=production no .env")
        print("📝 Arquivo de log criado: piranha_ops.log")
    
    def _print_demo_result(self, result: dict, scenario_title: str):
        """Imprime resultado do demo formatado"""
        print(f"\n📅 Timestamp: {result['timestamp']}")
        print(f"📊 Campanhas: {result['raw_data_summary']['total_campaigns']}")
        print(f"💰 Spend total: €{result['raw_data_summary']['total_spend']}")
        print(f"📈 ROAS médio: {result['raw_data_summary']['avg_roas']}")
        print(f"🎯 CTR médio: {result['raw_data_summary']['avg_ctr']}%")
        print(f"⏱️  Tempo de análise: {result['execution_time_seconds']:.1f}s")
        
        # Custo da análise
        cost_breakdown = result.get('cost_breakdown', {})
        print(f"💸 Custo da análise: ${cost_breakdown.get('total_cost', 0):.4f}")
        
        # Uso de modelos
        model_usage = result.get('model_usage', {})
        if model_usage:
            print(f"🎯 Uso de modelos: Economy {model_usage.get('economy', 0)}% | "
                  f"Standard {model_usage.get('standard', 0)}% | "
                  f"Deep {model_usage.get('deep', 0)}%")
        
        if result['alerts']:
            print(f"\n🚨 ALERTAS ({len(result['alerts'])}):")
            for alert in result['alerts']:
                emoji = "🚨" if alert['level'] == 'CRÍTICO' else "⚠️"
                print(f"   {emoji} [{alert['level']}] {alert['title']}")
                print(f"      → {alert['action']}")
                if alert.get('financial_impact'):
                    print(f"      💰 Impacto: €{alert['financial_impact']:.2f}")
        
        # 💾 Persistir dados reais para baseline histórico
        try:
            print(f"  💾 Salvando dados para baseline...")
            self.store.save_campaign_snapshot({
                'summary': result.get('raw_data_summary', {}),
                'campaigns': result.get('raw_data', {}).get('campaigns', []),
                'scenario': result.get('scenario', 'production')
            })
            
            # 🚨 Persistir alertas
            for alert in result.get('alerts', []):
                self.store.save_alert(alert)
            
            # 📊 Mostrar baseline atual
            baseline = self.store.get_baseline(7)
            print(f"  📊 Baseline atual: ROAS {baseline['metrics']['roas']:.2f}x | CTR {baseline['metrics']['ctr']:.2f}%")
            
            print(f"  ✅ Dados salvos com sucesso!")
            
        except Exception as store_error:
            logger.warning(f"⚠️ Erro ao salvar dados: {store_error}")
            print(f"  ⚠️ Erro ao salvar dados: {store_error}")
        else:
            print(f"\n✅ Nenhum alerta - performance dentro dos parâmetros")
        
        if result['recommendations']:
            print(f"\n💡 Recomendações:")
            for i, rec in enumerate(result['recommendations'][:3], 1):
                print(f"   {i}. {rec}")
    
    def _print_demo_summary(self, results: List[Dict]):
        """Imprime relatório final consolidado"""
        print("\n" + "="*70)
        print("📊 RELATÓRIO FINAL CONSOLIDADO")
        print("="*70)
        
        # Estatísticas gerais
        total_cost = sum(r.get('cost_breakdown', {}).get('total_cost', 0) for r in results)
        total_alerts = sum(len(r.get('alerts', [])) for r in results)
        total_campaigns = sum(r.get('raw_data_summary', {}).get('total_campaigns', 0) for r in results)
        
        print(f"📈 Total de campanhas analisadas: {total_campaigns}")
        print(f"🚨 Total de alertas gerados: {total_alerts}")
        print(f"💰 Custo total do demo: ${total_cost:.4f}")
        
        # Relatório do roteador
        print(f"\n📊 DESEMPENHO DO ROUTER:")
        self.router.print_report()
        
        # Verificar distribuição 85/15/<1%
        stats = self.router.get_stats()
        distribution = stats.get('distribution', {})
        
        print(f"\n🎯 DISTRIBUIÇÃO DE MODELOS:")
        economy_pct = distribution.get('economy', 0)
        standard_pct = distribution.get('standard', 0)
        deep_pct = distribution.get('deep', 0)
        
        print(f"   Economy: {economy_pct}% {'✅' if 80 <= economy_pct <= 90 else '⚠️'}")
        print(f"   Standard: {standard_pct}% {'✅' if 10 <= standard_pct <= 20 else '⚠️'}")
        print(f"   Deep: {deep_pct}% {'✅' if deep_pct <= 5 else '⚠️'}")
        
        # 📊 Baseline calculado
        baseline = self.store.get_baseline(7)
        print(f"\n📊 BASELINE CALCULADO ({baseline['period_days']} dias):")
        print(f"   ROAS: {baseline['metrics']['roas']:.2f}x")
        print(f"   CTR: {baseline['metrics']['ctr']:.2f}%")
        print(f"   CPC: €{baseline['metrics']['cpc']:.2f}")
        print(f"   Campanhas analisadas: {baseline['total_campaigns']}")
        
        # Thresholds
        print(f"\n⚠️  THRESHOLDS DE ALERTA:")
        print(f"   ROAS Crítico: < {baseline['thresholds']['roas_critical']:.2f}x")
        print(f"   ROAS Atenção: < {baseline['thresholds']['roas_warning']:.2f}x")
        print(f"   CTR Crítico: < {baseline['thresholds']['ctr_critical']:.2f}%")
        print(f"   CTR Atenção: < {baseline['thresholds']['ctr_warning']:.2f}%")
        
        # Recomendações finais
        recommendations = self.router.get_recommendations()
        if recommendations:
            print(f"\n💡 RECOMENDAÇÕES DE OTIMIZAÇÃO:")
            for rec in recommendations:
                print(f"   • {rec}")
    
    def run_monitoring(self):
        """Executa monitoramento contínuo (para produção)"""
        try:
            import schedule
        except ImportError:
            print("❌ Biblioteca 'schedule' não instalada")
            print("Instale com: pip install schedule")
            return
        
        print("\n" + "="*70)
        print("🔁 INICIANDO MONITORAMENTO CONTÍNUO")
        print("="*70)
        print(f"Modo: {self.config.MODE}")
        print(f"Intervalo: {self.config.CHECK_INTERVAL_MINUTES} minutos")
        print(f"Budget: ${self.config.BUDGET_DAILY_USD}/dia")
        print("\n⚡ Pressione Ctrl+C para parar")
        print("="*70)
        
        self.is_running = True
        self.start_time = datetime.now()
        self.cycle_count = 0
        
        # Agendar execução
        schedule.every(self.config.CHECK_INTERVAL_MINUTES).minutes.do(self._monitoring_cycle)
        
        # Primeira execução imediata
        print("\n🚀 Executando primeiro ciclo...")
        self._monitoring_cycle()
        
        # Loop principal
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Verificar a cada minuto
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoramento interrompido pelo usuário")
            self._print_final_report()
    
    def _monitoring_cycle(self):
        """Ciclo único de monitoramento"""
        self.cycle_count += 1
        cycle_start = datetime.now()
        
        print(f"\n{'='*70}")
        print(f"🔄 CICLO #{self.cycle_count} - {cycle_start.strftime('%H:%M:%S')}")
        print(f"{'='*70}")
        
        try:
            # Executar análise
            result = self.traffic_manager.analyze(
                date_range="last_7d",
                use_mock=self.config.is_mock()
            )
            
            # Processar resultados
            self._process_monitoring_results(result)
            
            # Salvar em arquivo para histórico
            self._save_cycle_result(result)
            
            # Mostrar resumo
            execution_time = result.get('execution_time_seconds', 0)
            cost = result.get('cost_breakdown', {}).get('total_cost', 0)
            alerts = len(result.get('alerts', []))
            
            print(f"✅ Ciclo completo em {execution_time:.1f}s")
            print(f"💰 Custo: ${cost:.4f}")
            print(f"🚨 Alertas: {alerts}")
            
            # Mostrar status do orçamento
            stats = self.router.get_stats()
            print(f"💳 Budget: ${stats['daily_spent']:.2f} / ${stats['daily_budget']:.2f}")
            
            # Enviar notificações se necessário
            if alerts > 0:
                self._send_notifications(result['alerts'])
            
        except Exception as e:
            logger.error(f"❌ Erro no ciclo {self.cycle_count}: {e}")
            print(f"❌ Erro: {e}")
            
            # Tentar recuperação
            try:
                self._emergency_recovery()
            except Exception as recovery_error:
                logger.error(f"❌ Recuperação falhou: {recovery_error}")
    
    def _process_monitoring_results(self, result: Dict):
        """Processa resultados do monitoramento"""
        alerts = result.get('alerts', [])
        
        if alerts:
            print(f"\n🚨 ALERTAS DETECTADOS ({len(alerts)}):")
            for alert in alerts:
                level_emoji = {
                    'CRÍTICO': '🚨',
                    'ALTO': '⚠️',
                    'MÉDIO': '💡',
                    'BAIXO': 'ℹ️'
                }.get(alert['level'], '•')
                
                print(f"   {level_emoji} [{alert['level']}] {alert['title']}")
                
                if alert.get('financial_impact'):
                    print(f"      💰 Impacto: €{alert['financial_impact']:.2f}")
        
        # Recomendações
        recommendations = result.get('recommendations', [])
        if recommendations:
            print(f"\n💡 RECOMENDAÇÕES:")
            for i, rec in enumerate(recommendations[:2], 1):
                print(f"   {i}. {rec}")
    
    def _save_cycle_result(self, result: Dict):
        """Salva resultado do ciclo em arquivo"""
        try:
            # Criar diretório se não existir
            os.makedirs('logs', exist_ok=True)
            
            filename = f"logs/cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Salvar apenas dados essenciais
            essential_data = {
                'timestamp': result['timestamp'],
                'cycle': self.cycle_count,
                'alerts_count': len(result.get('alerts', [])),
                'cost': result.get('cost_breakdown', {}).get('total_cost', 0),
                'execution_time': result.get('execution_time_seconds', 0),
                'scenario': result.get('scenario', 'unknown')
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(essential_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"❌ Erro ao salvar ciclo: {e}")
    
    def _send_notifications(self, alerts: List[Dict]):
        """Envia notificações (placeholder para integração real)"""
        critical_alerts = [a for a in alerts if a['level'] == 'CRÍTICO']
        
        if critical_alerts:
            print(f"\n📢 ENVIANDO NOTIFICAÇÕES:")
            print(f"   🚨 {len(critical_alerts)} alertas críticos para notificar")
            
            # Aqui você implementaria:
            # - Envio para Slack
            # - Envio para email
            # - Envio para WhatsApp
            # - Dashboard update
            
            # Por enquanto, apenas log
            for alert in critical_alerts:
                logger.critical(f"ALERTA CRÍTICO: {alert['title']} - {alert['description']}")
    
    def _emergency_recovery(self):
        """Procedimento de recuperação de emergência"""
        logger.warning("🔄 Executando recuperação de emergência...")
        
        # Resetar roteador
        try:
            self.router.reset_daily_stats()
            logger.info("✅ Roteador resetado")
        except Exception as e:
            logger.error(f"❌ Falha ao resetar roteador: {e}")
        
        # Tentar análise simplificada
        try:
            simple_result = self.traffic_manager.analyze(
                date_range="yesterday",
                use_mock=True,
                force_scenario='normal'
            )
            logger.info("✅ Análise simplificada concluída")
            return simple_result
        except Exception as e:
            logger.error(f"❌ Análise simplificada falhou: {e}")
            return None
    
    def _print_final_report(self):
        """Imprime relatório final quando parar"""
        print("\n" + "="*70)
        print("📊 RELATÓRIO FINAL DO MONITORAMENTO")
        print("="*70)
        
        if self.start_time:
            duration = datetime.now() - self.start_time
            print(f"⏰ Duração total: {duration}")
        
        print(f"🔄 Ciclos executados: {self.cycle_count}")
        
        # Estatísticas finais do roteador
        self.router.print_report()
        
        # Tendências de performance
        trends = self.traffic_manager.get_performance_trends()
        if trends and 'recent_avg_alerts' in trends:
            print(f"📈 Média de alertas por ciclo: {trends['recent_avg_alerts']:.1f}")
            print(f"📊 Tendência: {trends.get('trend_direction', 'unknown')}")
        
        print("\n👋 Obrigado por usar PiranhaOps!")
        print("="*70)
    
    def generate_weekly_report(self) -> Dict:
        """Gera relatório semanal completo"""
        print("\n📈 Gerando relatório semanal...")
        
        return self.traffic_manager.generate_weekly_report()
    
    def get_system_status(self) -> Dict:
        """Retorna status completo do sistema"""
        router_stats = self.router.get_stats()
        trends = self.traffic_manager.get_performance_trends()
        
        return {
            'system': {
                'version': '1.0.0',
                'mode': self.config.MODE,
                'is_running': self.is_running,
                'cycle_count': self.cycle_count,
                'uptime': str(datetime.now() - self.start_time) if self.start_time else 'stopped'
            },
            'budget': {
                'daily_budget': self.config.BUDGET_DAILY_USD,
                'daily_spent': router_stats['daily_spent'],
                'budget_remaining': router_stats['budget_remaining'],
                'budget_utilization': router_stats['budget_utilization']
            },
            'models': {
                'distribution': router_stats['distribution'],
                'recent_distribution': router_stats['recent_distribution'],
                'total_cost': router_stats['total_cost_usd']
            },
            'performance': trends,
            'recommendations': self.router.get_recommendations()
        }

def main():
    """Função principal"""
    print("\n" + "="*70)
    print("🚀 PIRANHAOPS - SISTEMA DE OPERAÇÕES B2B COM IA")
    print("="*70)
    print("Versão 1.0.0 | Modo Mock Ativado")
    print("="*70)
    
    try:
        ops = PiranhaOps()
    except Exception as e:
        print(f"\n❌ Falha na inicialização: {e}")
        sys.exit(1)
    
    # Menu interativo
    while True:
        print("\n" + "="*70)
        print("PIRANHAOPS - MENU PRINCIPAL")
        print("="*70)
        print("1. 🎭 Executar DEMO (3 cenários de teste)")
        print("2. 🔁 Iniciar monitoramento contínuo")
        print("3. 📊 Gerar relatório semanal")
        print("4. ⚙️  Ver status do sistema")
        print("5. 🧪 Executar testes rápidos")
        print("6. 🚪 Sair")
        print("="*70)
        
        try:
            choice = input("\nEscolha (1-6): ").strip()
            
            if choice == '1':
                ops.run_demo()
            elif choice == '2':
                ops.run_monitoring()
            elif choice == '3':
                report = ops.generate_weekly_report()
                print(f"\n📊 Relatório Semanal:")
                print(json.dumps(report, indent=2, ensure_ascii=False))
            elif choice == '4':
                status = ops.get_system_status()
                print(f"\n⚙️  Status do Sistema:")
                print(json.dumps(status, indent=2, ensure_ascii=False))
            elif choice == '5':
                _run_quick_tests(ops)
            elif choice == '6':
                print("\n👋 Até logo!")
                break
            else:
                print("\n❌ Opção inválida. Tente novamente.")
                
        except KeyboardInterrupt:
            print("\n\n🛑 Interrompido pelo usuário")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            logger.error(f"Erro no menu: {e}")

def _run_quick_tests(ops: PiranhaOps):
    """Executa testes rápidos do sistema"""
    print("\n🧪 EXECUTANDO TESTES RÁPIDOS...")
    
    tests_passed = 0
    tests_total = 0
    
    # Teste 1: Configurações
    tests_total += 1
    try:
        assert ops.config.is_mock() == True
        assert ops.config.BUDGET_DAILY_USD > 0
        print("✅ Teste 1: Configurações - PASSOU")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Teste 1: Configurações - FALHOU: {e}")
    
    # Teste 2: Roteador
    tests_total += 1
    try:
        stats = ops.router.get_stats()
        assert 'distribution' in stats
        print("✅ Teste 2: ModelRouter - PASSOU")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Teste 2: ModelRouter - FALHOU: {e}")
    
    # Teste 3: Meta Mock
    tests_total += 1
    try:
        data = ops.meta_mock.get_insights()
        assert 'campaigns' in data
        assert len(data['campaigns']) > 0
        print("✅ Teste 3: MetaAdsMock - PASSOU")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Teste 3: MetaAdsMock - FALHOU: {e}")
    
    # Teste 4: Traffic Manager
    tests_total += 1
    try:
        result = ops.traffic_manager.analyze(use_mock=True, force_scenario='normal')
        assert 'analysis' in result
        print("✅ Teste 4: TrafficManagerPro - PASSOU")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Teste 4: TrafficManagerPro - FALHOU: {e}")
    
    print(f"\n📊 RESULTADO DOS TESTES: {tests_passed}/{tests_total} passaram")
    
    if tests_passed == tests_total:
        print("🎉 Todos os testes passaram! Sistema operacional.")
    else:
        print("⚠️  Alguns testes falharam. Verifique os logs.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 PiranhaOps finalizado pelo usuário")
    except Exception as e:
        print(f"\n💥 Erro fatal: {e}")
        logger.critical(f"Erro fatal no sistema: {e}")
        sys.exit(1)