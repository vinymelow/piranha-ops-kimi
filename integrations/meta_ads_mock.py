"""
Simulador de Meta Ads para desenvolvimento
Gera dados realistas sem precisar de API key real
"""

import random
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class Campaign:
    """Campanha simulada com métricas realistas"""
    id: str
    name: str
    status: str
    objective: str
    spend: float
    impressions: int
    clicks: int
    conversions: int
    roas: float
    cpc: float
    ctr: float
    cpm: float
    purchase_roas: float
    cost_per_conversion: float
    date_start: str
    date_stop: str
    
    @property
    def frequency(self) -> float:
        return round(self.impressions / max(self.clicks, 1), 2)
    
    @property
    def conversion_rate(self) -> float:
        return round((self.conversions / max(self.clicks, 1)) * 100, 2)
    
    def to_dict(self) -> Dict:
        """Converte para dicionário incluindo propriedades calculadas"""
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'objective': self.objective,
            'spend': self.spend,
            'impressions': self.impressions,
            'clicks': self.clicks,
            'conversions': self.conversions,
            'roas': self.roas,
            'cpc': self.cpc,
            'ctr': self.ctr,
            'cpm': self.cpm,
            'purchase_roas': self.purchase_roas,
            'cost_per_conversion': self.cost_per_conversion,
            'date_start': self.date_start,
            'date_stop': self.date_stop,
            'conversion_rate': self.conversion_rate,
            'frequency': self.frequency
        }

@dataclass
class AdSet:
    """Conjunto de anúncios simulado"""
    id: str
    name: str
    campaign_id: str
    targeting: Dict
    status: str
    budget: float
    spend: float
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'campaign_id': self.campaign_id,
            'targeting': self.targeting,
            'status': self.status,
            'budget': self.budget,
            'spend': self.spend
        }

