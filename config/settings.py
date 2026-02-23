#!/usr/bin/env python3
"""
Configuração Centralizada - PiranhaOps AIOS v4.0
Estrutura de configuração seguindo o prompt estratégico completo
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import os
from pathlib import Path
from dotenv import load_dotenv

class Environment(Enum):
    MOCK = "mock"
    LOCALHOST = "localhost"
    PRODUCTION = "production"

class SquadType(Enum):
    COMMERCIAL = "commercial"
    OPERATIONAL = "operational"
    INTELLIGENCE = "intelligence"

class ModelTier(Enum):
    ECONOMY = "economy"      # 85% - kimi-k2-turbo-preview
    STANDARD = "standard"    # 15% - kimi-k2-0905-preview  
    DEEP = "deep"           # <1% - kimi-k2-thinking

@dataclass
class Settings:
    """
    Configuração centralizada do PiranhaOps AIOS v4.0
    Seguindo especificações do prompt estratégico
    """
    
    # ============================================================
    # SEÇÃO 1: AMBIENTE E MODO
    # ============================================================
    ENVIRONMENT: Environment = Environment.LOCALHOST
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # ============================================================
    # SEÇÃO 2: ORQUESTRAÇÃO (AIOS)
    # ============================================================
    AIOS_QUALITY_THRESHOLD: float = 0.85          # 85% mínimo
    AIOS_MAX_TASKS: int = 1000
    AIOS_TASK_TIMEOUT_SECONDS: int = 300
    AIOS_RETRY_ATTEMPTS: int = 3
    AIOS_RETRY_DELAY_SECONDS: int = 5
    
    # Distribuição de Modelos (OBRIGATÓRIO: 85/15/<1)
    MODEL_DISTRIBUTION: Dict[ModelTier, float] = field(default_factory=lambda: {
        ModelTier.ECONOMY: 0.85,
        ModelTier.STANDARD: 0.15,
        ModelTier.DEEP: 0.005  # 0.5% (arredonda para 1 task em 127)
    })
    
    # ============================================================
    # SEÇÃO 3: SQUADS CONFIGURAÇÃO
    # ============================================================
    SQUADS_CONFIG: Dict[SquadType, Dict] = field(default_factory=lambda: {
        SquadType.COMMERCIAL: {
            "enabled": True,
            "max_concurrent_tasks": 50,
            "priority": "high",
            "business_hours": {"start": 8, "end": 22},
            "auto_recovery": True
        },
        SquadType.OPERATIONAL: {
            "enabled": True,
            "max_concurrent_tasks": 40,
            "priority": "medium",
            "business_hours": {"start": 0, "end": 24},
            "auto_recovery": True
        },
        SquadType.INTELLIGENCE: {
            "enabled": True,
            "max_concurrent_tasks": 60,
            "priority": "high",
            "business_hours": {"start": 0, "end": 24},
            "auto_recovery": False  # Requer supervisão humana
        }
    })
    
    # ============================================================
    # SEÇÃO 4: INTEGRAÇÕES MCP (CHAVES - Carregadas de .env)
    # ============================================================
    
    # Moonshot AI (Obrigatório)
    MOONSHOT_API_KEY: Optional[str] = None
    MOONSHOT_BASE_URL: str = "https://api.moonshot.ai/v1"
    
    # Meta (Mock por enquanto)
    META_ACCESS_TOKEN: Optional[str] = None
    META_AD_ACCOUNT_ID: Optional[str] = None
    META_CAPI_ACCESS_TOKEN: Optional[str] = None
    
    # Shopify
    SHOPIFY_STORE_URL: Optional[str] = None  # formato: loja.myshopify.com
    SHOPIFY_ACCESS_TOKEN: Optional[str] = None
    SHOPIFY_API_VERSION: str = "2024-01"
    
    # Klaviyo
    KLAVIYO_API_KEY: Optional[str] = None
    KLAVIYO_LIST_ID: Optional[str] = None
    
    # WhatsApp Business
    WHATSAPP_BUSINESS_ID: Optional[str] = None
    WHATSAPP_ACCESS_TOKEN: Optional[str] = None
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None
    
    # Sage X3
    SAGE_X3_BASE_URL: Optional[str] = None
    SAGE_X3_API_KEY: Optional[str] = None
    SAGE_X3_COMPANY: Optional[str] = None
    
    # ============================================================
    # SEÇÃO 5: THRESHOLDS E REGRAS DE NEGÓCIO
    # ============================================================
    
    # Métricas B2B Tattoo Supplies
    ROAS_THRESHOLD: float = 3.0          # Mínimo aceitável
    CTR_THRESHOLD: float = 1.0           # Percentual
    CPC_MAX_TARGET: float = 1.50         # Euros
    CPM_NORMAL_RANGE: tuple = (8, 15)    # Euros
    
    # Cart Recovery
    CART_ABANDONMENT_DELAY_MINUTES: int = 60  # Tempo antes de considerar abandonado
    WHATSAPP_RECOVERY_DELAY_MINUTES: int = 15  # OPP-001: Reduzir para 15min
    EMAIL_FALLBACK_DELAY_HOURS: int = 24
    
    # Qualidade
    MIN_QUALITY_SCORE: float = 0.85
    AUTO_ESCALATE_QUALITY: float = 0.60  # Abaixo disso, escala para humano
    
    # ============================================================
    # SEÇÃO 6: OTIMIZAÇÃO DE CUSTOS (€50/mês - Revenue Activation)
    # ============================================================
    BUDGET_DAILY_USD: float = 1.00       # ~€0.93
    BUDGET_MONTHLY_EUR: float = 37.00
    
    # Limites por tier (em tokens)
    ECONOMY_MAX_TOKENS: int = 2000
    STANDARD_MAX_TOKENS: int = 4000
    DEEP_MAX_TOKENS: int = 8000
    
    # ============================================================
    # SEÇÃO 7: DASHBOARD
    # ============================================================
    DASHBOARD_HOST: str = "0.0.0.0"
    DASHBOARD_PORT: int = 8083
    DASHBOARD_REFRESH_INTERVAL_MS: int = 5000
    DASHBOARD_THEME: str = "dark"  # dark | light
    
    # ============================================================
    # MÉTODOS
    # ============================================================
    
    @classmethod
    def from_env(cls) -> "Settings":
        """Carrega configurações de variáveis de ambiente"""
        load_dotenv("config/secrets.env")
        
        return cls(
            ENVIRONMENT=Environment(os.getenv("MODE", "localhost")),
            MOONSHOT_API_KEY=os.getenv("MOONSHOT_API_KEY"),
            META_ACCESS_TOKEN=os.getenv("META_ACCESS_TOKEN"),
            SHOPIFY_ACCESS_TOKEN=os.getenv("SHOPIFY_ACCESS_TOKEN"),
            KLAVIYO_API_KEY=os.getenv("KLAVIYO_API_KEY"),
            WHATSAPP_ACCESS_TOKEN=os.getenv("WHATSAPP_ACCESS_TOKEN"),
            SAGE_X3_API_KEY=os.getenv("SAGE_X3_API_KEY"),
            BUDGET_DAILY_USD=float(os.getenv("BUDGET_DAILY_USD", "1.00")),
            BUDGET_MONTHLY_EUR=float(os.getenv("BUDGET_MONTHLY_EUR", "37.00"))
        )
    
    def is_mock(self) -> bool:
        """Retorna True se estiver em modo mock/localhost"""
        return self.ENVIRONMENT in [Environment.MOCK, Environment.LOCALHOST]
    
    def get_squad_config(self, squad: SquadType) -> Dict:
        """Retorna configuração específica do squad"""
        return self.SQUADS_CONFIG.get(squad, {})
    
    def validate(self) -> bool:
        """
        Valida consistência das configurações
        Levanta ValueError se houver inconsistências
        """
        # Validar distribuição 85/15/<1
        total_dist = sum(self.MODEL_DISTRIBUTION.values())
        if not 0.99 <= total_dist <= 1.01:
            raise ValueError(f"Distribuição de modelos deve somar 1.0, atual: {total_dist}")
        
        # Validar thresholds
        if self.AIOS_QUALITY_THRESHOLD < 0 or self.AIOS_QUALITY_THRESHOLD > 1:
            raise ValueError("Quality threshold deve estar entre 0 e 1")
        
        # Validar budgets
        if self.BUDGET_DAILY_USD <= 0:
            raise ValueError("Budget diário deve ser positivo")
        
        return True

# Instância global
settings = Settings.from_env()
settings.validate()  # Valida na importação