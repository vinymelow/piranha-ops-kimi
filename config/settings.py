"""
Configurações centralizadas do PiranhaOps
Fácil de trocar entre MOCK e PRODUÇÃO
"""

import os
import logging
from dataclasses import dataclass
from typing import Dict, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

@dataclass
class Settings:
    """Configurações do sistema"""
    
    # Modo de operação: 'mock' ou 'production'
    MODE: str = 'mock'
    
    # Moonshot API
    MOONSHOT_API_KEY: str = ''
    MOONSHOT_BASE_URL: str = 'https://api.moonshot.ai/v1'
    
    # Meta (mock por enquanto)
    META_ACCESS_TOKEN: str = 'mock_token_meta_12345'
    META_AD_ACCOUNT_ID: str = 'act_mock_67890'
    
    # Shopify (mock por enquanto)
    SHOPIFY_STORE: str = 'piranha-global-mock.myshopify.com'
    SHOPIFY_ACCESS_TOKEN: str = 'mock_token_shopify_12345'
    
    # Slack (mock por enquanto)
    SLACK_WEBHOOK_URL: str = 'https://hooks.slack.com/services/MOCK/WEBHOOK/URL'
    
    # Configurações de negócio
    CHECK_INTERVAL_MINUTES: int = 5  # 5 min para testes (depois 30)
    ROAS_THRESHOLD: float = 3.0
    CTR_THRESHOLD: float = 1.0
    BUDGET_DAILY_USD: float = 1.00  # €0.93 para testes
    
    # Modelos
    DEFAULT_MODEL: str = 'kimi-k2-turbo-preview'
    ANALYSIS_MODEL: str = 'kimi-k2-0905-preview'
    DEEP_MODEL: str = 'kimi-k2-thinking'

    @classmethod
    def from_env(cls) -> 'Settings':
        """Carrega do .env ou usa defaults"""
        try:
            load_dotenv()
        except Exception as e:
            logger.warning(f"Não foi possível carregar .env: {e}")
        
        return cls(
            MODE=os.getenv('MODE', 'mock'),
            MOONSHOT_API_KEY=os.getenv('MOONSHOT_API_KEY', ''),
            MOONSHOT_BASE_URL=os.getenv('MOONSHOT_BASE_URL', 'https://api.moonshot.ai/v1'),
            META_ACCESS_TOKEN=os.getenv('META_ACCESS_TOKEN', 'mock_token_meta_12345'),
            META_AD_ACCOUNT_ID=os.getenv('META_AD_ACCOUNT_ID', 'act_mock_67890'),
            SHOPIFY_STORE=os.getenv('SHOPIFY_STORE', 'piranha-global-mock.myshopify.com'),
            SHOPIFY_ACCESS_TOKEN=os.getenv('SHOPIFY_ACCESS_TOKEN', 'mock_token_shopify_12345'),
            SLACK_WEBHOOK_URL=os.getenv('SLACK_WEBHOOK_URL', 'https://hooks.slack.com/services/MOCK/WEBHOOK/URL'),
            CHECK_INTERVAL_MINUTES=int(os.getenv('CHECK_INTERVAL_MINUTES', '5')),
            ROAS_THRESHOLD=float(os.getenv('ROAS_THRESHOLD', '3.0')),
            CTR_THRESHOLD=float(os.getenv('CTR_THRESHOLD', '1.0')),
            BUDGET_DAILY_USD=float(os.getenv('BUDGET_DAILY_USD', '1.00')),
        )
    
    def is_mock(self) -> bool:
        """Verifica se está em modo mock"""
        return self.MODE.lower() == 'mock'
    
    def validate(self) -> bool:
        """Valida configurações essenciais"""
        errors = []
        
        if not self.is_mock():
            # Validações para modo produção
            if not self.MOONSHOT_API_KEY:
                errors.append("MOONSHOT_API_KEY é obrigatório em modo produção")
            if not self.META_ACCESS_TOKEN or 'mock' in self.META_ACCESS_TOKEN:
                errors.append("META_ACCESS_TOKEN inválido em modo produção")
            if not self.META_AD_ACCOUNT_ID or 'mock' in self.META_AD_ACCOUNT_ID:
                errors.append("META_AD_ACCOUNT_ID inválido em modo produção")
            
            # Validações de formato
            if not self.META_AD_ACCOUNT_ID.startswith('act_'):
                errors.append("META_AD_ACCOUNT_ID deve começar com 'act_'")
        
        # Validações comuns
        if self.BUDGET_DAILY_USD <= 0:
            errors.append("BUDGET_DAILY_USD deve ser positivo")
        if self.ROAS_THRESHOLD <= 0:
            errors.append("ROAS_THRESHOLD deve ser positivo")
        if self.CHECK_INTERVAL_MINUTES < 1:
            errors.append("CHECK_INTERVAL_MINUTES deve ser >= 1")
        
        if errors:
            raise ValueError(f"Erros de configuração: {'; '.join(errors)}")
        
        logger.info(f"✅ Configurações validadas - Modo: {self.MODE}")
        return True
    
    def get_model_config(self) -> Dict:
        """Retorna configuração dos modelos"""
        return {
            'economy': {
                'id': self.DEFAULT_MODEL,
                'input_price': 0.50,
                'output_price': 2.00,
                'description': 'Coleta, formatação, cálculos simples'
            },
            'standard': {
                'id': self.ANALYSIS_MODEL,
                'input_price': 2.00,
                'output_price': 10.00,
                'description': 'Análise, insights, escrita criativa'
            },
            'deep': {
                'id': self.DEEP_MODEL,
                'input_price': 3.00,
                'output_price': 15.00,
                'description': 'Debug complexo, arquitetura, estratégia'
            }
        }
    
    def to_dict(self) -> Dict:
        """Retorna configurações como dicionário (para logs)"""
        return {
            'mode': self.MODE,
            'budget_daily_usd': self.BUDGET_DAILY_USD,
            'check_interval_minutes': self.CHECK_INTERVAL_MINUTES,
            'roas_threshold': self.ROAS_THRESHOLD,
            'ctr_threshold': self.CTR_THRESHOLD,
            'meta_account': self.META_AD_ACCOUNT_ID if self.is_mock() else 'PRODUCTION',
            'shopify_store': self.SHOPIFY_STORE if self.is_mock() else 'PRODUCTION'
        }