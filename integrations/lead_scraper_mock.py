"""
Lead Scraper Mock - PiranhaOps AIOS v4.0 - Revenue Activation
Sistema de prospecção inteligente B2B
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import uuid
import random


@dataclass
class Lead:
    """Representa um lead capturado"""
    id: str
    name: str
    email: str
    phone: str
    source: str
    interest: str
    score: int
    created_at: str
    status: str


class LeadScraperMock:
    """Mock do Lead Scraper para captura e qualificação de leads"""
    
    def __init__(self):
        self.lead_database = []
        self.qualification_rules = {}
        self.initialize_test_data()
        
    def initialize_test_data(self):
        """Inicializa dados e regras de teste"""
        self.qualification_rules = {
            'facebook_ads': {
                'min_score': 70,
                'required_fields': ['name', 'email', 'phone'],
                'score_weights': {
                    'form_completion': 30,
                    'engagement_level': 25,
                    'demographic_match': 20,
                    'interest_relevance': 25
                }
            },
            'google_ads': {
                'min_score': 75,
                'required_fields': ['name', 'email'],
                'score_weights': {
                    'keyword_relevance': 40,
                    'landing_page_time': 30,
                    'conversion_action': 30
                }
            },
            'linkedin': {
                'min_score': 80,
                'required_fields': ['name', 'email', 'company'],
                'score_weights': {
                    'job_title_relevance': 35,
                    'company_size': 25,
                    'industry_match': 25,
                    'engagement_level': 15
                }
            },
            'website': {
                'min_score': 65,
                'required_fields': ['name', 'email'],
                'score_weights': {
                    'page_views': 25,
                    'time_on_site': 25,
                    'content_download': 25,
                    'return_visits': 25
                }
            }
        }
        
    def scrape_and_qualify(self, sources: List[str], 
                          qualification_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Captura e qualifica leads de múltiplas fontes
        
        Args:
            sources: Lista de fontes (facebook_ads, google_ads, linkedin, website)
            qualification_criteria: Critérios de qualificação
            
        Returns:
            Dict com leads capturados e análise de qualificação
        """
        all_leads = []
        
        for source in sources:
            if source in self.qualification_rules:
                source_leads = self._scrape_from_source(source, qualification_criteria)
                all_leads.extend(source_leads)
        
        # Qualificar leads
        qualified_leads = []
        for lead in all_leads:
            lead_score = self._calculate_lead_score(lead, qualification_criteria)
            lead['score'] = lead_score
            
            if lead_score >= qualification_criteria.get('min_score', 70):
                lead['status'] = 'qualified'
                qualified_leads.append(lead)
            else:
                lead['status'] = 'unqualified'
        
        # Gerar análise
        total_leads = len(all_leads)
        qualified_count = len(qualified_leads)
        avg_score = sum(lead['score'] for lead in all_leads) / total_leads if total_leads > 0 else 0
        
        # Análise por fonte
        source_analysis = {}
        for source in sources:
            source_leads = [lead for lead in all_leads if lead['source'] == source]
            if source_leads:
                source_qualified = [lead for lead in source_leads if lead['status'] == 'qualified']
                source_analysis[source] = {
                    'total_leads': len(source_leads),
                    'qualified_leads': len(source_qualified),
                    'qualification_rate': len(source_qualified) / len(source_leads) * 100,
                    'avg_score': sum(lead['score'] for lead in source_leads) / len(source_leads)
                }
        
        return {
            'leads': all_leads,
            'qualified_leads': qualified_leads,
            'summary': {
                'total_leads': total_leads,
                'qualified_count': qualified_count,
                'qualification_rate': qualified_count / total_leads * 100 if total_leads > 0 else 0,
                'avg_score': round(avg_score, 2),
                'sources': list(source_analysis.keys())
            },
            'source_analysis': source_analysis,
            'timestamp': datetime.now().isoformat()
        }
        
    def _scrape_from_source(self, source: str, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Simula scraping de uma fonte específica"""
        
        leads = []
        
        # Configurar dados base por fonte
        source_configs = {
            'facebook_ads': {
                'count_range': (5, 12),
                'interests': ['tattoo equipment', 'tattoo supplies', 'professional tattoo', 'tattoo artist'],
                'names': ['João Silva', 'Maria Santos', 'Pedro Oliveira', 'Ana Costa', 'Carlos Souza'],
                'score_range': (60, 95)
            },
            'google_ads': {
                'count_range': (3, 8),
                'interests': ['tattoo shop supplies', 'professional tattoo equipment', 'tattoo ink wholesale'],
                'names': ['Ricardo Lima', 'Fernanda Alves', 'Bruno Mendes', 'Patricia Rocha'],
                'score_range': (65, 90)
            },
            'linkedin': {
                'count_range': (2, 6),
                'interests': ['tattoo business', 'body art industry', 'professional equipment'],
                'names': ['Roberto Dias', 'Luciana Nunes', 'André Ferreira', 'Camila Araújo'],
                'score_range': (75, 98)
            },
            'website': {
                'count_range': (4, 10),
                'interests': ['tattoo products', 'equipment catalog', 'wholesale prices'],
                'names': ['Felipe Cardoso', 'Juliana Barros', 'Rafael Teixeira', 'Mariana Lopes'],
                'score_range': (55, 85)
            }
        }
        
        config = source_configs.get(source, source_configs['website'])
        num_leads = random.randint(*config['count_range'])
        
        for i in range(num_leads):
            base_name = random.choice(config['names'])
            lead = {
                'id': str(uuid.uuid4()),
                'name': f"{base_name} {i+1}",
                'email': f"lead{i+1}_{source}@example.com",
                'phone': f"+55119{random.randint(10000000, 99999999)}",
                'source': source,
                'interest': random.choice(config['interests']),
                'score': random.randint(*config['score_range']),
                'created_at': datetime.now().isoformat(),
                'status': 'new',
                'company': f"Empresa {random.randint(1, 50)}" if source == 'linkedin' else None,
                'job_title': f"{random.choice(['Proprietário', 'Gerente', 'Artista', 'Comprador'])}" if source == 'linkedin' else None
            }
            
            # Adicionar campos específicos por fonte
            if source == 'facebook_ads':
                lead['facebook_id'] = f"fb_{random.randint(100000000, 999999999)}"
                lead['form_completion_time'] = random.randint(30, 300)  # segundos
                lead['ad_interaction_score'] = random.randint(1, 10)
                
            elif source == 'google_ads':
                lead['keyword'] = random.choice(config['interests'])
                lead['landing_page_time'] = random.randint(60, 600)  # segundos
                lead['pages_viewed'] = random.randint(1, 8)
                
            elif source == 'linkedin':
                lead['company_size'] = random.choice(['small', 'medium', 'large'])
                lead['industry'] = 'Body Art'
                lead['seniority_level'] = random.choice(['owner', 'manager', 'senior'])
                lead['linkedin_connections'] = random.randint(100, 1000)
                
            elif source == 'website':
                lead['page_views'] = random.randint(3, 20)
                lead['time_on_site'] = random.randint(120, 1800)  # segundos
                lead['content_downloaded'] = random.choice([True, False])
                lead['return_visits'] = random.randint(0, 5)
                lead['referrer'] = random.choice(['google', 'facebook', 'direct', 'instagram'])
            
            leads.append(lead)
        
        return leads
        
    def _calculate_lead_score(self, lead: Dict[str, Any], criteria: Dict[str, Any]) -> int:
        """Calcula score de qualificação do lead"""
        
        source = lead['source']
        base_score = lead.get('score', 50)  # Score base vindo da fonte
        
        # Aplicar regras específicas por fonte
        if source == 'facebook_ads':
            # Form completion score
            if lead.get('form_completion_time', 0) < 120:  # Menos de 2 minutos
                base_score += 10
                
            # Ad interaction score
            ad_score = lead.get('ad_interaction_score', 0)
            if ad_score >= 7:
                base_score += 15
            elif ad_score >= 5:
                base_score += 10
                
        elif source == 'google_ads':
            # Keyword relevance
            keyword = lead.get('keyword', '').lower()
            if any(term in keyword for term in ['professional', 'wholesale', 'supplier']):
                base_score += 20
            elif any(term in keyword for term in ['equipment', 'supplies']):
                base_score += 10
                
            # Landing page engagement
            landing_time = lead.get('landing_page_time', 0)
            if landing_time > 300:  # Mais de 5 minutos
                base_score += 15
            elif landing_time > 120:  # Mais de 2 minutos
                base_score += 10
                
            # Pages viewed
            pages_viewed = lead.get('pages_viewed', 0)
            if pages_viewed >= 5:
                base_score += 10
            elif pages_viewed >= 3:
                base_score += 5
                
        elif source == 'linkedin':
            # Company size
            company_size = lead.get('company_size')
            if company_size == 'large':
                base_score += 20
            elif company_size == 'medium':
                base_score += 10
                
            # Seniority level
            seniority = lead.get('seniority_level')
            if seniority == 'owner':
                base_score += 25
            elif seniority == 'manager':
                base_score += 15
            elif seniority == 'senior':
                base_score += 10
                
            # Industry match
            if lead.get('industry') == 'Body Art':
                base_score += 10
                
        elif source == 'website':
            # Time on site
            time_on_site = lead.get('time_on_site', 0)
            if time_on_site > 900:  # Mais de 15 minutos
                base_score += 20
            elif time_on_site > 600:  # Mais de 10 minutos
                base_score += 15
            elif time_on_site > 300:  # Mais de 5 minutos
                base_score += 10
                
            # Content download
            if lead.get('content_downloaded'):
                base_score += 15
                
            # Return visits
            return_visits = lead.get('return_visits', 0)
            if return_visits >= 3:
                base_score += 15
            elif return_visits >= 2:
                base_score += 10
            elif return_visits >= 1:
                base_score += 5
                
            # Page views
            page_views = lead.get('page_views', 0)
            if page_views >= 10:
                base_score += 15
            elif page_views >= 5:
                base_score += 10
            elif page_views >= 3:
                base_score += 5
        
        # Validar campos obrigatórios
        required_fields = criteria.get('required_fields', [])
        for field in required_fields:
            if not lead.get(field):
                base_score -= 20  # Penalizar por campos faltantes
                
        # Garantir que o score esteja entre 0 e 100
        final_score = max(0, min(100, base_score))
        
        return int(final_score)
        
    def get_lead_details(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Retorna detalhes de um lead específico"""
        
        # Simular busca no banco de dados
        for lead in self.lead_database:
            if lead.get('id') == lead_id:
                return lead
                
        # Se não encontrar, criar um lead mock
        return {
            'id': lead_id,
            'name': 'Lead Exemplo',
            'email': 'exemplo@lead.com',
            'phone': '+5511999999999',
            'source': 'facebook_ads',
            'interest': 'tattoo equipment',
            'score': 85,
            'status': 'qualified',
            'created_at': datetime.now().isoformat(),
            'last_contact': datetime.now().isoformat(),
            'notes': 'Lead de exemplo para testes'
        }
        
    def update_lead_status(self, lead_id: str, new_status: str, notes: Optional[str] = None) -> Dict[str, Any]:
        """Atualiza status de um lead"""
        
        valid_statuses = ['new', 'qualified', 'contacted', 'converted', 'lost', 'unqualified']
        
        if new_status not in valid_statuses:
            return {
                'success': False,
                'error': f'Status inválido. Status válidos: {", ".join(valid_statuses)}'
            }
            
        return {
            'success': True,
            'lead_id': lead_id,
            'previous_status': 'new',
            'new_status': new_status,
            'notes': notes,
            'updated_at': datetime.now().isoformat(),
            'message': f'Status do lead atualizado para {new_status}'
        }
        
    def get_lead_analytics(self, date_range: Dict[str, str]) -> Dict[str, Any]:
        """Retorna análise de leads por período"""
        
        # Simular análise
        total_leads = random.randint(50, 200)
        qualified_leads = int(total_leads * random.uniform(0.3, 0.6))
        converted_leads = int(qualified_leads * random.uniform(0.2, 0.4))
        
        return {
            'date_range': date_range,
            'total_leads': total_leads,
            'qualified_leads': qualified_leads,
            'converted_leads': converted_leads,
            'qualification_rate': round(qualified_leads / total_leads * 100, 2),
            'conversion_rate': round(converted_leads / qualified_leads * 100, 2) if qualified_leads > 0 else 0,
            'avg_score': round(random.uniform(65, 85), 2),
            'top_sources': [
                {'source': 'facebook_ads', 'count': int(total_leads * 0.4)},
                {'source': 'google_ads', 'count': int(total_leads * 0.3)},
                {'source': 'linkedin', 'count': int(total_leads * 0.2)},
                {'source': 'website', 'count': int(total_leads * 0.1)}
            ]
        }
        
    def cleanup_old_leads(self, days_to_keep: int = 90) -> Dict[str, Any]:
        """Limpa leads antigos do banco de dados"""
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Simular limpeza
        return {
            'cleanup_date': datetime.now().isoformat(),
            'days_to_keep': days_to_keep,
            'leads_removed': random.randint(100, 500),
            'space_freed_mb': round(random.uniform(10, 50), 2),
            'status': 'completed'
        }