class MetaAdsMock:
    """
    Simulador de API do Meta Ads com cenários realistas
    Gera dados com variações sazonais e comportamentos reais
    """
    
    # Templates realistas de campanhas B2B
    CAMPAIGN_TEMPLATES = [
        {"name": "Black Ink Premium - Awareness", "objective": "BRAND_AWARENESS", "base_spend": 150},
        {"name": "Needles Pro Kit - Conversion", "objective": "CONVERSIONS", "base_spend": 200},
        {"name": "Tattoo Machines - Retargeting", "objective": "CONVERSIONS", "base_spend": 180},
        {"name": "Supplies B2B - Lookalike", "objective": "LEAD_GENERATION", "base_spend": 120},
        {"name": "Flash Sale Q1 - Dynamic", "objective": "CONVERSIONS", "base_spend": 300},
        {"name": "Artist Essentials - Catalog", "objective": "CONVERSIONS", "base_spend": 220},
        {"name": "Wholesale Deal - Messages", "objective": "MESSAGES", "base_spend": 80},
        {"name": "Professional Tools - Traffic", "objective": "TRAFFIC", "base_spend": 160},
        {"name": "Ink Collection - Reach", "objective": "REACH", "base_spend": 140},
        {"name": "Equipment Promo - Sales", "objective": "SALES", "base_spend": 250}
    ]
    
    # Benchmarks por objetivo (baseados em dados reais B2B)
    BENCHMARKS = {
        'BRAND_AWARENESS': {'ctr': 1.2, 'cpc': 0.45, 'roas': 1.5, 'cpm': 8.5},
        'CONVERSIONS': {'ctr': 1.8, 'cpc': 0.65, 'roas': 3.2, 'cpm': 12.0},
        'LEAD_GENERATION': {'ctr': 2.1, 'cpc': 0.55, 'roas': 2.8, 'cpm': 10.5},
        'MESSAGES': {'ctr': 2.5, 'cpc': 0.35, 'roas': 2.2, 'cpm': 7.8},
        'TRAFFIC': {'ctr': 1.5, 'cpc': 0.40, 'roas': 2.0, 'cpm': 9.2},
        'REACH': {'ctr': 1.0, 'cpc': 0.50, 'roas': 1.8, 'cpm': 7.0},
        'SALES': {'ctr': 2.0, 'cpc': 0.70, 'roas': 4.0, 'cpm': 14.0}
    }
    
    def __init__(self, account_id: str = "act_mock_12345"):
        self.account_id = account_id
        self.random_seed = random.Random(42)  # Seed fixo para reproducibilidade
        self.scenario = 'normal'  # normal, crisis, boom, seasonal
        self.date_range = 7  # dias padrão
        self._campaign_counter = 0
        
        logger.info(f"🎭 MetaAdsMock inicializado - Conta: {account_id}")
    
    def set_scenario(self, scenario: str, date_range: int = 7):
        """Define cenário de teste: normal, crisis, boom, seasonal"""
        self.scenario = scenario
        self.date_range = date_range
        logger.info(f"🎭 Cenário definido: {scenario} ({date_range} dias)")
    
    def get_insights(self, date_preset: str = "last_7d", level: str = "campaign") -> Dict:
        """
        Retorna insights simulados com dados realistas
        
        Args:
            date_preset: período (last_7d, last_30d, today, yesterday)
            level: nível de granularidade (campaign, adset, ad)
        """
        # Determinar número de campanhas baseado no cenário
        if self.scenario == 'crisis':
            num_campaigns = self.random_seed.randint(3, 6)  # Menos campanhas em crise
        elif self.scenario == 'boom':
            num_campaigns = self.random_seed.randint(8, 12)  # Mais campanhas em boom
        else:
            num_campaigns = self.random_seed.randint(5, 10)  # Normal
        
        campaigns = []
        total_spend = 0
        
        # Gerar campanhas
        for i in range(num_campaigns):
            campaign = self._generate_campaign(i)
            campaigns.append(campaign.to_dict())  # Usar método to_dict em vez de asdict
            total_spend += campaign.spend
        
        # Calcular agregados
        total_impressions = sum(c['impressions'] for c in campaigns)
        total_clicks = sum(c['clicks'] for c in campaigns)
        total_conversions = sum(c['conversions'] for c in campaigns)
        
        # Criar resumo executivo
        summary = {
            'total_campaigns': len(campaigns),
            'total_spend': round(total_spend, 2),
            'total_impressions': total_impressions,
            'total_clicks': total_clicks,
            'total_conversions': total_conversions,
            'avg_roas': round(sum(c['roas'] for c in campaigns) / len(campaigns), 2) if campaigns else 0,
            'avg_ctr': round(sum(c['ctr'] for c in campaigns) / len(campaigns), 2) if campaigns else 0,
            'avg_cpc': round(sum(c['cpc'] for c in campaigns) / len(campaigns), 2) if campaigns else 0,
            'avg_cpm': round(sum(c['cpm'] for c in campaigns) / len(campaigns), 2) if campaigns else 0,
            'scenario': self.scenario,
            'date_range': self.date_range,
            'generated_at': datetime.now().isoformat()
        }
        
        # Adicionar análise de tendências
        trends = self._generate_trends(campaigns)
        
        # Detectar problemas
        issues = self._detect_issues(campaigns)
        
        return {
            'success': True,
            'account_id': self.account_id,
            'date_preset': date_preset,
            'level': level,
            'campaigns': campaigns,
            'summary': summary,
            'trends': trends,
            'issues': issues,
            'recommendations': self._generate_recommendations(campaigns, issues)
        }
    
    def _generate_campaign(self, index: int) -> Campaign:
        """Gera uma campanha simulada baseada no cenário"""
        
        # Selecionar template
        template = self.CAMPAIGN_TEMPLATES[index % len(self.CAMPAIGN_TEMPLATES)]
        objective = template['objective']
        base_spend = template['base_spend']
        benchmark = self.BENCHMARKS[objective]
        
        # Ajustar baseado no cenário
        if self.scenario == 'crisis':
            # Cenário crise: performance ruim
            spend_multiplier = self.random_seed.uniform(0.7, 1.3)
            performance_multiplier = self.random_seed.uniform(0.4, 0.8)  # Performance ruim
            crisis_factor = self.random_seed.uniform(0.5, 0.8)  # Reduz ROAS e CTR
        elif self.scenario == 'boom':
            # Cenário bom: performance excelente
            spend_multiplier = self.random_seed.uniform(1.2, 2.0)
            performance_multiplier = self.random_seed.uniform(1.3, 1.8)  # Performance boa
            boom_factor = self.random_seed.uniform(1.2, 1.6)  # Aumenta ROAS e CTR
        else:  # normal
            # Cenário normal: variado
            spend_multiplier = self.random_seed.uniform(0.8, 1.5)
            performance_multiplier = self.random_seed.uniform(0.8, 1.3)
        
        # Gerar valores base
        spend = round(base_spend * spend_multiplier, 2)
        
        # Impressões baseadas em spend e CPM
        cpm = benchmark['cpm']
        if self.scenario == 'crisis':
            cpm *= crisis_factor
        elif self.scenario == 'boom':
            cpm *= boom_factor
        
        impressions = int((spend / (cpm / 1000)) * self.random_seed.uniform(0.8, 1.2))
        
        # Clicks baseados em CTR
        ctr = benchmark['ctr']
        if self.scenario == 'crisis':
            ctr *= crisis_factor
        elif self.scenario == 'boom':
            ctr *= boom_factor
        
        clicks = int(impressions * (ctr / 100) * self.random_seed.uniform(0.7, 1.3))
        clicks = max(1, clicks)  # Garantir pelo menos 1 click
        
        # Conversions baseadas em taxa de conversão
        conversion_rate = self.random_seed.uniform(1.5, 4.5)  # B2B typical
        if self.scenario == 'crisis':
            conversion_rate *= crisis_factor
        elif self.scenario == 'boom':
            conversion_rate *= boom_factor
        
        conversions = int(clicks * (conversion_rate / 100))
        conversions = max(0, conversions)
        
        # Calcular métricas derivadas
        cpc = spend / clicks if clicks > 0 else 0
        roas = self.random_seed.uniform(1.5, 4.5) * performance_multiplier
        
        # Ajustar ROAS baseado em conversions
        if conversions > 0:
            conversion_value = self.random_seed.uniform(80, 250)  # Valor médio B2B
            total_conversion_value = conversions * conversion_value
            roas = total_conversion_value / spend
        
        # Algumas campanhas sempre problemáticas (realista)
        if index % 4 == 0:  # 25% das campanhas são problemáticas
            roas *= self.random_seed.uniform(0.4, 0.7)
            ctr *= self.random_seed.uniform(0.5, 0.8)
        
        # Gerar datas
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=self.date_range - 1)
        
        return Campaign(
            id=f"{self.account_id}:campaign_{index}_{self.random_seed.randint(1000, 9999)}",
            name=template['name'],
            status=self.random_seed.choices(['ACTIVE', 'PAUSED'], weights=[0.8, 0.2])[0],
            objective=objective,
            spend=round(spend, 2),
            impressions=impressions,
            clicks=clicks,
            conversions=conversions,
            roas=round(roas, 2),
            cpc=round(cpc, 2),
            ctr=round(ctr, 2),
            cpm=round(cpm, 2),
            purchase_roas=round(roas * self.random_seed.uniform(0.8, 1.2), 2),
            cost_per_conversion=round(spend / max(conversions, 1), 2),
            date_start=start_date.isoformat(),
            date_stop=end_date.isoformat()
        )
    
    def _generate_trends(self, campaigns: List[Dict]) -> Dict:
        """Gera análise de tendências"""
        if not campaigns:
            return {}
        
        # Calcular tendências simples
        roas_values = [c['roas'] for c in campaigns]
        ctr_values = [c['ctr'] for c in campaigns]
        spend_values = [c['spend'] for c in campaigns]
        
        # Detectar tendências
        avg_roas = sum(roas_values) / len(roas_values)
        avg_ctr = sum(ctr_values) / len(ctr_values)
        total_spend = sum(spend_values)
        
        # Identificar outliers
        roas_outliers = [c for c in campaigns if c['roas'] < avg_roas * 0.5 or c['roas'] > avg_roas * 2]
        ctr_outliers = [c for c in campaigns if c['ctr'] < avg_ctr * 0.3 or c['ctr'] > avg_ctr * 3]
        
        return {
            'avg_roas': round(avg_roas, 2),
            'avg_ctr': round(avg_ctr, 2),
            'total_spend': round(total_spend, 2),
            'roas_outliers': len(roas_outliers),
            'ctr_outliers': len(ctr_outliers),
            'best_performer': max(campaigns, key=lambda x: x['roas'])['name'] if campaigns else None,
            'worst_performer': min(campaigns, key=lambda x: x['roas'])['name'] if campaigns else None,
            'highest_spend': max(campaigns, key=lambda x: x['spend'])['name'] if campaigns else None
        }
    
    def _detect_issues(self, campaigns: List[Dict]) -> List[Dict]:
        """Detecta problemas nas campanhas"""
        issues = []
        
        for campaign in campaigns:
            # Problemas de ROAS
            if campaign['roas'] < 2.0:
                issues.append({
                'campaign': campaign['name'],
                    'issue': 'ROAS_BAIXO',
                    'value': campaign['roas'],
                    'threshold': 2.0,
                    'severity': 'HIGH' if campaign['roas'] < 1.5 else 'MEDIUM'
                })
            
            # Problemas de CTR
            if campaign['ctr'] < 1.0:
                issues.append({
                    'campaign': campaign['name'],
                    'issue': 'CTR_BAIXO',
                    'value': campaign['ctr'],
                    'threshold': 1.0,
                    'severity': 'HIGH' if campaign['ctr'] < 0.5 else 'MEDIUM'
                })
            
            # Problemas de CPC
            if campaign['cpc'] > 1.5:
                issues.append({
                    'campaign': campaign['name'],
                    'issue': 'CPC_ALTO',
                    'value': campaign['cpc'],
                    'threshold': 1.5,
                    'severity': 'HIGH' if campaign['cpc'] > 2.0 else 'MEDIUM'
                })
            
            # Problemas de spend
            if campaign['spend'] > 400:
                issues.append({
                    'campaign': campaign['name'],
                    'issue': 'SPEND_ALTO',
                    'value': campaign['spend'],
                    'threshold': 400,
                    'severity': 'MEDIUM'
                })
        
        return issues
    
    def _generate_recommendations(self, campaigns: List[Dict], issues: List[Dict]) -> List[str]:
        """Gera recomendações baseadas nos dados"""
        recommendations = []
        
        # Recomendações baseadas em issues
        roas_issues = [i for i in issues if i['issue'] == 'ROAS_BAIXO']
        ctr_issues = [i for i in issues if i['issue'] == 'CTR_BAIXO']
        cpc_issues = [i for i in issues if i['issue'] == 'CPC_ALTO']
        
        if roas_issues:
            recommendations.append(f"Revisar {len(roas_issues)} campanhas com ROAS abaixo de 2.0x")
        
        if ctr_issues:
            recommendations.append(f"Otimizar criativos das {len(ctr_issues)} campanhas com CTR < 1%")
        
        if cpc_issues:
            recommendations.append(f"Ajustar segmentação das {len(cpc_issues)} campanhas com CPC > $1.50")
        
        # Recomendações gerais
        if campaigns:
            avg_roas = sum(c['roas'] for c in campaigns) / len(campaigns)
            if avg_roas > 3.5:
                recommendations.append("Performance excelente - considerar aumentar budget")
            elif avg_roas < 2.5:
                recommendations.append("Performance abaixo do esperado - pausar campanhas underperforming")
        
        # Recomendações por objetivo
        conversion_campaigns = [c for c in campaigns if c['objective'] == 'CONVERSIONS']
        if conversion_campaigns:
            avg_conversion_rate = sum(c['conversion_rate'] for c in conversion_campaigns) / len(conversion_campaigns)
            if avg_conversion_rate < 2.0:
                recommendations.append("Taxa de conversão baixa - revisar landing pages")
        
        return recommendations[:5]  # Limitar a 5 recomendações
    
    def generate_alert_scenario(self) -> Dict:
        """Gera um cenário específico com alertas para teste"""
        self.set_scenario('crisis')
        data = self.get_insights()
        
        # Forçar uma campanha crítica
        if data['campaigns']:
            critical_campaign = data['campaigns'][0]
            critical_campaign['roas'] = 1.2
            critical_campaign['ctr'] = 0.3
            critical_campaign['spend'] = 450
            critical_campaign['name'] += " [CRITICAL TEST]"
            critical_campaign['status'] = 'ACTIVE'
            
            # Adicionar mais issues
            data['issues'].extend([
                {
                    'campaign': critical_campaign['name'],
                    'issue': 'CRITICAL_PERFORMANCE',
                    'value': 1.2,
                    'threshold': 3.0,
                    'severity': 'CRITICAL'
                }
            ])
        
        return data
    
    def generate_performance_breakdown(self, campaign_id: str) -> Dict:
        """Gera breakdown detalhado de uma campanha (simula API de insights detalhados)"""
        
        # Simular dados diários
        daily_data = []
        for i in range(self.date_range):
            date = (datetime.now() - timedelta(days=i)).date()
            
            # Simular variação diária
            daily_spend = self.random_seed.uniform(20, 80)
            daily_impressions = int(daily_spend * self.random_seed.uniform(80, 150))
            daily_clicks = int(daily_impressions * self.random_seed.uniform(0.008, 0.025))
            daily_conversions = int(daily_clicks * self.random_seed.uniform(0.02, 0.06))
            
            daily_data.append({
                'date': date.isoformat(),
                'spend': round(daily_spend, 2),
                'impressions': daily_impressions,
                'clicks': daily_clicks,
                'conversions': daily_conversions,
                'ctr': round((daily_clicks / daily_impressions * 100) if daily_impressions > 0 else 0, 2),
                'cpc': round(daily_spend / daily_clicks if daily_clicks > 0 else 0, 2),
                'roas': round(self.random_seed.uniform(1.5, 4.5), 2)
            })
        
        return {
            'campaign_id': campaign_id,
            'breakdown': daily_data,
            'total_days': len(daily_data),
            'trend': 'upward' if daily_data[-1]['roas'] > daily_data[0]['roas'] else 'downward',
            'volatility': self.random_seed.uniform(0.1, 0.4)
        }
    
    def get_adsets(self, campaign_id: str) -> List[Dict]:
        """Simula conjuntos de anúncios de uma campanha"""
        adsets = []
        num_adsets = self.random_seed.randint(2, 5)
        
        for i in range(num_adsets):
            adset = AdSet(
                id=f"{campaign_id}:adset_{i}_{self.random_seed.randint(100, 999)}",
                name=f"AdSet {i+1} - {self.random_seed.choice(['Mobile', 'Desktop', 'Both'])}",
                campaign_id=campaign_id,
                targeting={
                    'age_min': self.random_seed.choice([18, 25, 35]),
                    'age_max': self.random_seed.choice([34, 44, 54, 65]),
                    'genders': [1, 2],  # Male, Female
                    'interests': ['Tattoo', 'Body Art', 'Professional Services']
                },
                status=self.random_seed.choice(['ACTIVE', 'PAUSED']),
                budget=self.random_seed.uniform(50, 200),
                spend=self.random_seed.uniform(20, 150)
            )
            adsets.append(adset.to_dict())
        
        return adsets