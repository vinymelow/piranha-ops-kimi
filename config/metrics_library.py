#!/usr/bin/env python3
"""
Biblioteca de Métricas B2B com Classificação Automática
Baseado em benchmarks 2024/2025 para B2B Tattoo Supplies
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple

class MetricTier(Enum):
    CRITICAL = "critical"      # 🚨 Vermelho - Ação imediata
    WARNING = "warning"        # ⚠️ Amarelo - Observar
    OPTIMIZATION = "optimization"  # 🔵 Azul - Quick win
    HEALTHY = "healthy"        # 🟢 Verde - Manter

class MetricPhase(Enum):
    REVENUE_ACTIVATION = "revenue_activation"      # Fase 1 (0-30 dias)
    WHOLESALE_ENGINE = "wholesale_engine"          # Fase 2 (30-60 dias)
    OPERATIONAL_LIBERATION = "operational_lib"   # Fase 3 (60-90 dias)
    COMPLIANCE = "compliance"                     # Fase 4 (90-120 dias)
    STRATEGIC = "strategic"                       # Cross-phase

@dataclass
class MetricThreshold:
    """Thresholds científicos para classificação automática"""
    critical_below: Optional[float] = None
    warning_below: Optional[float] = None
    optimization_above: Optional[float] = None
    healthy_above: Optional[float] = None
    target: float = 0.0
    unit: str = "units"
    
    def classify(self, value: float) -> MetricTier:
        """Classifica valor baseado em thresholds"""
        if self.critical_below is not None and value < self.critical_below:
            return MetricTier.CRITICAL
        if self.warning_below is not None and value < self.warning_below:
            return MetricTier.WARNING
        if self.healthy_above is not None and value >= self.healthy_above:
            return MetricTier.HEALTHY
        if self.optimization_above is not None and value >= self.optimization_above:
            return MetricTier.OPTIMIZATION
        return MetricTier.WARNING

# MÉTRICAS FASE 1: REVENUE ACTIVATION (0-30 dias)
REVENUE_METRICS = {
    "cart_recovery_rate": MetricThreshold(
        critical_below=0.05,      # <5% é crítico (indústria: 10-15%)
        warning_below=0.08,       # 5-8% atenção
        optimization_above=0.10, # 10-12% bom
        healthy_above=0.12,       # >12% excelente
        target=0.10,
        unit="percentage"
    ),
    "cart_recovery_revenue_eur": MetricThreshold(
        critical_below=1000,
        warning_below=2500,
        optimization_above=3000,
        healthy_above=5000,
        target=3000,
        unit="EUR"
    ),
    "new_studios_per_week": MetricThreshold(
        critical_below=10,
        warning_below=25,
        optimization_above=30,
        healthy_above=50,
        target=30,
        unit="count"
    ),
    "studio_to_lead_conversion": MetricThreshold(
        critical_below=0.15,
        warning_below=0.20,
        optimization_above=0.25,
        healthy_above=0.35,
        target=0.25,
        unit="percentage"
    ),
    "stockout_prediction_accuracy": MetricThreshold(
        critical_below=0.70,
        warning_below=0.80,
        optimization_above=0.85,
        healthy_above=0.90,
        target=0.85,
        unit="percentage"
    ),
    "stockout_prevented_value_eur": MetricThreshold(
        critical_below=5000,
        warning_below=10000,
        optimization_above=15000,
        healthy_above=20000,
        target=15000,
        unit="EUR"
    ),
    "reorder_frequency_increase": MetricThreshold(
        critical_below=1.0,  # Sem aumento
        warning_below=1.1,
        optimization_above=1.2,
        healthy_above=1.3,
        target=1.2,
        unit="ratio"
    ),
    "lead_response_time_minutes": MetricThreshold(
        critical_below=None,
        warning_below=None,
        optimization_above=None,
        healthy_above=None,
        target=5,
        unit="minutes"
        # Lógica especial: quanto MENOR melhor
    )
}

# MÉTRICAS FASE 2: WHOLESALE ENGINE (30-60 dias)
WHOLESALE_METRICS = {
    "partner_application_time_hours": MetricThreshold(
        critical_below=None,
        warning_below=None,
        optimization_above=None,
        healthy_above=None,
        target=2,
        unit="hours"
    ),
    "partner_conversion_rate": MetricThreshold(
        critical_below=0.20,
        warning_below=0.30,
        optimization_above=0.40,
        healthy_above=0.50,
        target=0.40,
        unit="percentage"
    ),
    "wholesale_ltv_growth": MetricThreshold(
        critical_below=1.0,
        warning_below=1.2,
        optimization_above=1.3,
        healthy_above=1.5,
        target=1.3,
        unit="ratio"
    ),
    "wholesale_purchase_frequency_monthly": MetricThreshold(
        critical_below=2,
        warning_below=3,
        optimization_above=4,
        healthy_above=5,
        target=4,
        unit="count"
    ),
    "tier_upgrade_rate": MetricThreshold(
        critical_below=0.05,
        warning_below=0.10,
        optimization_above=0.15,
        healthy_above=0.20,
        target=0.15,
        unit="percentage"
    )
}

# MÉTRICAS FASE 3: OPERATIONAL LIBERATION (60-90 dias)
OPERATIONAL_METRICS = {
    "dhl_processing_time_minutes": MetricThreshold(
        critical_below=None,
        warning_below=None,
        optimization_above=None,
        healthy_above=None,
        target=2,
        unit="minutes"
    ),
    "shipping_error_rate": MetricThreshold(
        critical_below=None,
        warning_below=None,
        optimization_above=None,
        healthy_above=None,
        target=0.005,
        unit="percentage"
    ),
    "cod_processing_time_minutes": MetricThreshold(
        critical_below=None,
        warning_below=None,
        optimization_above=None,
        healthy_above=None,
        target=5,
        unit="minutes"
    ),
    "cod_reconciliation_accuracy": MetricThreshold(
        critical_below=0.95,
        warning_below=0.98,
        optimization_above=0.99,
        healthy_above=0.995,
        target=0.99,
        unit="percentage"
    ),
    "team_time_saved_hours_monthly": MetricThreshold(
        critical_below=20,
        warning_below=40,
        optimization_above=60,
        healthy_above=100,
        target=60,
        unit="hours"
    ),
    "manual_work_reduction_percentage": MetricThreshold(
        critical_below=0.10,
        warning_below=0.20,
        optimization_above=0.30,
        healthy_above=0.40,
        target=0.30,
        unit="percentage"
    )
}

# MÉTRICAS FASE 4: COMPLIANCE (90-120 dias)
COMPLIANCE_METRICS = {
    "infarmed_reporting_time_minutes": MetricThreshold(
        critical_below=None,
        warning_below=None,
        optimization_above=None,
        healthy_above=None,
        target=15,
        unit="minutes"
    ),
    "compliance_error_rate": MetricThreshold(
        critical_below=None,
        warning_below=None,
        optimization_above=None,
        healthy_above=None,
        target=0.0,
        unit="percentage"
    ),
    "rma_resolution_time_hours": MetricThreshold(
        critical_below=None,
        warning_below=None,
        optimization_above=None,
        healthy_above=None,
        target=48,
        unit="hours"
    ),
    "rma_satisfaction_score": MetricThreshold(
        critical_below=3.5,
        warning_below=4.0,
        optimization_above=4.2,
        healthy_above=4.5,
        target=4.0,
        unit="score"
    ),
    "bank_reconciliation_time_minutes": MetricThreshold(
        critical_below=None,
        warning_below=None,
        optimization_above=None,
        healthy_above=None,
        target=60,
        unit="minutes"
    ),
    "financial_error_rate": MetricThreshold(
        critical_below=None,
        warning_below=None,
        optimization_above=None,
        healthy_above=None,
        target=0.001,
        unit="percentage"
    )
}

# MÉTRICAS ESTRATÉGICAS (Cross-Phase)
STRATEGIC_METRICS = {
    "customer_acquisition_cost_eur": MetricThreshold(
        critical_below=None,
        warning_below=None,
        optimization_above=None,
        healthy_above=None,
        target=100,
        unit="EUR"
    ),
    "ltv_cac_ratio": MetricThreshold(
        critical_below=3.0,       # <3:1 insustentável
        warning_below=3.5,
        optimization_above=4.0,
        healthy_above=5.0,
        target=4.0,
        unit="ratio"
    ),
    "sales_velocity_eur_per_day": MetricThreshold(
        critical_below=1000,
        warning_below=2000,
        optimization_above=3000,
        healthy_above=5000,
        target=3000,
        unit="EUR"
    ),
    "pipeline_coverage_ratio": MetricThreshold(
        critical_below=3.0,
        warning_below=4.0,
        optimization_above=4.0,
        healthy_above=5.0,
        target=4.0,
        unit="ratio"
    ),
    "forecast_accuracy_percentage": MetricThreshold(
        critical_below=0.70,
        warning_below=0.80,
        optimization_above=0.85,
        healthy_above=0.90,
        target=0.85,
        unit="percentage"
    ),
    "b2b_win_rate": MetricThreshold(
        critical_below=0.15,
        warning_below=0.20,
        optimization_above=0.25,
        healthy_above=0.30,
        target=0.25,
        unit="percentage"
    )
}

# Agregar todas
ALL_METRICS = {
    **REVENUE_METRICS,
    **WHOLESALE_METRICS,
    **OPERATIONAL_METRICS,
    **COMPLIANCE_METRICS,
    **STRATEGIC_METRICS
}

# FUNÇÕES ÚTEIS PARA DASHBOARD
def get_metrics_by_phase(phase: MetricPhase) -> Dict[str, MetricThreshold]:
    """Retorna métricas por fase do roadmap"""
    phase_map = {
        MetricPhase.REVENUE_ACTIVATION: REVENUE_METRICS,
        MetricPhase.WHOLESALE_ENGINE: WHOLESALE_METRICS,
        MetricPhase.OPERATIONAL_LIBERATION: OPERATIONAL_METRICS,
        MetricPhase.COMPLIANCE: COMPLIANCE_METRICS,
        MetricPhase.STRATEGIC: STRATEGIC_METRICS
    }
    return phase_map.get(phase, {})

def get_metrics_by_tier(tier: MetricTier) -> Dict[str, MetricThreshold]:
    """Retorna métricas classificadas por tier atual"""
    return {k: v for k, v in ALL_METRICS.items() if v.classify(get_current_value(k)) == tier}

def get_current_value(metric_id: str) -> float:
    """Simula valor atual da métrica (em produção: busca do banco)"""
    # Valores simulados baseados em targets
    threshold = ALL_METRICS.get(metric_id)
    if not threshold:
        return 0.0
    
    # Simula valor próximo do target com variação
    import random
    variation = random.uniform(0.8, 1.1)  # ±20%
    return threshold.target * variation

def get_executive_summary() -> Dict:
    """Resumo executivo para dashboard CEO/Head of Growth"""
    metrics_status = {
        "critical": [],
        "warning": [],
        "optimization": [],
        "healthy": []
    }
    
    for metric_id, threshold in ALL_METRICS.items():
        current_value = get_current_value(metric_id)
        tier = threshold.classify(current_value)
        
        metrics_status[tier.value].append({
            "id": metric_id,
            "name": metric_id.replace("_", " ").title(),
            "value": current_value,
            "target": threshold.target,
            "unit": threshold.unit,
            "phase": get_phase_from_metric(metric_id)
        })
    
    return metrics_status

def get_phase_from_metric(metric_id: str) -> str:
    """Determina fase da métrica pelo ID"""
    if any(x in metric_id for x in ['cart', 'studio', 'stock', 'lead', 'reorder']):
        return "Fase 1: Revenue Activation"
    elif any(x in metric_id for x in ['partner', 'wholesale', 'tier']):
        return "Fase 2: Wholesale Engine"
    elif any(x in metric_id for x in ['dhl', 'cod', 'time_saved', 'manual']):
        return "Fase 3: Operational Liberation"
    elif any(x in metric_id for x in ['infarmed', 'rma', 'compliance', 'bank']):
        return "Fase 4: Compliance"
    else:
        return "Estratégico"