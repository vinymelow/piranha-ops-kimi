"""
Inventory Pro Mock - PiranhaOps AIOS v4.0 - Revenue Activation
Sistema de forecast preditivo para gestão de estoque
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import random
import math


@dataclass
class ProductForecast:
    """Representa uma previsão de produto"""
    sku: str
    product_name: str
    current_stock: int
    forecast_demand: int
    reorder_point: int
    safety_stock: int
    lead_time_days: int
    supplier: str
    last_order_date: str
    unit_cost: float
    selling_price: float


class InventoryForecastMock:
    """Mock do sistema de previsão de inventário"""
    
    def __init__(self):
        self.product_database = []
        self.forecast_models = {}
        self.suppliers = {}
        self.initialize_test_data()
        
    def initialize_test_data(self):
        """Inicializa dados de teste"""
        self.suppliers = {
            'Fornecedor ABC': {
                'name': 'Fornecedor ABC',
                'lead_time_days': 14,
                'reliability': 0.95,
                'minimum_order': 50,
                'payment_terms': '30 dias',
                'contact': 'contato@fornecedorabc.com'
            },
            'Fornecedor XYZ': {
                'name': 'Fornecedor XYZ',
                'lead_time_days': 7,
                'reliability': 0.88,
                'minimum_order': 25,
                'payment_terms': '15 dias',
                'contact': 'vendas@fornecedorxyz.com'
            },
            'Fornecedor Premium': {
                'name': 'Fornecedor Premium',
                'lead_time_days': 21,
                'reliability': 0.98,
                'minimum_order': 100,
                'payment_terms': '45 dias',
                'contact': 'premium@fornecedor.com'
            }
        }
        
        # Produtos de teste
        base_products = [
            {'sku': 'SKU001', 'name': 'Tattoo Ink Preto Profissional 30ml', 'category': 'tintas'},
            {'sku': 'SKU002', 'name': 'Agulhas Tattoo Round Liner #12', 'category': 'agulhas'},
            {'sku': 'SKU003', 'name': 'Máquina Tattoo Rotary Premium', 'category': 'maquinas'},
            {'sku': 'SKU004', 'name': 'Folha de Transferência A4', 'category': 'papéis'},
            {'sku': 'SKU005', 'name': 'Luvas Nitrílicas Tamanho M', 'category': 'epi'},
            {'sku': 'SKU006', 'name': 'Pigmento Vermelho Tattoo 15ml', 'category': 'tintas'},
            {'sku': 'SKU007', 'name': 'Agulhas Tattoo Magnum #15', 'category': 'agulhas'},
            {'sku': 'SKU008', 'name': 'Fonte de Alimentação Tattoo 12V', 'category': 'acessorios'},
            {'sku': 'SKU009', 'name': 'Creme Pós-Tattoo 50g', 'category': 'pos_procedimento'},
            {'sku': 'SKU010', 'name': 'Algodão Hidrófilo 500g', 'category': 'consumiveis'}
        ]
        
        # Gerar estoque inicial
        for i, product in enumerate(base_products):
            current_stock = random.randint(20, 200)
            monthly_demand = random.randint(50, 300)
            
            product_data = {
                'sku': product['sku'],
                'product_name': product['name'],
                'category': product['category'],
                'current_stock': current_stock,
                'forecast_demand': monthly_demand,
                'reorder_point': int(monthly_demand * 0.3),  # 30% da demanda mensal
                'safety_stock': int(monthly_demand * 0.1),  # 10% de segurança
                'lead_time_days': random.choice([7, 14, 21]),
                'supplier': random.choice(list(self.suppliers.keys())),
                'last_order_date': (datetime.now() - timedelta(days=random.randint(1, 60))).isoformat(),
                'unit_cost': round(random.uniform(5, 150), 2),
                'selling_price': 0,  # Será calculado
                'seasonal_factor': random.uniform(0.8, 1.5),
                'trend_factor': random.uniform(0.9, 1.3)
            }
            
            # Calcular preço de venda (custo + 60% de margem)
            product_data['selling_price'] = round(product_data['unit_cost'] * 1.6, 2)
            
            self.product_database.append(product_data)
            
    def get_forecast(self, skus: List[str], 
                    forecast_days: int = 30,
                    confidence_level: float = 0.95) -> Dict[str, Any]:
        """
        Gera previsão de demanda e análise de estoque
        
        Args:
            skus: Lista de SKUs para analisar
            forecast_days: Número de dias para previsão
            confidence_level: Nível de confiança da previsão
            
        Returns:
            Dict com previsões e alertas
        """
        products_forecast = []
        alerts = []
        
        for sku in skus:
            product = self._get_product_by_sku(sku)
            if not product:
                continue
                
            # Calcular previsão de demanda
            daily_demand = product['forecast_demand'] / 30  # Demanda diária média
            forecasted_demand = daily_demand * forecast_days
            
            # Aplicar fatores sazonais e de tendência
            adjusted_demand = forecasted_demand * product['seasonal_factor'] * product['trend_factor']
            
            # Calcular níveis críticos
            days_of_stock = product['current_stock'] / daily_demand if daily_demand > 0 else float('inf')
            stockout_date = datetime.now() + timedelta(days=days_of_stock)
            
            # Gerar alertas baseados em regras
            if product['current_stock'] <= product['safety_stock']:
                alerts.append({
                    'sku': sku,
                    'alert_type': 'critical_stock',
                    'current_stock': product['current_stock'],
                    'safety_stock': product['safety_stock'],
                    'urgency': 'critical',
                    'message': f'Estoque crítico para {product["product_name"]}'
                })
            elif product['current_stock'] <= product['reorder_point']:
                alerts.append({
                    'sku': sku,
                    'alert_type': 'reorder_point',
                    'current_stock': product['current_stock'],
                    'reorder_point': product['reorder_point'],
                    'urgency': 'high',
                    'message': f'Ponto de reabastecimento atingido para {product["product_name"]}'
                })
            elif days_of_stock <= product['lead_time_days']:
                alerts.append({
                    'sku': sku,
                    'alert_type': 'lead_time_risk',
                    'current_stock': product['current_stock'],
                    'days_of_stock': round(days_of_stock, 1),
                    'lead_time_days': product['lead_time_days'],
                    'urgency': 'medium',
                    'message': f'Risco de falta de estoque antes da próxima entrega para {product["product_name"]}'
                })
            
            # Preparar previsão do produto
            product_forecast = {
                'sku': sku,
                'product_name': product['product_name'],
                'category': product['category'],
                'current_stock': product['current_stock'],
                'forecast_demand': round(adjusted_demand, 0),
                'daily_demand': round(daily_demand, 2),
                'reorder_point': product['reorder_point'],
                'safety_stock': product['safety_stock'],
                'lead_time_days': product['lead_time_days'],
                'supplier': product['supplier'],
                'last_order_date': product['last_order_date'],
                'stockout_date': stockout_date.isoformat(),
                'days_until_stockout': round(days_of_stock, 1),
                'unit_cost': product['unit_cost'],
                'selling_price': product['selling_price'],
                'inventory_value': round(product['current_stock'] * product['unit_cost'], 2),
                'recommended_order_quantity': self._calculate_order_quantity(product, adjusted_demand),
                'confidence_level': confidence_level
            }
            
            products_forecast.append(product_forecast)
        
        # Calcular resumo geral
        total_products = len(products_forecast)
        products_with_alerts = len(alerts)
        critical_alerts = len([a for a in alerts if a['urgency'] == 'critical'])
        high_alerts = len([a for a in alerts if a['urgency'] == 'high'])
        
        total_forecast_value = sum(p['forecast_demand'] * p['unit_cost'] for p in products_forecast)
        total_inventory_value = sum(p['inventory_value'] for p in products_forecast)
        
        return {
            'products': products_forecast,
            'alerts': alerts,
            'summary': {
                'total_products': total_products,
                'products_with_alerts': products_with_alerts,
                'critical_alerts': critical_alerts,
                'high_alerts': high_alerts,
                'total_forecast_value': round(total_forecast_value, 2),
                'total_inventory_value': round(total_inventory_value, 2),
                'forecast_period_days': forecast_days,
                'average_days_until_stockout': round(sum(p['days_until_stockout'] for p in products_forecast) / total_products, 1) if total_products > 0 else 0
            },
            'timestamp': datetime.now().isoformat()
        }
        
    def _get_product_by_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        """Retorna produto pelo SKU"""
        for product in self.product_database:
            if product['sku'] == sku:
                return product
        return None
        
    def _calculate_order_quantity(self, product: Dict[str, Any], forecasted_demand: float) -> int:
        """Calcula quantidade recomendada de pedido"""
        
        # Quantidade para cobrir período de lead time + segurança
        daily_demand = forecasted_demand / 30
        lead_time_demand = daily_demand * product['lead_time_days']
        
        # Adicionar estoque de segurança
        total_needed = lead_time_demand + product['safety_stock']
        
        # Subtrair estoque atual
        order_quantity = max(0, int(total_needed - product['current_stock']))
        
        # Considerar pedido mínimo do fornecedor
        supplier = self.suppliers.get(product['supplier'], {})
        minimum_order = supplier.get('minimum_order', 1)
        
        if order_quantity > 0 and order_quantity < minimum_order:
            order_quantity = minimum_order
            
        return order_quantity
        
    def get_supplier_recommendations(self, sku: str, urgency_level: str = 'medium') -> List[Dict[str, Any]]:
        """Retorna recomendações de fornecedores"""
        
        product = self._get_product_by_sku(sku)
        if not product:
            return []
            
        recommendations = []
        
        # Avaliar cada fornecedor
        for supplier_name, supplier_data in self.suppliers.items():
            score = 0
            
            # Lead time (quanto menor, melhor)
            if urgency_level == 'critical':
                if supplier_data['lead_time_days'] <= 7:
                    score += 40
                elif supplier_data['lead_time_days'] <= 14:
                    score += 20
            else:
                if supplier_data['lead_time_days'] <= 14:
                    score += 30
                elif supplier_data['lead_time_days'] <= 21:
                    score += 15
                    
            # Confiabilidade
            score += supplier_data['reliability'] * 30
            
            # Termos de pagamento (quanto mais longo, melhor)
            if '45 dias' in supplier_data['payment_terms']:
                score += 20
            elif '30 dias' in supplier_data['payment_terms']:
                score += 15
            elif '15 dias' in supplier_data['payment_terms']:
                score += 10
                
            # Pedido mínimo (se atende à necessidade)
            recommended_quantity = self._calculate_order_quantity(product, product['forecast_demand'])
            if recommended_quantity >= supplier_data['minimum_order']:
                score += 10
            else:
                score -= 5
                
            recommendations.append({
                'supplier': supplier_name,
                'score': round(score, 1),
                'lead_time_days': supplier_data['lead_time_days'],
                'reliability': supplier_data['reliability'],
                'payment_terms': supplier_data['payment_terms'],
                'minimum_order': supplier_data['minimum_order'],
                'contact': supplier_data['contact'],
                'recommended': score >= 70
            })
        
        # Ordenar por score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations
        
    def get_seasonal_forecast(self, sku: str, months_ahead: int = 6) -> Dict[str, Any]:
        """Retorna previsão sazonal para um produto"""
        
        product = self._get_product_by_sku(sku)
        if not product:
            return {'error': 'Produto não encontrado'}
            
        seasonal_multipliers = {
            1: 1.2,   # Janeiro - alta temporada
            2: 1.1,   # Fevereiro
            3: 0.9,   # Março
            4: 0.8,   # Abril
            5: 0.85,  # Maio
            6: 0.9,   # Junho
            7: 0.95,  # Julho
            8: 1.0,   # Agosto
            9: 1.1,   # Setembro
            10: 1.15, # Outubro
            11: 1.25, # Novembro - alta temporada
            12: 1.3   # Dezembro - alta temporada
        }
        
        monthly_forecasts = []
        current_month = datetime.now().month
        
        for i in range(months_ahead):
            month = (current_month + i - 1) % 12 + 1
            multiplier = seasonal_multipliers.get(month, 1.0)
            
            base_monthly_demand = product['forecast_demand']
            adjusted_demand = base_monthly_demand * multiplier
            
            monthly_forecasts.append({
                'month': month,
                'month_name': self._get_month_name(month),
                'seasonal_multiplier': multiplier,
                'base_demand': base_monthly_demand,
                'adjusted_demand': round(adjusted_demand, 0),
                'stock_needed': round(adjusted_demand * 1.2, 0)  # Adicionar 20% de buffer
            })
        
        return {
            'sku': sku,
            'product_name': product['product_name'],
            'monthly_forecasts': monthly_forecasts,
            'peak_seasons': [m for m in monthly_forecasts if m['seasonal_multiplier'] > 1.1],
            'low_seasons': [m for m in monthly_forecasts if m['seasonal_multiplier'] < 0.9]
        }
        
    def _get_month_name(self, month: int) -> str:
        """Retorna nome do mês em português"""
        months = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        return months[month - 1]
        
    def get_inventory_turnover(self, sku: str, period_days: int = 30) -> Dict[str, Any]:
        """Calcula giro de inventário"""
        
        product = self._get_product_by_sku(sku)
        if not product:
            return {'error': 'Produto não encontrado'}
            
        # Simular vendas do período
        units_sold = int(product['forecast_demand'] * (period_days / 30))
        average_inventory = (product['current_stock'] + product['reorder_point']) / 2
        
        turnover_ratio = units_sold / average_inventory if average_inventory > 0 else 0
        days_to_turn = period_days / turnover_ratio if turnover_ratio > 0 else float('inf')
        
        # Classificar giro
        if turnover_ratio >= 12:
            turnover_classification = 'Excelente'
        elif turnover_ratio >= 6:
            turnover_classification = 'Bom'
        elif turnover_ratio >= 3:
            turnover_classification = 'Regular'
        else:
            turnover_classification = 'Baixo'
            
        return {
            'sku': sku,
            'product_name': product['product_name'],
            'period_days': period_days,
            'units_sold': units_sold,
            'average_inventory': round(average_inventory, 2),
            'turnover_ratio': round(turnover_ratio, 2),
            'days_to_turnover': round(days_to_turn, 1),
            'turnover_classification': turnover_classification,
            'inventory_efficiency': 'Alta' if turnover_ratio >= 6 else 'Baixa'
        }
        
    def create_stock_alert(self, alert_config: Dict[str, Any]) -> Dict[str, Any]:
        """Cria alerta personalizado de estoque"""
        
        alert_id = f"stock_alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            'alert_id': alert_id,
            'alert_name': alert_config.get('name', 'Alerta de Estoque'),
            'skus': alert_config.get('skus', []),
            'trigger_conditions': alert_config.get('conditions', {
                'stock_level': 'below_reorder',
                'days_until_stockout': 7
            }),
            'notification_channels': alert_config.get('channels', ['email', 'whatsapp']),
            'recipients': alert_config.get('recipients', ['estoque@empresa.com']),
            'status': 'active',
            'created_at': datetime.now().isoformat()
        }
        
    def get_low_stock_report(self) -> Dict[str, Any]:
        """Retorna relatório de produtos com estoque baixo"""
        
        low_stock_products = []
        
        for product in self.product_database:
            if product['current_stock'] <= product['reorder_point']:
                days_of_stock = product['current_stock'] / (product['forecast_demand'] / 30)
                
                low_stock_products.append({
                    'sku': product['sku'],
                    'product_name': product['product_name'],
                    'category': product['category'],
                    'current_stock': product['current_stock'],
                    'reorder_point': product['reorder_point'],
                    'days_of_stock': round(days_of_stock, 1),
                    'urgency_level': 'Critical' if product['current_stock'] <= product['safety_stock'] else 'High',
                    'supplier': product['supplier'],
                    'lead_time_days': product['lead_time_days'],
                    'last_order_days_ago': (datetime.now() - datetime.fromisoformat(product['last_order_date'])).days
                })
        
        # Ordenar por urgência
        low_stock_products.sort(key=lambda x: (x['urgency_level'] == 'Critical', x['days_of_stock']))
        
        return {
            'low_stock_products': low_stock_products,
            'total_critical': len([p for p in low_stock_products if p['urgency_level'] == 'Critical']),
            'total_high_priority': len([p for p in low_stock_products if p['urgency_level'] == 'High']),
            'total_value_at_risk': sum(p['current_stock'] * 50 for p in low_stock_products),  # Estimativa
            'report_generated_at': datetime.now().isoformat()
        }