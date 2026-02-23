"""
Mock do Google Ads para testes da Fase 1 - Revenue Activation
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class GoogleCampaignMetrics:
    """Métricas de campanha do Google Ads"""
    campaign_id: str
    impressions: int
    clicks: int
    cost: float
    conversions: int
    conversion_value: float
    ctr: float
    avg_cpc: float
    roas: float


class GoogleAdsMock:
    """Mock do Google Ads API para testes"""
    
    def __init__(self):
        self.test_data = {}
        self.initialize_test_data()
        
    def initialize_test_data(self):
        """Inicializa dados de teste"""
        self.test_data = {
            'campaigns': [
                {
                    'id': 'google_camp_123',
                    'name': 'Campanha Google Performance',
                    'status': 'ENABLED',
                    'advertising_channel_type': 'SEARCH',
                    'budget': 150.0,
                    'currency': 'BRL',
                    'targeting': {
                        'languages': ['pt'],
                        'locations': ['São Paulo', 'Rio de Janeiro']
                    }
                }
            ],
            'ad_groups': [
                {
                    'id': 'google_adgroup_456',
                    'campaign_id': 'google_camp_123',
                    'name': 'Grupo de Anúncios Google',
                    'cpc_bid': 1.50
                }
            ],
            'keywords': [
                {
                    'id': 'google_kw_789',
                    'ad_group_id': 'google_adgroup_456',
                    'text': 'tattoo supply',
                    'match_type': 'BROAD',
                    'cpc_bid': 1.25
                }
            ]
        }
        
    def get_campaign_performance(self, campaign_ids: List[str], 
                               metrics: List[str],
                               date_range: str = 'LAST_30_DAYS') -> Dict[str, Any]:
        """
        Retorna performance de campanhas do Google Ads
        
        Args:
            campaign_ids: Lista de IDs de campanha
            metrics: Métricas a retornar
            date_range: Período de análise
            
        Returns:
            Dict com performance data
        """
        campaigns_data = []
        total_cost = 0
        total_conversions = 0
        total_conversion_value = 0
        total_impressions = 0
        total_clicks = 0
        
        for i, campaign_id in enumerate(campaign_ids):
            # Gerar métricas realistas
            base_impressions = 800 + (i * 150)
            base_clicks = base_impressions * 0.04  # 4% CTR médio
            base_cost = base_clicks * 0.45  # R$0.45 CPC médio
            base_conversions = base_clicks * 0.08  # 8% taxa de conversão
            base_conversion_value = base_conversions * 120  # R$120 valor médio por conversão
            
            campaign_performance = {
                'campaign_id': campaign_id,
                'campaign_name': f'Campanha Google {i+1}',
                'impressions': int(base_impressions),
                'clicks': int(base_clicks),
                'cost': round(base_cost, 2),
                'conversions': int(base_conversions),
                'conversion_value': round(base_conversion_value, 2),
                'ctr': round((base_clicks / base_impressions) * 100, 2),
                'avg_cpc': round(base_cost / base_clicks if base_clicks > 0 else 0, 2),
                'cost_per_conversion': round(base_cost / base_conversions if base_conversions > 0 else 0, 2),
                'conversion_rate': round((base_conversions / base_clicks) * 100 if base_clicks > 0 else 0, 2),
                'roas': round(base_conversion_value / base_cost if base_cost > 0 else 0, 2)
            }
            
            campaigns_data.append(campaign_performance)
            
            # Acumular totais
            total_cost += campaign_performance['cost']
            total_conversions += campaign_performance['conversions']
            total_conversion_value += campaign_performance['conversion_value']
            total_impressions += campaign_performance['impressions']
            total_clicks += campaign_performance['clicks']
        
        # Calcular médias gerais
        avg_cpc = total_cost / total_clicks if total_clicks > 0 else 0
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_roas = total_conversion_value / total_cost if total_cost > 0 else 0
        
        return {
            'campaigns': campaigns_data,
            'metrics': {
                'total_cost': round(total_cost, 2),
                'total_conversions': total_conversions,
                'total_conversion_value': round(total_conversion_value, 2),
                'total_impressions': total_impressions,
                'total_clicks': total_clicks,
                'avg_cpc': round(avg_cpc, 2),
                'avg_ctr': round(avg_ctr, 2),
                'avg_roas': round(avg_roas, 2),
                'cost_per_conversion': round(total_cost / total_conversions if total_conversions > 0 else 0, 2)
            },
            'status': 'success',
            'date_range': date_range
        }
        
    def get_keyword_performance(self, ad_group_ids: List[str]) -> Dict[str, Any]:
        """Retorna performance de palavras-chave"""
        
        keywords_data = []
        
        for ad_group_id in ad_group_ids:
            # Simular performance de keywords
            keywords = [
                {
                    'keyword_id': f'kw_{i}',
                    'ad_group_id': ad_group_id,
                    'keyword_text': f'tattoo supply keyword {i}',
                    'match_type': 'BROAD',
                    'impressions': 200 + (i * 50),
                    'clicks': 8 + (i * 2),
                    'cost': 3.60 + (i * 0.90),
                    'conversions': 1,
                    'conversion_value': 20.00,
                    'avg_cpc': 0.45,
                    'ctr': 4.0,
                    'quality_score': 7 + (i % 3)
                }
                for i in range(3)
            ]
            keywords_data.extend(keywords)
            
        return {
            'keywords': keywords_data,
            'status': 'success'
        }
        
    def get_search_terms_report(self, campaign_ids: List[str]) -> Dict[str, Any]:
        """Retorna relatório de termos de pesquisa"""
        
        search_terms = [
            {
                'search_term': 'tattoo supply sp',
                'impressions': 150,
                'clicks': 6,
                'cost': 2.70,
                'conversions': 1,
                'conversion_value': 25.00
            },
            {
                'search_term': 'tattoo equipment rio',
                'impressions': 120,
                'clicks': 5,
                'cost': 2.25,
                'conversions': 0,
                'conversion_value': 0.00
            },
            {
                'search_term': 'professional tattoo supplies',
                'impressions': 80,
                'clicks': 4,
                'cost': 1.80,
                'conversions': 1,
                'conversion_value': 30.00
            }
        ]
        
        return {
            'search_terms': search_terms,
            'status': 'success'
        }
        
    def create_campaign(self, campaign_config: Dict[str, Any]) -> Dict[str, Any]:
        """Cria uma nova campanha no Google Ads"""
        
        campaign_id = f"google_camp_created_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            'campaign_id': campaign_id,
            'resource_name': f'customers/1234567890/campaigns/{campaign_id}',
            'status': 'created',
            'name': campaign_config.get('name', 'Nova Campanha Google'),
            'advertising_channel_type': campaign_config.get('channel_type', 'SEARCH'),
            'budget': campaign_config.get('budget', 100.0),
            'message': f'Campanha Google criada com sucesso. ID: {campaign_id}'
        }
        
    def update_campaign_bidding(self, campaign_id: str, bidding_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Atualiza estratégia de lance da campanha"""
        
        return {
            'campaign_id': campaign_id,
            'previous_strategy': 'MANUAL_CPC',
            'new_strategy': bidding_strategy.get('strategy_type', 'MAXIMIZE_CONVERSIONS'),
            'status': 'updated',
            'message': f'Estratégia de lance atualizada para {bidding_strategy.get("strategy_type", "MAXIMIZE_CONVERSIONS")}'
        }
        
    def get_campaigns_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Retorna campanhas por status"""
        
        campaigns = [
            campaign for campaign in self.test_data['campaigns']
            if campaign['status'] == status
        ]
        
        return campaigns
        
    def pause_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Pausa uma campanha do Google Ads"""
        
        return {
            'campaign_id': campaign_id,
            'previous_status': 'ENABLED',
            'new_status': 'PAUSED',
            'status': 'updated',
            'message': f'Campanha Google {campaign_id} pausada com sucesso'
        }
        
    def get_recommendations(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Retorna recomendações de otimização para Google Ads"""
        
        return [
            {
                'type': 'KEYWORD',
                'title': 'Adicionar Palavras-Chave',
                'description': 'Adicione estas palavras-chave de alto desempenho: "tattoo ink", "tattoo needles"',
                'impact': 'HIGH',
                'confidence': 80
            },
            {
                'type': 'BUDGET',
                'title': 'Aumentar Budget',
                'description': 'Sua campanha está com budget limitado. Aumente para alcançar mais clientes.',
                'impact': 'MEDIUM',
                'confidence': 90
            },
            {
                'type': 'BIDDING',
                'title': 'Ajustar Lances',
                'description': 'Aumente lances em palavras-chave de alto desempenho.',
                'impact': 'MEDIUM',
                'confidence': 75
            }
        ]
        
    def get_quality_score_report(self, campaign_id: str) -> Dict[str, Any]:
        """Retorna relatório de Quality Score"""
        
        return {
            'campaign_id': campaign_id,
            'quality_score_breakdown': {
                'expected_ctr': 7,
                'ad_relevance': 8,
                'landing_page_experience': 7
            },
            'overall_quality_score': 7.3,
            'keywords_by_quality_score': {
                '10': 2,
                '9': 3,
                '8': 5,
                '7': 8,
                '6': 4,
                '5': 2
            },
            'recommendations': [
                'Melhore o texto dos anúncios',
                'Otimize as páginas de destino',
                'Teste novos criativos'
            ]
        }
        
    def get_conversion_tracking_status(self, campaign_id: str) -> Dict[str, Any]:
        """Retorna status do tracking de conversões"""
        
        return {
            'campaign_id': campaign_id,
            'conversion_actions': [
                {
                    'name': 'Purchase',
                    'status': 'ENABLED',
                    'category': 'DEFAULT',
                    'value': 150.00
                },
                {
                    'name': 'Add to Cart',
                    'status': 'ENABLED',
                    'category': 'DEFAULT',
                    'value': 50.00
                }
            ],
            'tracking_status': 'healthy',
            'issues': []
        }