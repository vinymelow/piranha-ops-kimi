"""
WhatsApp Mock - PiranhaOps AIOS v4.0 - Revenue Activation
Simulador da Evolution API para automação B2B
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import uuid


@dataclass
class WhatsAppMessage:
    """Representa uma mensagem WhatsApp"""
    phone_number: str
    message: str
    template_name: str
    message_id: str
    status: str
    timestamp: str


class WhatsAppMock:
    """Mock do WhatsApp Business API para testes"""
    
    def __init__(self):
        self.test_data = {}
        self.message_templates = {}
        self.initialize_test_data()
        
    def initialize_test_data(self):
        """Inicializa dados e templates de teste"""
        self.message_templates = {
            'promocao_especial': {
                'name': 'promocao_especial',
                'language': 'pt_BR',
                'category': 'MARKETING',
                'components': [
                    {
                        'type': 'HEADER',
                        'format': 'TEXT',
                        'text': '🔥 Oferta Especial!'
                    },
                    {
                        'type': 'BODY',
                        'text': 'Olá {{1}}! Temos uma oferta especial para você: {{2}}% de desconto em {{3}}. Não perca tempo, essa oferta termina em {{4}} dias!'
                    },
                    {
                        'type': 'FOOTER',
                        'text': 'Equipe Tattoo Supply'
                    }
                ]
            },
            'abandoned_cart_reminder': {
                'name': 'abandoned_cart_reminder',
                'language': 'pt_BR',
                'category': 'UTILITY',
                'components': [
                    {
                        'type': 'HEADER',
                        'format': 'TEXT',
                        'text': '🛒 Carrinho Abandonado'
                    },
                    {
                        'type': 'BODY',
                        'text': 'Olá {{1}}! Você deixou itens no seu carrinho. Complete sua compra agora e ganhe {{2}}% de desconto com o código {{3}}!'
                    },
                    {
                        'type': 'BUTTONS',
                        'buttons': [
                            {'type': 'URL', 'text': 'Completar Compra', 'url': '{{4}}'},
                            {'type': 'QUICK_REPLY', 'text': 'Ver Carrinho'}
                        ]
                    }
                ]
            },
            'stock_alert': {
                'name': 'stock_alert',
                'language': 'pt_BR',
                'category': 'UTILITY',
                'components': [
                    {
                        'type': 'BODY',
                        'text': '⚠️ Estoque Baixo! O produto {{1}} está com apenas {{2}} unidades restantes. Últimas unidades!'
                    }
                ]
            },
            'lead_qualification': {
                'name': 'lead_qualification',
                'language': 'pt_BR',
                'category': 'UTILITY',
                'components': [
                    {
                        'type': 'BODY',
                        'text': 'Olá {{1}}! Obrigado pelo seu interesse em nossos produtos. Você tem alguns minutos para conversarmos sobre suas necessidades?'
                    },
                    {
                        'type': 'BUTTONS',
                        'buttons': [
                            {'type': 'QUICK_REPLY', 'text': 'Sim, tenho interesse'},
                            {'type': 'QUICK_REPLY', 'text': 'Não, obrigado'}
                        ]
                    }
                ]
            }
        }
        
    def send_message(self, messages: List[Dict[str, Any]], 
                    template: str,
                    campaign_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Envia mensagens WhatsApp usando template
        
        Args:
            messages: Lista de mensagens com dados dos destinatários
            template: Nome do template a usar
            campaign_id: ID opcional da campanha
            
        Returns:
            Dict com resultados do envio
        """
        if template not in self.message_templates:
            return {
                'success': False,
                'error': f'Template {template} não encontrado',
                'available_templates': list(self.message_templates.keys())
            }
        
        message_ids = []
        delivered_to = []
        failed_deliveries = []
        total_cost = 0
        
        template_config = self.message_templates[template]
        
        for message_data in messages:
            phone_number = message_data.get('phone_number')
            if not phone_number:
                failed_deliveries.append({'error': 'Número de telefone não fornecido'})
                continue
                
            # Validar formato do telefone (simplificado)
            if not phone_number.startswith('+'):
                phone_number = '+55' + phone_number
                
            # Gerar ID único da mensagem
            message_id = str(uuid.uuid4())
            
            # Calcular custo (R$0.05 por mensagem para templates aprovados)
            message_cost = 0.05
            total_cost += message_cost
            
            # Simular envio bem-sucedido (95% de taxa de sucesso)
            import random
            if random.random() < 0.95:
                message_ids.append(message_id)
                delivered_to.append(phone_number)
            else:
                failed_deliveries.append({
                    'phone_number': phone_number,
                    'error': 'Falha no envio'
                })
        
        delivery_rate = (len(delivered_to) / len(messages)) * 100 if messages else 0
        
        return {
            'success': True,
            'message_ids': message_ids,
            'delivered_to': delivered_to,
            'failed_deliveries': failed_deliveries,
            'delivery_rate': round(delivery_rate, 2),
            'cost': round(total_cost, 2),
            'template_used': template,
            'campaign_id': campaign_id,
            'messages_sent': len(delivered_to),
            'timestamp': datetime.now().isoformat()
        }
        
    def send_abandoned_cart_reminder(self, abandoned_carts: List[Dict[str, Any]], 
                                   reminder_type: str = 'first_reminder',
                                   discount_offer: Optional[int] = None) -> Dict[str, Any]:
        """Envia lembrete de carrinho abandonado"""
        
        total_recovery_value = 0
        messages_sent = 0
        total_cost = 0
        
        for cart in abandoned_carts:
            customer_phone = cart.get('customer_phone') or '+5511999999999'
            cart_value = cart.get('total_value', 0)
            customer_name = cart.get('customer_name', 'Cliente')
            
            # Calcular valor estimado de recuperação
            recovery_rate = 0.15  # 15% taxa média de recuperação
            estimated_recovery = cart_value * recovery_rate
            total_recovery_value += estimated_recovery
            
            # Preparar mensagem com template
            message_data = {
                'phone_number': customer_phone,
                'customer_name': customer_name,
                'discount_percentage': discount_offer or 10,
                'discount_code': f'RECOVERY{discount_offer or 10}',
                'cart_url': f'https://loja.com/cart/{cart.get("cart_id", "default")}'
            }
            
            # Simular envio
            result = self.send_message(
                messages=[message_data],
                template='abandoned_cart_reminder',
                campaign_id=f'abandoned_cart_{datetime.now().strftime("%Y%m%d")}'
            )
            
            if result['success']:
                messages_sent += result['messages_sent']
                total_cost += result['cost']
        
        # Calcular ROI estimado
        roi = (total_recovery_value - total_cost) / total_cost if total_cost > 0 else 0
        
        return {
            'success': True,
            'messages_sent': messages_sent,
            'template_used': 'abandoned_cart_reminder',
            'reminder_type': reminder_type,
            'discount_offer': discount_offer,
            'estimated_recovery_value': round(total_recovery_value, 2),
            'cost': round(total_cost, 2),
            'estimated_roi': round(roi, 2),
            'timestamp': datetime.now().isoformat()
        }
        
    def send_stock_alert(self, stock_data: Dict[str, Any], 
                        alert_type: str = 'low_stock') -> Dict[str, Any]:
        """Envia alerta de estoque"""
        
        # Definir destinatários com base no tipo de alerta
        recipients = {
            'low_stock': ['compras@empresa.com', 'estoque@empresa.com'],
            'critical_stock': ['compras@empresa.com', 'estoque@empresa.com', 'gerencia@empresa.com'],
            'out_of_stock': ['compras@empresa.com', 'estoque@empresa.com', 'gerencia@empresa.com', 'vendas@empresa.com']
        }
        
        recipient_list = recipients.get(alert_type, recipients['low_stock'])
        
        # Converter emails para números WhatsApp (mock)
        phone_numbers = []
        for email in recipient_list:
            # Simular conversão de email para WhatsApp
            if 'compras' in email:
                phone_numbers.append('+5511987654321')
            elif 'estoque' in email:
                phone_numbers.append('+5511987654322')
            elif 'gerencia' in email:
                phone_numbers.append('+5511987654323')
            elif 'vendas' in email:
                phone_numbers.append('+5511987654324')
        
        messages = []
        for phone in phone_numbers:
            message_data = {
                'phone_number': phone,
                'product_name': stock_data.get('product_name', 'Produto'),
                'current_stock': stock_data.get('current_stock', 0),
                'sku': stock_data.get('sku', 'SKU_UNKNOWN')
            }
            messages.append(message_data)
        
        # Enviar alertas
        result = self.send_message(
            messages=messages,
            template='stock_alert',
            campaign_id=f'stock_alert_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        )
        
        # Determinar nível de urgência
        current_stock = stock_data.get('current_stock', 0)
        reorder_point = stock_data.get('reorder_point', 50)
        
        if current_stock <= 0:
            urgency_level = 'critical'
            estimated_impact = 'high'
        elif current_stock <= reorder_point * 0.2:
            urgency_level = 'critical'
            estimated_impact = 'high'
        elif current_stock <= reorder_point * 0.5:
            urgency_level = 'high'
            estimated_impact = 'medium'
        else:
            urgency_level = 'medium'
            estimated_impact = 'low'
        
        return {
            'alert_sent': result['success'],
            'recipients': recipient_list,
            'alert_level': urgency_level,
            'estimated_impact': estimated_impact,
            'recommended_actions': [
                'Contactar fornecedor urgente' if urgency_level == 'critical' else 'Verificar próxima entrega',
                'Reduzir investimento em mídia para este SKU' if urgency_level in ['critical', 'high'] else 'Monitorar consumo',
                'Buscar fornecedor alternativo' if urgency_level == 'critical' else None
            ],
            'timestamp': datetime.now().isoformat()
        }
        
    def send_lead_qualification_message(self, leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Envia mensagem de qualificação para leads"""
        
        qualified_leads = []
        messages_sent = 0
        total_cost = 0
        
        for lead in leads:
            if lead.get('score', 0) >= 70:  # Apenas leads qualificados
                phone_number = lead.get('phone', '+5511999999999')
                lead_name = lead.get('name', 'Lead')
                
                message_data = {
                    'phone_number': phone_number,
                    'lead_name': lead_name.split()[0] if ' ' in lead_name else lead_name
                }
                
                result = self.send_message(
                    messages=[message_data],
                    template='lead_qualification',
                    campaign_id=f'lead_qual_{datetime.now().strftime("%Y%m%d")}'
                )
                
                if result['success']:
                    qualified_leads.append(lead)
                    messages_sent += result['messages_sent']
                    total_cost += result['cost']
        
        return {
            'success': True,
            'leads_contacted': len(qualified_leads),
            'messages_sent': messages_sent,
            'cost': round(total_cost, 2),
            'qualification_rate': round(len(qualified_leads) / len(leads) * 100, 2) if leads else 0,
            'timestamp': datetime.now().isoformat()
        }
        
    def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """Retorna status de uma mensagem"""
        
        # Simular status possíveis
        import random
        statuses = ['sent', 'delivered', 'read', 'failed']
        status_weights = [0.1, 0.3, 0.5, 0.1]  # 50% chance de read
        
        current_status = random.choices(statuses, weights=status_weights)[0]
        
        return {
            'message_id': message_id,
            'status': current_status,
            'timestamp': datetime.now().isoformat(),
            'delivered_at': datetime.now().isoformat() if current_status in ['delivered', 'read'] else None,
            'read_at': datetime.now().isoformat() if current_status == 'read' else None
        }
        
    def get_template_list(self) -> List[Dict[str, Any]]:
        """Retorna lista de templates disponíveis"""
        
        templates_list = []
        for template_name, template_data in self.message_templates.items():
            templates_list.append({
                'name': template_name,
                'language': template_data['language'],
                'category': template_data['category'],
                'status': 'APPROVED',
                'created_at': '2024-01-01T00:00:00Z'
            })
        
        return templates_list
        
    def get_account_info(self) -> Dict[str, Any]:
        """Retorna informações da conta WhatsApp Business"""
        
        return {
            'business_account_id': '1234567890',
            'phone_number': '+551140028922',
            'display_name': 'Tattoo Supply Brasil',
            'verified_status': 'VERIFIED',
            'quality_rating': 'HIGH',
            'messaging_limit_tier': 'TIER_1000',
            'webhooks_registered': True
        }