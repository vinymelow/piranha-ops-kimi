"""
Agente Traffic Manager Pro
Monitora Meta Ads e detecta anomalias com IA
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TrafficManagerPro:
    """
    Agente especializado em monitoramento de tráfego pago
    Implementa fluxo: Economy → Standard → Deep (quando necessário)
    """
    
    def __init__(self, router, mock_client=None):
        self.router = router
        self.mock_client = mock_client  # Para modo mock
        self.alert_threshold_roas = 3.0
        self.alert_threshold_ctr = 1.0
        self.performance_history = []
        
        logger.info("🚦 TrafficManagerPro inicializado")
    
    def analyze(self, date_range: str = "last_7d", use_mock: bool = True, force_scenario: Optional[str] = None) -> Dict:
        """
        Executa análise completa de tráfego
        
        Fluxo otimizado:
        1. Coleta dados (economy) - 85% do uso
        2. Analisa performance (standard) - 15% do uso  
        3. Gera alertas se necessário (standard) - apenas se houver issues
        4. Debug complexo se falhar (deep) - <1% do uso
        
        Args:
            date_range: período de análise
            use_mock: usar simulador ou API real
            force_scenario: forçar cenário específico (crisis/boom/normal)
        """
        print(f"\n{'='*70}")
        print("📊 TRAFFIC MANAGER PRO - ANÁLISE INICIADA")
        print(f"{'='*70}")
        
        start_time = datetime.now()
        
        try:
            # ETAPA 1: Coleta de dados (Economy - 85%)
            print("\n📥 FASE 1: Coletando dados (economy)...")
            raw_data = self._fetch_data(date_range, use_mock, force_scenario)
            
            # ETAPA 2: Análise de performance (Standard - 15%)
            print("\n🧠 FASE 2: Analisando performance (standard)...")
            analysis = self._analyze_performance(raw_data)
            
            # ETAPA 3: Alertas (Standard - apenas se necessário)
            alerts = []
            recommendations = []
            
            if analysis['has_issues']:
                print(f"\n🚨 FASE 3: Gerando alertas (standard)...")
                alerts = self._generate_alerts(analysis)
                recommendations = analysis.get('recommendations', [])
            else:
                print(f"\n✅ Sem issues detectadas - pulando geração de alertas")
            
            # ETAPA 4: Debug complexo (Deep - <1% - apenas se falhar)
            if analysis.get('parse_error'):
                print(f"\n🔧 FASE 4: Debug complexo (deep)...")
                analysis = self._debug_analysis_failure(raw_data)
            
            # Registrar no histórico
            self._record_performance(analysis, alerts)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'date_range': date_range,
                'execution_time_seconds': execution_time,
                'scenario': raw_data.get('scenario', 'unknown'),
                'raw_data_summary': raw_data['summary'],
                'analysis': analysis,
                'alerts': alerts,
                'recommendations': recommendations,
                'cost_breakdown': self._get_cost_breakdown(),
                'model_usage': self.router.get_stats()['distribution']
            }
            
            print(f"\n✅ Análise completa em {execution_time:.1f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro na análise: {e}")
            
            # Fallback: tentar debug com modelo deep
            try:
                print(f"\n🔧 Tentando debug com modelo deep...")
                debug_result = self._emergency_debug(str(e))
                return {
                    'timestamp': datetime.now().isoformat(),
                    'date_range': date_range,
                    'error': str(e),
                    'debug_analysis': debug_result,
                    'status': 'failed_with_debug'
                }
            except Exception as debug_error:
                logger.error(f"❌ Debug também falhou: {debug_error}")
                return {
                    'timestamp': datetime.now().isoformat(),
                    'date_range': date_range,
                    'error': str(e),
                    'status': 'failed'
                }
    
    def _fetch_data(self, date_range: str, use_mock: bool, force_scenario: Optional[str] = None) -> Dict:
        """Coleta dados - Economy mode (85% do uso)"""
        logger.info("📥 Coletando dados do Meta Ads...")
        
        if force_scenario:
            self.mock_client.set_scenario(force_scenario)
        
        if use_mock and self.mock_client:
            # Usar simulador com cenário específico
            data = self.mock_client.get_insights(date_range)
            prompt = f"""
            Formate os seguintes dados de campanhas Meta Ads em JSON estruturado e limpo:
            
            Dados brutos: {json.dumps(data, indent=2)}
            
            Retorne APENAS o JSON formatado com esta estrutura:
            {{
                "campaigns": [...],
                "summary": {{...}},
                "trends": {{...}},
                "issues": [...]
            }}
            
            Remova campos desnecessários, mantenha apenas métricas essenciais.
            """
        else:
            # Modo produção - chamada real API
            prompt = f"""
            Busque dados da API Meta Ads para conta {self.mock_client.account_id if self.mock_client else 'production'}.
            Período: {date_range}
            
            Retorne JSON com:
            - Campanhas ativas: id, nome, status, objetivo
            - Métricas: spend, impressions, clicks, CTR, CPC, conversions, ROAS
            - Resumo agregado
            - Issues detectadas
            
            Formato profissional, dados reais.
            """
        
        response = self.router.call(
            task_type='fetch_meta_data',
            messages=[{"role": "user", "content": prompt.strip()}],
            temperature=0.1,
            max_tokens=2000
        )
        
        # Parse resposta
        content = response.choices[0].message.content.strip()
        
        # Se estiver usando mock, já temos os dados estruturados
        if use_mock:
            # Formatar os dados do mock para garantir consistência
            formatted_data = {
                'campaigns': data['campaigns'],
                'summary': data['summary'],
                'trends': data.get('trends', {}),
                'issues': data.get('issues', []),
                'scenario': data.get('scenario', 'normal'),
                'recommendations': data.get('recommendations', [])
            }
        else:
            try:
                # Tentar parsear JSON da resposta
                formatted_data = json.loads(content)
            except json.JSONDecodeError:
                logger.warning("❌ Falha ao parsear JSON, usando dados brutos")
                formatted_data = {
                    'raw_content': content,
                    'parse_error': True,
                    'campaigns': [],
                    'summary': {},
                    'issues': []
                }
        
        logger.info(f"✅ {formatted_data['summary'].get('total_campaigns', 0)} campanhas coletadas")
        return formatted_data
    
    def _analyze_performance(self, data: Dict) -> Dict:
        """Analisa performance - Standard mode (15% do uso)"""
        logger.info("🧠 Analisando performance com modelo standard...")
        
        campaigns = data.get('campaigns', [])
        issues = data.get('issues', [])
        trends = data.get('trends', {})
        
        if not campaigns:
            return {
                'has_issues': True,
                'error': 'Nenhuma campanha encontrada',
                'recommendations': ['Verificar conexão com Meta Ads']
            }
        
        # Preparar dados para análise
        campaign_data = json.dumps(campaigns[:10], indent=2)  # Limitar para não exceder tokens
        issues_data = json.dumps(issues[:5], indent=2)
        trends_data = json.dumps(trends, indent=2)
        
        prompt = f"""
        Você é um especialista sênior em performance marketing B2B com foco em e-commerce profissional.
        
        ANALISE ESTES DADOS DE CAMPANHAS META ADS:
        
        CAMPANHAS:
        {campaign_data}
        
        ISSUES DETECTADAS:
        {issues_data}
        
        TENDÊNCIAS:
        {trends_data}
        
        BENCHMARKS B2B REFERÊNCIA:
        - ROAS mínimo aceitável: 3.0x
        - CTR saudável: > 1.0%
        - CPC target: < $1.50
        - CPM médio: $8-15
        
        TAREFAS DE ANÁLISE:
        1. Calcule baseline de ROAS e CTR (média das campanhas boas)
        2. Identifique campanhas underperforming (ROAS < 3.0 ou CTR < 1%)
        3. Calcule risco financeiro: spend total em campanhas ruins
        4. Detecte padrões: quedas de CTR, aumento de CPC, etc.
        5. Compare contra benchmarks de e-commerce B2B
        6. Identifique oportunidades de otimização
        7. Priorize ações por impacto vs esforço
        
        RETORNE JSON estruturado:
        {{
            "has_issues": boolean,
            "baseline_roas": float,
            "baseline_ctr": float,
            "underperforming_campaigns": [
                {{
                    "name": string,
                    "issue": string,
                    "current_value": float,
                    "target": float,
                    "spend_impact": float
                }}
            ],
            "risk_financeiro": float,
            "issues_summary": "descrição detalhada dos problemas encontrados",
            "recommendations": [
                "ação prioridade alta",
                "ação prioridade média", 
                "ação prioridade baixa"
            ],
            "opportunities": [
                "oportunidade de scale",
                "oportunidade de otimização"
            ]
        }}
        
        Seja específico, use números reais, seja direto e profissional.
        """
        
        response = self.router.call(
            task_type='analyze_performance',
            messages=[{"role": "user", "content": prompt.strip()}],
            temperature=0.2,
            max_tokens=1500
        )
        
        content = response.choices[0].message.content.strip()
        
        # Extrair JSON da resposta
        try:
            # Tentar parsear direto
            analysis = json.loads(content)
        except json.JSONDecodeError:
            # Extrair JSON de texto com regex
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    analysis = json.loads(json_match.group())
                except:
                    analysis = {
                        'parse_error': True,
                        'raw_response': content[:500],
                        'has_issues': 'CRITICAL' in content.upper() or 'ALERTA' in content.upper()
                    }
            else:
                analysis = {
                    'parse_error': True,
                    'raw_response': content[:200],
                    'has_issues': True
                }
        
        # Garantir campos obrigatórios
        if 'has_issues' not in analysis:
            analysis['has_issues'] = len(analysis.get('underperforming_campaigns', [])) > 0
        
        if 'recommendations' not in analysis:
            analysis['recommendations'] = ['Análise completa disponível no dashboard']
        
        logger.info(f"✅ Análise completa: {len(analysis.get('underperforming_campaigns', []))} campanhas com problemas")
        
        if analysis.get('risk_financeiro', 0) > 100:
            logger.warning(f"💰 Risco financeiro: €{analysis['risk_financeiro']:.2f}")
        
        return analysis
    
    def _generate_alerts(self, analysis: Dict) -> List[Dict]:
        """Gera alertas detalhados - Standard mode"""
        logger.info("🚨 Gerando alertas com modelo standard...")
        
        issues = analysis.get('underperforming_campaigns', [])
        risk = analysis.get('risk_financeiro', 0)
        summary = analysis.get('issues_summary', 'Problemas detectados na análise')
        
        if not issues and risk < 50:
            logger.info("✅ Nenhum alerta crítico necessário")
            return []
        
        prompt = f"""
        Você é gerente de tráfego sênior. Escreva alertas profissionais para o time de marketing.
        
        CONTEXTO:
        - {len(issues)} campanhas com performance abaixo do esperado
        - Risco financeiro: €{risk:.2f} em spend ineficiente
        - Problemas identificados: {summary[:200]}
        
        CRIE ALERTAS NO FORMATO:
        - Nível: CRÍTICO / ALTO / MÉDIO / BAIXO
        - Título: máximo 50 caracteres, direto e impactante
        - Descrição: 2-3 frases com contexto e números específicos
        - Ação imediata: o que fazer agora (máximo 80 caracteres)
        - Meta: resultado esperado da ação
        
        PRIORIDADE:
        1. CRÍTICO: ROAS < 1.5 ou risco > €200
        2. ALTO: ROAS < 2.5 ou CTR < 0.5%
        3. MÉDIO: ROAS < 3.0 ou CTR < 1.0%
        4. BAIXO: otimizações menores
        
        Retorne APENAS uma lista de objetos JSON:
        [
            {{
                "level": "CRÍTICO|ALTO|MÉDIO|BAIXO",
                "title": "Título do alerta",
                "description": "Descrição detalhada",
                "action": "Ação imediata",
                "metric": "métrica afetada",
                "current_value": float,
                "target": float,
                "financial_impact": float
            }}
        ]
        
        Máximo 3 alertas, seja objetivo e profissional.
        """
        
        response = self.router.call(
            task_type='write_alert',
            messages=[{"role": "user", "content": prompt.strip()}],
            temperature=0.3,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse alertas
        try:
            alerts = json.loads(content)
            if not isinstance(alerts, list):
                alerts = [alerts]
        except json.JSONDecodeError:
            # Fallback: criar alertas genéricos baseados nos dados
            alerts = []
            for issue in issues[:2]:  # Máximo 2 alertas
                severity = 'HIGH' if issue.get('current_value', 0) < 2.0 else 'MEDIUM'
                alerts.append({
                    'level': 'CRÍTICO' if severity == 'HIGH' else 'MÉDIO',
                    'title': f"Performance {issue['name']}",
                    'description': f"Campanha {issue['name']} com {issue['issue']}: {issue['current_value']} vs target {issue['target']}",
                    'action': 'Revisar segmentação e criativos',
                    'metric': issue['issue'].lower(),
                    'current_value': issue['current_value'],
                    'target': issue['target'],
                    'financial_impact': issue.get('spend_impact', 0)
                })
        
        # Log alertas
        for alert in alerts:
            emoji = "🚨" if alert['level'] == 'CRÍTICO' else "⚠️" if alert['level'] == 'ALTO' else "💡"
            logger.warning(f"{emoji} ALERTA {alert['level']}: {alert['title']}")
        
        return alerts
    
    def _debug_analysis_failure(self, raw_data: Dict) -> Dict:
        """Debug complexo em caso de falha - Deep mode (<1% do uso)"""
        logger.warning("🔧 Debug complexo de falha de análise...")
        
        prompt = f"""
        DEBUG DE FALHA EM ANÁLISE DE PERFORMANCE
        
        Dados brutos que causaram falha:
        {json.dumps(raw_data, indent=2, default=str)[:1500]}
        
        TENTE:
        1. Identificar por que a análise anterior falhou
        2. Propor correções no formato de dados
        3. Sugerir melhorias no processo de análise
        4. Criar análise alternativa simplificada
        
        RETORNE:
        {{
            "debug_status": "completed",
            "failure_reason": "motivo identificado",
            "suggested_fix": "correção proposta",
            "simple_analysis": {{
                "has_issues": boolean,
                "basic_recommendations": ["rec1", "rec2"]
            }}
        }}
        """
        
        try:
            response = self.router.call(
                task_type='debug_error',
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            # Extrair JSON
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    'debug_status': 'partial',
                    'failure_reason': 'Unable to parse debug response',
                    'simple_analysis': {
                        'has_issues': True,
                        'basic_recommendations': ['Verificar formato dos dados', 'Tentar análise manual']
                    }
                }
                
        except Exception as e:
            logger.error(f"❌ Debug também falhou: {e}")
            return {
                'debug_status': 'failed',
                'failure_reason': str(e),
                'simple_analysis': {
                    'has_issues': True,
                    'basic_recommendations': ['Análise manual necessária']
                }
            }
    
    def _emergency_debug(self, error_message: str) -> Dict:
        """Debug de emergência quando tudo falha"""
        logger.error(f"🚨 Debug de emergência: {error_message}")
        
        return {
            'emergency_analysis': True,
            'error': error_message,
            'recommendations': [
                'Verificar logs completos',
                'Testar conexão com APIs',
                'Reiniciar serviço se necessário',
                'Análise manual recomendada'
            ],
            'status': 'emergency_mode'
        }
    
    def _get_cost_breakdown(self) -> Dict:
        """Retorna breakdown de custos do modelo"""
        stats = self.router.get_stats()
        return {
            'economy_cost': stats['by_model']['economy']['cost'],
            'standard_cost': stats['by_model']['standard']['cost'],
            'deep_cost': stats['by_model']['deep']['cost'],
            'total_cost': stats['total_cost_usd'],
            'budget_used': stats['daily_spent'],
            'budget_remaining': stats['budget_remaining']
        }
    
    def _record_performance(self, analysis: Dict, alerts: List[Dict]):
        """Registra performance para análise histórica"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'has_issues': analysis.get('has_issues', False),
            'num_alerts': len(alerts),
            'risk_financeiro': analysis.get('risk_financeiro', 0),
            'baseline_roas': analysis.get('baseline_roas', 0),
            'num_underperforming': len(analysis.get('underperforming_campaigns', []))
        }
        
        self.performance_history.append(record)
        
        # Manter apenas últimos 100 registros
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]
    
    def get_performance_trends(self) -> Dict:
        """Retorna tendências de performance histórica"""
        if not self.performance_history:
            return {'message': 'Sem dados históricos'}
        
        recent = self.performance_history[-10:]  # Últimos 10 ciclos
        
        trends = {
            'total_cycles': len(self.performance_history),
            'recent_avg_issues': sum(p['has_issues'] for p in recent) / len(recent),
            'recent_avg_alerts': sum(p['num_alerts'] for p in recent) / len(recent),
            'recent_avg_risk': sum(p['risk_financeiro'] for p in recent) / len(recent),
            'trend_direction': 'improving' if recent[-1]['num_alerts'] < recent[0]['num_alerts'] else 'worsening'
        }
        
        return trends
    
    def generate_weekly_report(self) -> Dict:
        """Gera relatório semanal completo"""
        trends = self.get_performance_trends()
        router_stats = self.router.get_stats()
        
        return {
            'period': 'last_7_days',
            'performance_trends': trends,
            'cost_analysis': {
                'total_spent': router_stats['total_cost_usd'],
                'daily_average': router_stats['daily_spent'],
                'budget_utilization': router_stats['budget_utilization']
            },
            'model_distribution': router_stats['distribution'],
            'recommendations': self.router.get_recommendations()
        }