"""
Evolution API Mock - Simulador completo da Evolution API para WhatsApp
Baseado nas especificações do Input V4
"""

import asyncio
import json
import random
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import os
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class InstanceStatus(Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    AUTHENTICATION_FAILURE = "authentication_failure"

@dataclass
class Message:
    id: str
    instance_id: str
    recipient: str
    content: str
    message_type: str
    status: MessageStatus
    timestamp: datetime
    template_name: Optional[str] = None
    template_params: Optional[Dict] = None
    error_message: Optional[str] = None

@dataclass
class RateLimitInfo:
    requests_count: int
    window_start: datetime
    blocked_until: Optional[datetime] = None

class EvolutionMock:
    """
    Simulador completo da Evolution API para WhatsApp
    Implementa todos os métodos especificados no Input V4
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.failure_rate = 0.05  # 5% de falhas
        self.min_delay = 1.0
        self.max_delay = 3.0
        self.rate_limit_window = timedelta(minutes=1)
        self.max_requests_per_window = 30
        
        # Estado das instâncias
        self.instances: Dict[str, InstanceStatus] = {}
        
        # Histórico de mensagens
        self.messages: List[Message] = []
        
        # Controle de rate limit por instância
        self.rate_limits: Dict[str, RateLimitInfo] = {}
        
        # Templates de mensagens
        self.templates = self._load_templates()
        
        # Configuração de persistência
        self.persistence_dir = Path("mock_data")
        self.persistence_dir.mkdir(exist_ok=True)
        
        logger.info("EvolutionMock inicializado com sucesso")
    
    def _load_templates(self) -> Dict[str, Dict]:
        """Carrega templates de mensagens aprovados"""
        return {
            "abandoned_cart_v1": {
                "name": "abandoned_cart_v1",
                "category": "UTILITY",
                "language": "pt_BR",
                "components": [
                    {
                        "type": "header",
                        "parameters": [{"type": "image", "image": {"link": "{{header_image}}"}}]
                    },
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": "{{customer_name}}"},
                            {"type": "text", "text": "{{product_name}}"},
                            {"type": "text", "text": "{{discount_percentage}}"},
                            {"type": "text", "text": "{{discount_code}}"},
                            {"type": "text", "text": "{{validity_hours}}"}
                        ]
                    },
                    {
                        "type": "button",
                        "sub_type": "url",
                        "index": "0",
                        "parameters": [{"type": "text", "text": "{{checkout_url}}"}]
                    }
                ]
            },
            "stock_alert_vip": {
                "name": "stock_alert_vip",
                "category": "ALERT_UPDATE",
                "language": "pt_BR",
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": "{{customer_name}}"},
                            {"type": "text", "text": "{{product_name}}"},
                            {"type": "text", "text": "{{available_quantity}}"},
                            {"type": "text", "text": "{{price}}"}
                        ]
                    },
                    {
                        "type": "button",
                        "sub_type": "quick_reply",
                        "index": "0",
                        "parameters": [{"type": "payload", "payload": "RESERVE_{{product_id}}"}]
                    },
                    {
                        "type": "button",
                        "sub_type": "quick_reply",
                        "index": "1",
                        "parameters": [{"type": "payload", "payload": "MORE_INFO_{{product_id}}"}]
                    }
                ]
            },
            "new_studio_welcome": {
                "name": "new_studio_welcome",
                "category": "UTILITY",
                "language": "pt_BR",
                "components": [
                    {
                        "type": "header",
                        "parameters": [{"type": "image", "image": {"link": "{{studio_logo}}"}}]
                    },
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": "{{customer_name}}"},
                            {"type": "text", "text": "{{studio_name}}"},
                            {"type": "text", "text": "{{trainer_name}}"},
                            {"type": "text", "text": "{{welcome_offer}}"}
                        ]
                    },
                    {
                        "type": "button",
                        "sub_type": "url",
                        "index": "0",
                        "parameters": [{"type": "text", "text": "{{booking_url}}"}]
                    },
                    {
                        "type": "button",
                        "sub_type": "quick_reply",
                        "index": "1",
                        "parameters": [{"type": "payload", "payload": "SCHEDULE_CLASS"}]
                    }
                ]
            }
        }
    
    def _check_rate_limit(self, instance_id: str) -> bool:
        """Verifica se a instância está dentro do limite de requisições"""
        now = datetime.now()
        
        if instance_id not in self.rate_limits:
            self.rate_limits[instance_id] = RateLimitInfo(
                requests_count=0,
                window_start=now
            )
        
        rate_info = self.rate_limits[instance_id]
        
        # Verifica se está bloqueado
        if rate_info.blocked_until and now < rate_info.blocked_until:
            return False
        
        # Reinicia a janela se necessário
        if now - rate_info.window_start > self.rate_limit_window:
            rate_info.requests_count = 0
            rate_info.window_start = now
            rate_info.blocked_until = None
        
        # Verifica limite
        if rate_info.requests_count >= self.max_requests_per_window:
            rate_info.blocked_until = now + timedelta(minutes=5)
            logger.warning(f"Rate limit excedido para instância {instance_id}")
            return False
        
        rate_info.requests_count += 1
        return True
    
    def _simulate_delay(self):
        """Simula delay realista da API"""
        delay = random.uniform(self.min_delay, self.max_delay)
        time.sleep(delay)
    
    def _should_fail(self) -> bool:
        """Determina se uma requisição deve falhar (5% de chance)"""
        return random.random() < self.failure_rate
    
    def _generate_message_id(self) -> str:
        """Gera ID único para mensagem"""
        return str(uuid.uuid4())
    
    def _save_message(self, message: Message):
        """Salva mensagem para análise"""
        self.messages.append(message)
        
        # Persiste em arquivo
        messages_file = self.persistence_dir / "messages.json"
        try:
            with open(messages_file, 'w', encoding='utf-8') as f:
                json.dump([
                    {
                        **asdict(msg),
                        'timestamp': msg.timestamp.isoformat(),
                        'status': msg.status.value
                    }
                    for msg in self.messages
                ], f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar mensagem: {e}")
    
    async def send_text(self, instance_id: str, recipient: str, message: str, 
                       options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Envia mensagem de texto simples
        
        Args:
            instance_id: ID da instância do WhatsApp
            recipient: Número do destinatário
            message: Conteúdo da mensagem
            options: Opções adicionais
            
        Returns:
            Dict com resultado da operação
        """
        logger.info(f"Enviando texto para {recipient}: {message[:50]}...")
        
        # Verifica rate limit
        if not self._check_rate_limit(instance_id):
            return {
                "success": False,
                "error": "Rate limit excedido. Tente novamente em 5 minutos.",
                "error_code": "RATE_LIMIT_EXCEEDED"
            }
        
        # Simula delay
        await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
        
        # Simula falha ocasional
        if self._should_fail():
            error_msg = random.choice([
                "Erro de conexão com WhatsApp",
                "Número de telefone inválido",
                "Mensagem bloqueada por spam"
            ])
            
            msg = Message(
                id=self._generate_message_id(),
                instance_id=instance_id,
                recipient=recipient,
                content=message,
                message_type="text",
                status=MessageStatus.FAILED,
                timestamp=datetime.now(),
                error_message=error_msg
            )
            self._save_message(msg)
            
            return {
                "success": False,
                "error": error_msg,
                "error_code": "MESSAGE_FAILED",
                "message_id": msg.id
            }
        
        # Sucesso
        msg = Message(
            id=self._generate_message_id(),
            instance_id=instance_id,
            recipient=recipient,
            content=message,
            message_type="text",
            status=MessageStatus.SENT,
            timestamp=datetime.now()
        )
        self._save_message(msg)
        
        return {
            "success": True,
            "message_id": msg.id,
            "status": "sent",
            "timestamp": msg.timestamp.isoformat()
        }
    
    async def send_template(self, instance_id: str, recipient: str, 
                           template_name: str, template_params: Dict[str, Any],
                           options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Envia mensagem de template
        
        Args:
            instance_id: ID da instância do WhatsApp
            recipient: Número do destinatário
            template_name: Nome do template
            template_params: Parâmetros do template
            options: Opções adicionais
            
        Returns:
            Dict com resultado da operação
        """
        logger.info(f"Enviando template '{template_name}' para {recipient}")
        
        # Verifica se o template existe
        if template_name not in self.templates:
            return {
                "success": False,
                "error": f"Template '{template_name}' não encontrado",
                "error_code": "TEMPLATE_NOT_FOUND"
            }
        
        # Verifica rate limit
        if not self._check_rate_limit(instance_id):
            return {
                "success": False,
                "error": "Rate limit excedido. Tente novamente em 5 minutos.",
                "error_code": "RATE_LIMIT_EXCEEDED"
            }
        
        # Simula delay
        await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
        
        # Simula falha ocasional
        if self._should_fail():
            error_msg = random.choice([
                "Erro ao processar template",
                "Parâmetros inválidos para template",
                "Template não aprovado"
            ])
            
            msg = Message(
                id=self._generate_message_id(),
                instance_id=instance_id,
                recipient=recipient,
                content=f"Template: {template_name}",
                message_type="template",
                status=MessageStatus.FAILED,
                timestamp=datetime.now(),
                template_name=template_name,
                template_params=template_params,
                error_message=error_msg
            )
            self._save_message(msg)
            
            return {
                "success": False,
                "error": error_msg,
                "error_code": "TEMPLATE_FAILED",
                "message_id": msg.id
            }
        
        # Valida parâmetros do template
        template = self.templates[template_name]
        validation_result = self._validate_template_params(template, template_params)
        if not validation_result["valid"]:
            return {
                "success": False,
                "error": validation_result["error"],
                "error_code": "INVALID_TEMPLATE_PARAMS"
            }
        
        # Sucesso
        msg = Message(
            id=self._generate_message_id(),
            instance_id=instance_id,
            recipient=recipient,
            content=f"Template: {template_name}",
            message_type="template",
            status=MessageStatus.SENT,
            timestamp=datetime.now(),
            template_name=template_name,
            template_params=template_params
        )
        self._save_message(msg)
        
        return {
            "success": True,
            "message_id": msg.id,
            "status": "sent",
            "template_name": template_name,
            "timestamp": msg.timestamp.isoformat()
        }
    
    def _validate_template_params(self, template: Dict, params: Dict) -> Dict[str, Any]:
        """Valida parâmetros do template"""
        try:
            # Verifica parâmetros obrigatórios com base no template
            required_params = set()
            for component in template.get("components", []):
                if component["type"] == "body":
                    for param in component.get("parameters", []):
                        if "text" in str(param):
                            required_params.add(param.get("text", ""))
            
            missing_params = required_params - set(params.keys())
            if missing_params:
                return {
                    "valid": False,
                    "error": f"Parâmetros faltando: {', '.join(missing_params)}"
                }
            
            return {"valid": True}
        except Exception as e:
            return {
                "valid": False,
                "error": f"Erro na validação: {str(e)}"
            }
    
    def get_instance_status(self, instance_id: str) -> Dict[str, Any]:
        """
        Obtém status da instância
        
        Args:
            instance_id: ID da instância
            
        Returns:
            Dict com status da instância
        """
        logger.info(f"Obtendo status da instância {instance_id}")
        
        # Simula mudanças de status ocasionais
        if instance_id not in self.instances:
            # Nova instância - 70% chance de estar conectada
            self.instances[instance_id] = InstanceStatus.CONNECTED if random.random() < 0.7 else InstanceStatus.DISCONNECTED
        else:
            # 10% chance de mudar de status
            if random.random() < 0.1:
                current_status = self.instances[instance_id]
                if current_status == InstanceStatus.CONNECTED:
                    self.instances[instance_id] = random.choice([
                        InstanceStatus.DISCONNECTED,
                        InstanceStatus.CONNECTING,
                        InstanceStatus.AUTHENTICATION_FAILURE
                    ])
                else:
                    self.instances[instance_id] = InstanceStatus.CONNECTED
        
        status = self.instances[instance_id]
        
        # Informações adicionais baseadas no status
        if status == InstanceStatus.CONNECTED:
            return {
                "success": True,
                "instance_id": instance_id,
                "status": "connected",
                "connected": True,
                "qrcode": None,
                "timestamp": datetime.now().isoformat()
            }
        elif status == InstanceStatus.DISCONNECTED:
            return {
                "success": True,
                "instance_id": instance_id,
                "status": "disconnected",
                "connected": False,
                "qrcode": f"https://example.com/qrcode/{instance_id}",
                "timestamp": datetime.now().isoformat()
            }
        elif status == InstanceStatus.CONNECTING:
            return {
                "success": True,
                "instance_id": instance_id,
                "status": "connecting",
                "connected": False,
                "qrcode": f"https://example.com/qrcode/{instance_id}",
                "timestamp": datetime.now().isoformat()
            }
        else:  # AUTHENTICATION_FAILURE
            return {
                "success": False,
                "instance_id": instance_id,
                "status": "authentication_failure",
                "connected": False,
                "error": "Falha na autenticação. Escaneie o QR code novamente.",
                "qrcode": f"https://example.com/qrcode/{instance_id}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def simulate_incoming_message(self, instance_id: str, sender: str, 
                                       message: str, message_type: str = "text") -> Dict[str, Any]:
        """
        Simula mensagem recebida (para testes)
        
        Args:
            instance_id: ID da instância
            sender: Número do remetente
            message: Conteúdo da mensagem
            message_type: Tipo da mensagem
            
        Returns:
            Dict com confirmação
        """
        logger.info(f"Simulando mensagem recebida de {sender}: {message[:50]}...")
        
        # Simula delay
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Cria mensagem recebida
        msg = Message(
            id=self._generate_message_id(),
            instance_id=instance_id,
            recipient=instance_id,  # Invertido - é uma mensagem recebida
            content=message,
            message_type=message_type,
            status=MessageStatus.DELIVERED,
            timestamp=datetime.now()
        )
        self._save_message(msg)
        
        return {
            "success": True,
            "message_id": msg.id,
            "simulated": True,
            "timestamp": msg.timestamp.isoformat()
        }
    
    def get_message_history(self, instance_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtém histórico de mensagens da instância
        
        Args:
            instance_id: ID da instância
            limit: Limite de mensagens
            
        Returns:
            Lista de mensagens
        """
        instance_messages = [
            msg for msg in self.messages 
            if msg.instance_id == instance_id
        ]
        
        # Ordena por timestamp (mais recente primeiro)
        instance_messages.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Limita resultado
        instance_messages = instance_messages[:limit]
        
        return [
            {
                "id": msg.id,
                "recipient": msg.recipient,
                "content": msg.content,
                "message_type": msg.message_type,
                "status": msg.status.value,
                "timestamp": msg.timestamp.isoformat(),
                "template_name": msg.template_name,
                "template_params": msg.template_params,
                "error_message": msg.error_message
            }
            for msg in instance_messages
        ]
    
    def get_templates(self) -> Dict[str, Any]:
        """
        Obtém todos os templates disponíveis
        
        Returns:
            Dict com templates
        """
        return {
            "success": True,
            "templates": self.templates,
            "count": len(self.templates)
        }
    
    def get_template(self, template_name: str) -> Dict[str, Any]:
        """
        Obtém template específico
        
        Args:
            template_name: Nome do template
            
        Returns:
            Dict com template ou erro
        """
        if template_name not in self.templates:
            return {
                "success": False,
                "error": f"Template '{template_name}' não encontrado",
                "error_code": "TEMPLATE_NOT_FOUND"
            }
        
        return {
            "success": True,
            "template": self.templates[template_name]
        }
    
    def get_stats(self, instance_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtém estatísticas de uso
        
        Args:
            instance_id: ID da instância (opcional)
            
        Returns:
            Dict com estatísticas
        """
        if instance_id:
            instance_messages = [
                msg for msg in self.messages 
                if msg.instance_id == instance_id
            ]
        else:
            instance_messages = self.messages
        
        total_messages = len(instance_messages)
        sent_messages = len([msg for msg in instance_messages if msg.status == MessageStatus.SENT])
        delivered_messages = len([msg for msg in instance_messages if msg.status == MessageStatus.DELIVERED])
        failed_messages = len([msg for msg in instance_messages if msg.status == MessageStatus.FAILED])
        
        template_messages = len([msg for msg in instance_messages if msg.message_type == "template"])
        text_messages = len([msg for msg in instance_messages if msg.message_type == "text"])
        
        return {
            "success": True,
            "instance_id": instance_id,
            "total_messages": total_messages,
            "sent_messages": sent_messages,
            "delivered_messages": delivered_messages,
            "failed_messages": failed_messages,
            "template_messages": template_messages,
            "text_messages": text_messages,
            "success_rate": (sent_messages + delivered_messages) / total_messages if total_messages > 0 else 0,
            "failure_rate": failed_messages / total_messages if total_messages > 0 else 0
        }
    
    def reset_instance(self, instance_id: str) -> Dict[str, Any]:
        """
        Reseta estado da instância
        
        Args:
            instance_id: ID da instância
            
        Returns:
            Dict com confirmação
        """
        logger.info(f"Resetando instância {instance_id}")
        
        # Remove estado da instância
        if instance_id in self.instances:
            del self.instances[instance_id]
        
        # Remove rate limit
        if instance_id in self.rate_limits:
            del self.rate_limits[instance_id]
        
        # Remove mensagens da instância
        self.messages = [
            msg for msg in self.messages 
            if msg.instance_id != instance_id
        ]
        
        return {
            "success": True,
            "instance_id": instance_id,
            "message": "Instância resetada com sucesso"
        }
    
    def clear_all_data(self) -> Dict[str, Any]:
        """
        Limpa todos os dados do mock (para testes)
        
        Returns:
            Dict com confirmação
        """
        logger.warning("Limpando todos os dados do EvolutionMock")
        
        self.instances.clear()
        self.messages.clear()
        self.rate_limits.clear()
        
        return {
            "success": True,
            "message": "Todos os dados foram limpos"
        }


# Funções utilitárias para facilitar uso
async def create_evolution_mock(config: Optional[Dict] = None) -> EvolutionMock:
    """
    Factory function para criar instância do EvolutionMock
    
    Args:
        config: Configuração opcional
        
    Returns:
        Instância do EvolutionMock
    """
    return EvolutionMock(config)

async def test_evolution_mock():
    """
    Função de teste para verificar funcionamento do mock
    """
    print("🧪 Iniciando testes do EvolutionMock...")
    
    # Cria instância
    mock = await create_evolution_mock()
    
    # Testa status da instância
    print("📱 Testando status da instância...")
    status = mock.get_instance_status("test_instance")
    print(f"Status: {status['status']}")
    
    # Testa envio de texto
    print("💬 Testando envio de mensagem de texto...")
    result = await mock.send_text(
        "test_instance", 
        "5511999999999", 
        "Olá! Esta é uma mensagem de teste do EvolutionMock."
    )
    print(f"Resultado texto: {'✅ Sucesso' if result['success'] else '❌ Falha'}")
    
    # Testa envio de template
    print("📋 Testando envio de template...")
    result = await mock.send_template(
        "test_instance",
        "5511999999999",
        "abandoned_cart_v1",
        {
            "customer_name": "João",
            "product_name": "Tênis Esportivo",
            "discount_percentage": "20%",
            "discount_code": "DESCONTO20",
            "validity_hours": "24",
            "checkout_url": "checkout123",
            "header_image": "https://example.com/image.jpg"
        }
    )
    print(f"Resultado template: {'✅ Sucesso' if result['success'] else '❌ Falha'}")
    
    # Testa simulação de mensagem recebida
    print("📨 Testando mensagem recebida...")
    result = await mock.simulate_incoming_message(
        "test_instance",
        "5511999999999",
        "Olá, gostaria de mais informações sobre os produtos."
    )
    print(f"Mensagem recebida: {'✅ Simulada' if result['success'] else '❌ Falha'}")
    
    # Testa histórico
    print("📊 Testando histórico de mensagens...")
    history = mock.get_message_history("test_instance", limit=10)
    print(f"Mensagens no histórico: {len(history)}")
    
    # Testa estatísticas
    print("📈 Testando estatísticas...")
    stats = mock.get_stats("test_instance")
    print(f"Taxa de sucesso: {stats['success_rate']:.1%}")
    
    print("✅ Testes concluídos!")


if __name__ == "__main__":
    # Executa testes se rodar diretamente
    asyncio.run(test_evolution_mock())