"""
Simulador de Sage X3 ERP para desenvolvimento
Gera dados realistas de inventário e vendas para produtos B2B tattoo supplies
"""

import random
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class StockStatus(Enum):
    """Status do estoque"""
    NORMAL = "normal"
    RUPTURE_IMMINENT = "rupture_imminent"
    OVERSTOCK = "overstock"
    SUPPLIER_DELAY = "supplier_delay"

class AlertLevel(Enum):
    """Nível de alerta"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SageProduct:
    """Produto do Sage X3 com métricas completas"""
    sku: str
    name: str
    category: str
    current_stock: int
    min_stock: int
    max_stock: int
    reorder_point: int
    unit_cost: float
    unit_price: float
    supplier: str
    lead_time_days: int  # tempo de entrega do fornecedor
    last_order_date: Optional[str]
    last_delivery_date: Optional[str]
    monthly_velocity: float  # velocidade média mensal
    weekly_velocity: float   # velocidade média semanal
    daily_velocity: float    # velocidade média diária
    coverage_days: float     # dias de cobertura atual
    status: str
    revenue_at_risk: float   # receita em risco por falta de estoque
    
    @property
    def stock_level_percentage(self) -> float:
        """Percentual do nível de estoque em relação ao máximo"""
        return (self.current_stock / self.max_stock) * 100 if self.max_stock > 0 else 0
    
    @property
    def is_below_reorder_point(self) -> bool:
        """Verifica se está abaixo do ponto de reordenação"""
        return self.current_stock <= self.reorder_point
    
    @property
    def is_out_of_stock(self) -> bool:
        """Verifica se está sem estoque"""
        return self.current_stock <= 0
    
    @property
    def total_value(self) -> float:
        """Valor total do estoque atual"""
        return self.current_stock * self.unit_cost
    
    @property
    def gross_margin(self) -> float:
        """Margem de lucro bruta"""
        return ((self.unit_price - self.unit_cost) / self.unit_price) * 100 if self.unit_price > 0 else 0
    
    def to_dict(self) -> Dict:
        """Converte para dicionário incluindo propriedades calculadas"""
        return {
            'sku': self.sku,
            'name': self.name,
            'category': self.category,
            'current_stock': self.current_stock,
            'min_stock': self.min_stock,
            'max_stock': self.max_stock,
            'reorder_point': self.reorder_point,
            'unit_cost': self.unit_cost,
            'unit_price': self.unit_price,
            'supplier': self.supplier,
            'lead_time_days': self.lead_time_days,
            'last_order_date': self.last_order_date,
            'last_delivery_date': self.last_delivery_date,
            'monthly_velocity': self.monthly_velocity,
            'weekly_velocity': self.weekly_velocity,
            'daily_velocity': self.daily_velocity,
            'coverage_days': self.coverage_days,
            'status': self.status,
            'revenue_at_risk': self.revenue_at_risk,
            'stock_level_percentage': round(self.stock_level_percentage, 2),
            'is_below_reorder_point': self.is_below_reorder_point,
            'is_out_of_stock': self.is_out_of_stock,
            'total_value': round(self.total_value, 2),
            'gross_margin': round(self.gross_margin, 2)
        }

@dataclass
class StockAlert:
    """Alerta de estoque com análise de risco"""
    alert_id: str
    sku: str
    product_name: str
    alert_type: str
    alert_level: str
    current_stock: int
    reorder_point: int
    coverage_days: float
    velocity_weekly: float
    lead_time_days: int
    revenue_at_risk: float
    suggested_order_quantity: int
    urgency_days: int  # dias até crítico
    created_at: str
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            'alert_id': self.alert_id,
            'sku': self.sku,
            'product_name': self.product_name,
            'alert_type': self.alert_type,
            'alert_level': self.alert_level,
            'current_stock': self.current_stock,
            'reorder_point': self.reorder_point,
            'coverage_days': self.coverage_days,
            'velocity_weekly': self.velocity_weekly,
            'lead_time_days': self.lead_time_days,
            'revenue_at_risk': self.revenue_at_risk,
            'suggested_order_quantity': self.suggested_order_quantity,
            'urgency_days': self.urgency_days,
            'created_at': self.created_at
        }

class SageX3Mock:
    """
    Simulador de Sage X3 ERP com cenários realistas
    Gera dados de inventário e vendas para produtos B2B tattoo supplies
    """
    
    # Produtos prioritários conforme especificado
    PRIORITY_PRODUCTS = [
        {
            "sku": "LUVAS_NITRILO",
            "name": "Luvas de Nitrilo para Tattoo",
            "category": "PROTEÇÃO",
            "base_cost": 2.50,
            "base_price": 8.90,
            "supplier": "MEDICAL_SUPPLIES_BR",
            "lead_time_days": 14
        },
        {
            "sku": "REVOLUTION_NEEDLES",
            "name": "Agulhas Revolution - Cartridge",
            "category": "AGULHAS",
            "base_cost": 15.00,
            "base_price": 45.00,
            "supplier": "REVOLUTION_TATTOO_USA",
            "lead_time_days": 21
        },
        {
            "sku": "FINELINE_NEEDLES",
            "name": "Agulhas FineLine - Premium",
            "category": "AGULHAS",
            "base_cost": 12.00,
            "base_price": 38.00,
            "supplier": "FINELINE_GERMANY",
            "lead_time_days": 28
        }
    ]
    
    # Configurações de estoque por cenário
    STOCK_CONFIGS = {
        'normal': {
            'stock_variance': (0.8, 1.2),
            'velocity_variance': (0.9, 1.1),
            'delay_probability': 0.1
        },
        'rupture_imminent': {
            'stock_variance': (0.1, 0.4),
            'velocity_variance': (1.2, 1.8),
            'delay_probability': 0.3
        },
        'overstock': {
            'stock_variance': (1.5, 2.5),
            'velocity_variance': (0.6, 0.9),
            'delay_probability': 0.05
        },
        'supplier_delay': {
            'stock_variance': (0.3, 0.7),
            'velocity_variance': (0.8, 1.2),
            'delay_probability': 0.7
        }
    }
    
    def __init__(self, company_code: str = "TATTOO_BRA"):
        self.company_code = company_code
        self.random_seed = random.Random(42)  # Seed fixo para reproducibilidade
        self.scenario = 'normal'
        self.products = {}
        self.alerts = []
        self._initialize_products()
        
        logger.info(f"📦 SageX3Mock inicializado - Empresa: {company_code}")
    
    def _initialize_products(self):
        """Inicializa produtos com configurações base"""
        for product_config in self.PRIORITY_PRODUCTS:
            product = self._generate_base_product(product_config)
            self.products[product.sku] = product
    
    def _generate_base_product(self, config: Dict) -> SageProduct:
        """Gera produto base com configurações realistas"""
        
        # Configurações de estoque baseadas no cenário
        stock_config = self.STOCK_CONFIGS[self.scenario]
        
        # Estoque base (diferente para cada produto)
        base_stocks = {
            'LUVAS_NITRILO': {'current': 500, 'min': 100, 'max': 1000, 'reorder': 150},
            'REVOLUTION_NEEDLES': {'current': 200, 'min': 50, 'max': 400, 'reorder': 75},
            'FINELINE_NEEDLES': {'current': 150, 'min': 40, 'max': 300, 'reorder': 60}
        }
        
        base_config = base_stocks[config['sku']]
        
        # Aplicar variação do cenário
        stock_multiplier = self.random_seed.uniform(*stock_config['stock_variance'])
        current_stock = int(base_config['current'] * stock_multiplier)
        
        # Velocidades base (unidades por período)
        velocity_multipliers = {
            'LUVAS_NITRILO': {'daily': 15, 'weekly': 100, 'monthly': 400},
            'REVOLUTION_NEEDLES': {'daily': 8, 'weekly': 50, 'monthly': 200},
            'FINELINE_NEEDLES': {'daily': 6, 'weekly': 40, 'monthly': 160}
        }
        
        velocity_base = velocity_multipliers[config['sku']]
        velocity_multiplier = self.random_seed.uniform(*stock_config['velocity_variance'])
        
        daily_velocity = velocity_base['daily'] * velocity_multiplier
        weekly_velocity = velocity_base['weekly'] * velocity_multiplier
        monthly_velocity = velocity_base['monthly'] * velocity_multiplier
        
        # Calcular cobertura em dias
        coverage_days = (current_stock / daily_velocity) if daily_velocity > 0 else 999
        
        # Determinar status
        if coverage_days < config['lead_time_days']:
            status = StockStatus.RUPTURE_IMMINENT.value
        elif current_stock > base_config['max'] * 1.5:
            status = StockStatus.OVERSTOCK.value
        elif self.random_seed.random() < stock_config['delay_probability']:
            status = StockStatus.SUPPLIER_DELAY.value
        else:
            status = StockStatus.NORMAL.value
        
        # Calcular receita em risco
        revenue_at_risk = self._calculate_revenue_at_risk(
            current_stock, daily_velocity, config['base_price'], coverage_days
        )
        
        # Gerar datas
        end_date = datetime.now().date()
        
        # Data do último pedido (varia de 7 a 45 dias)
        days_since_order = self.random_seed.randint(7, 45)
        last_order_date = (end_date - timedelta(days=days_since_order)).isoformat()
        
        # Data da última entrega (varia de 3 a 30 dias)
        days_since_delivery = self.random_seed.randint(3, 30)
        last_delivery_date = (end_date - timedelta(days=days_since_delivery)).isoformat()
        
        return SageProduct(
            sku=config['sku'],
            name=config['name'],
            category=config['category'],
            current_stock=current_stock,
            min_stock=base_config['min'],
            max_stock=base_config['max'],
            reorder_point=base_config['reorder'],
            unit_cost=config['base_cost'],
            unit_price=config['base_price'],
            supplier=config['supplier'],
            lead_time_days=config['lead_time_days'],
            last_order_date=last_order_date,
            last_delivery_date=last_delivery_date,
            monthly_velocity=monthly_velocity,
            weekly_velocity=weekly_velocity,
            daily_velocity=daily_velocity,
            coverage_days=coverage_days,
            status=status,
            revenue_at_risk=revenue_at_risk
        )
    
    def _calculate_revenue_at_risk(self, current_stock: int, daily_velocity: float, 
                                 unit_price: float, coverage_days: float) -> float:
        """Calcula receita em risco devido a possível falta de estoque"""
        
        # Dias críticos (tempo de reposição + margem de segurança)
        critical_days = 7  # uma semana de margem
        
        if coverage_days < critical_days:
            # Estima unidades que faltarão
            missing_days = critical_days - coverage_days
            missing_units = missing_days * daily_velocity
            return missing_units * unit_price
        
        return 0.0
    
    def set_scenario(self, scenario: str):
        """Define cenário de teste: normal, rupture_imminent, overstock, supplier_delay"""
        if scenario not in self.STOCK_CONFIGS:
            raise ValueError(f"Cenário inválido. Use: {list(self.STOCK_CONFIGS.keys())}")
        
        self.scenario = scenario
        logger.info(f"📦 Cenário definido: {scenario}")
        
        # Recriar produtos com novo cenário
        self._initialize_products()
    
    def get_inventory_status(self, sku: Optional[str] = None) -> Dict:
        """
        Retorna status do inventário
        
        Args:
            sku: SKU específico ou None para todos os produtos
        """
        if sku:
            if sku not in self.products:
                return {'success': False, 'error': f'Produto {sku} não encontrado'}
            
            product = self.products[sku]
            return {
                'success': True,
                'company_code': self.company_code,
                'scenario': self.scenario,
                'product': product.to_dict(),
                'generated_at': datetime.now().isoformat()
            }
        
        # Retornar todos os produtos
        products_data = [product.to_dict() for product in self.products.values()]
        
        # Calcular agregados
        total_stock_value = sum(p.total_value for p in self.products.values())
        total_revenue_at_risk = sum(p.revenue_at_risk for p in self.products.values())
        products_below_reorder = sum(1 for p in self.products.values() if p.is_below_reorder_point)
        
        summary = {
            'total_products': len(self.products),
            'total_stock_value': round(total_stock_value, 2),
            'total_revenue_at_risk': round(total_revenue_at_risk, 2),
            'products_below_reorder': products_below_reorder,
            'products_out_of_stock': sum(1 for p in self.products.values() if p.is_out_of_stock),
            'avg_coverage_days': round(sum(p.coverage_days for p in self.products.values()) / len(self.products), 2),
            'scenario': self.scenario,
            'generated_at': datetime.now().isoformat()
        }
        
        return {
            'success': True,
            'company_code': self.company_code,
            'summary': summary,
            'products': products_data
        }
    
    def get_product_velocity(self, sku: str, period: str = '30d') -> Dict:
        """
        Retorna velocidade de vendas do produto
        
        Args:
            sku: SKU do produto
            period: período (7d, 30d, 90d)
        """
        if sku not in self.products:
            return {'success': False, 'error': f'Produto {sku} não encontrado'}
        
        product = self.products[sku]
        
        # Simular histórico de velocidades com variações
        velocity_data = self._generate_velocity_history(sku, period)
        
        # Análise de tendência
        trend = self._analyze_velocity_trend(velocity_data)
        
        return {
            'success': True,
            'sku': sku,
            'product_name': product.name,
            'period': period,
            'current_velocity': {
                'daily': product.daily_velocity,
                'weekly': product.weekly_velocity,
                'monthly': product.monthly_velocity
            },
            'velocity_history': velocity_data,
            'trend': trend,
            'generated_at': datetime.now().isoformat()
        }
    
    def _generate_velocity_history(self, sku: str, period: str) -> List[Dict]:
        """Gera histórico de velocidades com variações realistas"""
        product = self.products[sku]
        
        # Determinar número de períodos baseado no intervalo
        if period == '7d':
            periods = 7
            period_type = 'daily'
            base_velocity = product.daily_velocity
        elif period == '30d':
            periods = 4  # semanas
            period_type = 'weekly'
            base_velocity = product.weekly_velocity
        else:  # 90d
            periods = 3  # meses
            period_type = 'monthly'
            base_velocity = product.monthly_velocity
        
        history = []
        for i in range(periods):
            # Aplicar variações realistas
            variance = self.random_seed.uniform(0.7, 1.4)
            seasonal_factor = 1 + (self.random_seed.uniform(-0.2, 0.3) * 
                                 self.random_seed.sin(i * 0.5))
            
            velocity = base_velocity * variance * seasonal_factor
            
            date = datetime.now() - timedelta(
                days=i if period_type == 'daily' else 
                i*7 if period_type == 'weekly' else i*30
            )
            
            history.append({
                'date': date.isoformat(),
                'velocity': round(velocity, 2),
                'variance_factor': round(variance, 2),
                'seasonal_factor': round(seasonal_factor, 2)
            })
        
        return list(reversed(history))
    
    def _analyze_velocity_trend(self, velocity_data: List[Dict]) -> Dict:
        """Analisa tendência da velocidade"""
        if len(velocity_data) < 2:
            return {'direction': 'stable', 'change_percentage': 0}
        
        first_velocity = velocity_data[0]['velocity']
        last_velocity = velocity_data[-1]['velocity']
        
        if first_velocity == 0:
            change_percentage = 0
        else:
            change_percentage = ((last_velocity - first_velocity) / first_velocity) * 100
        
        if change_percentage > 10:
            direction = 'increasing'
        elif change_percentage < -10:
            direction = 'decreasing'
        else:
            direction = 'stable'
        
        return {
            'direction': direction,
            'change_percentage': round(change_percentage, 2)
        }
    
    def simulate_sales(self, days: int = 7) -> Dict:
        """
        Simula vendas por período específico
        
        Args:
            days: número de dias para simular
        """
        sales_data = []
        total_revenue = 0
        total_units = 0
        
        for day in range(days):
            day_date = datetime.now() - timedelta(days=day)
            day_sales = []
            day_revenue = 0
            day_units = 0
            
            for sku, product in self.products.items():
                # Simular vendas diárias com base na velocidade
                daily_sales = int(product.daily_velocity * 
                                self.random_seed.uniform(0.5, 1.5))
                
                # Limitar pelas unidades disponíveis
                daily_sales = min(daily_sales, product.current_stock)
                
                if daily_sales > 0:
                    revenue = daily_sales * product.unit_price
                    day_revenue += revenue
                    day_units += daily_sales
                    
                    day_sales.append({
                        'sku': sku,
                        'product_name': product.name,
                        'units_sold': daily_sales,
                        'revenue': round(revenue, 2),
                        'avg_price': product.unit_price
                    })
                    
                    # Atualizar estoque (simplificado - não persiste)
                    # product.current_stock -= daily_sales
            
            sales_data.append({
                'date': day_date.isoformat(),
                'total_revenue': round(day_revenue, 2),
                'total_units': day_units,
                'products': day_sales
            })
            
            total_revenue += day_revenue
            total_units += day_units
        
        return {
            'success': True,
            'days': days,
            'total_revenue': round(total_revenue, 2),
            'total_units': total_units,
            'avg_daily_revenue': round(total_revenue / days, 2),
            'daily_sales': list(reversed(sales_data))
        }
    
    def check_reorder_needs(self) -> Dict:
        """
        Verifica necessidades de reordenação e gera alertas
        """
        alerts = []
        urgent_products = []
        
        for sku, product in self.products.items():
            # Verificar se precisa de reordenação
            needs_reorder, urgency_days = self._calculate_reorder_urgency(product)
            
            if needs_reorder:
                # Determinar nível de alerta
                alert_level = self._determine_alert_level(product, urgency_days)
                
                # Calcular quantidade sugerida para pedido
                suggested_quantity = self._calculate_order_quantity(product)
                
                # Criar alerta
                alert = StockAlert(
                    alert_id=f"ALERT_{sku}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    sku=sku,
                    product_name=product.name,
                    alert_type='REORDER_NEEDED',
                    alert_level=alert_level.value,
                    current_stock=product.current_stock,
                    reorder_point=product.reorder_point,
                    coverage_days=product.coverage_days,
                    velocity_weekly=product.weekly_velocity,
                    lead_time_days=product.lead_time_days,
                    revenue_at_risk=product.revenue_at_risk,
                    suggested_order_quantity=suggested_quantity,
                    urgency_days=urgency_days,
                    created_at=datetime.now().isoformat()
                )
                
                alerts.append(alert.to_dict())
                
                if urgency_days <= 7:  # Muito urgente
                    urgent_products.append({
                        'sku': sku,
                        'name': product.name,
                        'urgency_days': urgency_days,
                        'current_stock': product.current_stock,
                        'revenue_at_risk': product.revenue_at_risk
                    })
        
        # Armazenar alertas
        self.alerts = alerts
        
        return {
            'success': True,
            'total_alerts': len(alerts),
            'urgent_alerts': len(urgent_products),
            'alerts': alerts,
            'urgent_products': urgent_products,
            'generated_at': datetime.now().isoformat()
        }
    
    def _calculate_reorder_urgency(self, product: SageProduct) -> tuple[bool, int]:
        """Calcula urgência da reordenação"""
        
        # Dias até atingir o ponto de reordenação
        if product.daily_velocity > 0:
            days_to_reorder = (product.current_stock - product.reorder_point) / product.daily_velocity
        else:
            days_to_reorder = 999
        
        # Precisa reordenar se estiver abaixo do ponto ou se faltarão dias
        needs_reorder = (product.current_stock <= product.reorder_point or 
                        days_to_reorder <= product.lead_time_days)
        
        # Dias de urgência (negativo significa que já deveria ter reordenado)
        urgency_days = int(days_to_reorder - product.lead_time_days)
        
        return needs_reorder, urgency_days
    
    def _determine_alert_level(self, product: SageProduct, urgency_days: int) -> AlertLevel:
        """Determina nível do alerta baseado na urgência"""
        if urgency_days <= -7:
            return AlertLevel.CRITICAL
        elif urgency_days <= 0:
            return AlertLevel.HIGH
        elif urgency_days <= 7:
            return AlertLevel.MEDIUM
        else:
            return AlertLevel.LOW
    
    def _calculate_order_quantity(self, product: SageProduct) -> int:
        """Calcula quantidade sugerida para pedido"""
        
        # Quantidade para atingir estoque máximo
        quantity_to_max = product.max_stock - product.current_stock
        
        # Quantidade para cobrir período de reposição + margem de segurança
        safety_stock = product.daily_velocity * 7  # uma semana de segurança
        reorder_quantity = (product.daily_velocity * product.lead_time_days) + safety_stock
        
        # Usar o maior valor
        suggested_quantity = max(quantity_to_max, reorder_quantity)
        
        # Arredondar para múltiplo de 10 para pedidos práticos
        return int(round(suggested_quantity / 10) * 10)
    
    def generate_purchase_suggestion(self, sku: str) -> Dict:
        """
        Gera sugestão detalhada de compra para produto específico
        
        Args:
            sku: SKU do produto
        """
        if sku not in self.products:
            return {'success': False, 'error': f'Produto {sku} não encontrado'}
        
        product = self.products[sku]
        
        # Análise detalhada
        needs_reorder, urgency_days = self._calculate_reorder_urgency(product)
        suggested_quantity = self._calculate_order_quantity(product)
        
        # Cálculos financeiros
        order_cost = suggested_quantity * product.unit_cost
        expected_revenue = suggested_quantity * product.unit_price
        expected_margin = expected_revenue - order_cost
        
        # Análise de risco
        risk_analysis = self._analyze_purchase_risk(product, suggested_quantity)
        
        # Fornecedores alternativos (simulados)
        alternative_suppliers = self._get_alternative_suppliers(product)
        
        return {
            'success': True,
            'sku': sku,
            'product_name': product.name,
            'current_status': {
                'stock': product.current_stock,
                'coverage_days': product.coverage_days,
                'revenue_at_risk': product.revenue_at_risk
            },
            'suggestion': {
                'needs_reorder': needs_reorder,
                'urgency_days': urgency_days,
                'suggested_quantity': suggested_quantity,
                'order_cost': round(order_cost, 2),
                'expected_revenue': round(expected_revenue, 2),
                'expected_margin': round(expected_margin, 2),
                'margin_percentage': round((expected_margin / expected_revenue) * 100, 2) if expected_revenue > 0 else 0
            },
            'timing_analysis': {
                'lead_time_days': product.lead_time_days,
                'safety_stock_days': 7,
                'recommended_order_date': (datetime.now() + timedelta(days=max(0, urgency_days))).isoformat(),
                'expected_delivery_date': (datetime.now() + timedelta(days=product.lead_time_days)).isoformat()
            },
            'risk_analysis': risk_analysis,
            'alternative_suppliers': alternative_suppliers,
            'generated_at': datetime.now().isoformat()
        }
    
    def _analyze_purchase_risk(self, product: SageProduct, suggested_quantity: int) -> Dict:
        """Analisa riscos da compra sugerida"""
        
        # Risco de excesso de estoque
        excess_risk = 'HIGH' if (product.current_stock + suggested_quantity) > product.max_stock * 1.5 else 'LOW'
        
        # Risco de obsolescência (para produtos com validade)
        obsolescence_risk = 'MEDIUM' if product.category in ['AGULHAS'] else 'LOW'
        
        # Risco financeiro
        order_value = suggested_quantity * product.unit_cost
        financial_risk = 'HIGH' if order_value > 5000 else 'MEDIUM' if order_value > 2000 else 'LOW'
        
        return {
            'excess_risk': excess_risk,
            'obsolescence_risk': obsolescence_risk,
            'financial_risk': financial_risk,
            'order_value': order_value
        }
    
    def _get_alternative_suppliers(self, product: SageProduct) -> List[Dict]:
        """Retorna fornecedores alternativos simulados"""
        
        # Fornecedores alternativos por categoria
        supplier_options = {
            'PROTEÇÃO': [
                {'name': 'PROTECT_BRASIL', 'lead_time': 10, 'cost_factor': 0.95},
                {'name': 'SAFETY_IMPORT', 'lead_time': 21, 'cost_factor': 0.85}
            ],
            'AGULHAS': [
                {'name': 'NEEDLE_MASTER_USA', 'lead_time': 14, 'cost_factor': 1.1},
                {'name': 'PRECISION_TATTOO', 'lead_time': 18, 'cost_factor': 0.9}
            ]
        }
        
        alternatives = []
        for supplier in supplier_options.get(product.category, []):
            alternatives.append({
                'supplier_name': supplier['name'],
                'lead_time_days': supplier['lead_time'],
                'unit_cost': round(product.unit_cost * supplier['cost_factor'], 2),
                'cost_difference': f"{((supplier['cost_factor'] - 1) * 100):+.1f}%"
            })
        
        return alternatives
    
    def generate_alert_scenario(self) -> Dict:
        """Gera cenário com alertas para teste"""
        self.set_scenario('rupture_imminent')
        
        # Forçar produto crítico
        critical_product = self.products['LUVAS_NITRILO']
        critical_product.current_stock = 5  # Estoque crítico
        critical_product.daily_velocity = 20  # Alta velocidade
        critical_product.coverage_days = 0.25  # Poucas horas de estoque
        critical_product.revenue_at_risk = 5000
        
        # Recalcular alertas
        alerts_data = self.check_reorder_needs()
        
        return {
            'success': True,
            'scenario': 'test_alert',
            'critical_product': critical_product.to_dict(),
            'alerts_data': alerts_data,
            'generated_at': datetime.now().isoformat()
        }
    
    def get_financial_summary(self) -> Dict:
        """Retorna resumo financeiro do inventário"""
        total_value = sum(p.total_value for p in self.products.values())
        total_revenue_at_risk = sum(p.revenue_at_risk for p in self.products.values())
        
        # Análise por categoria
        category_analysis = {}
        for product in self.products.values():
            if product.category not in category_analysis:
                category_analysis[product.category] = {
                    'products': 0,
                    'total_value': 0,
                    'total_stock': 0,
                    'revenue_at_risk': 0
                }
            
            cat = category_analysis[product.category]
            cat['products'] += 1
            cat['total_value'] += product.total_value
            cat['total_stock'] += product.current_stock
            cat['revenue_at_risk'] += product.revenue_at_risk
        
        # Formatar valores
        for cat_data in category_analysis.values():
            cat_data['total_value'] = round(cat_data['total_value'], 2)
            cat_data['revenue_at_risk'] = round(cat_data['revenue_at_risk'], 2)
        
        return {
            'success': True,
            'total_inventory_value': round(total_value, 2),
            'total_revenue_at_risk': round(total_revenue_at_risk, 2),
            'category_breakdown': category_analysis,
            'risk_percentage': round((total_revenue_at_risk / total_value) * 100, 2) if total_value > 0 else 0,
            'generated_at': datetime.now().isoformat()
        }