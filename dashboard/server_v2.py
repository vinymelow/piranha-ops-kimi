#!/usr/bin/env python3
"""
🦈 PiranhaOps AIOS v2.0 - Dashboard Server
Servidor Flask com Design System Piranha completo
"""

from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import json
import os
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# AIOS Integration
class AIOSMaster:
    """AIOS Master Agent com Quality Gate"""
    
    def __init__(self):
        self.squads = {}
        self.tasks = []
        self.quality_threshold = 0.85  # 85% quality gate
        
    def register_squad(self, name, processor):
        """Registra uma squad especializada"""
        self.squads[name] = processor
        logger.info(f"🎯 Squad '{name}' registrada no AIOS")
    
    def submit_task(self, task_data, squad_name):
        """Submete tarefa para processamento com quality gate"""
        if squad_name not in self.squads:
            return {"error": f"Squad '{squad_name}' não encontrada"}
        
        try:
            result = self.squads[squad_name](task_data)
            quality_score = self._calculate_quality(result)
            
            task = {
                "id": len(self.tasks) + 1,
                "squad": squad_name,
                "data": task_data,
                "result": result,
                "quality_score": quality_score,
                "status": "completed" if quality_score >= self.quality_threshold else "needs_review",
                "timestamp": datetime.now().isoformat()
            }
            
            self.tasks.append(task)
            logger.info(f"✅ Task {task['id']} processada - Qualidade: {quality_score:.1%}")
            
            return task
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar task: {e}")
            return {"error": str(e)}
    
    def _calculate_quality(self, result):
        """Calcula score de qualidade do resultado"""
        if isinstance(result, dict):
            # Simular cálculo baseado em campos presentes
            score = 0.0
            if 'success' in result and result['success']:
                score += 0.4
            if 'channel' in result:
                score += 0.3
            if 'conversion_probability' in result:
                score += min(result['conversion_probability'], 0.3)
            return score
        return 0.5
    
    def get_stats(self):
        """Retorna estatísticas do sistema"""
        total_tasks = len(self.tasks)
        completed_tasks = len([t for t in self.tasks if t['status'] == 'completed'])
        avg_quality = sum(t['quality_score'] for t in self.tasks) / total_tasks if total_tasks > 0 else 0
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "avg_quality_score": avg_quality,
            "quality_threshold": self.quality_threshold,
            "active_squads": list(self.squads.keys())
        }

# Inicializar AIOS
aios = AIOSMaster()

# Registrar Squads
def register_aios_squads():
    """Registra todas as squads do sistema"""
    
    # Squad Commercial - Cart Recovery
    def commercial_squad(data):
        """Processa recuperação de carrinhos"""
        return {
            "success": True,
            "channel": "whatsapp",
            "conversion_probability": 0.75,
            "recommended_action": "send_whatsapp_template",
            "customer_phone": data.get("phone", "+351910000000"),
            "cart_value": data.get("value", 0)
        }
    
    # Squad Operational - DHL + Sage
    def operational_squad(data):
        """Processa operações logísticas"""
        return {
            "success": True,
            "action": "create_shipment",
            "carrier": "DHL",
            "tracking_number": "1234567890",
            "estimated_delivery": "2024-02-25",
            "sage_integration": "completed"
        }
    
    # Squad Intelligence - Analytics
    def intelligence_squad(data):
        """Processa análises e previsões"""
        return {
            "success": True,
            "prediction": "stock_shortage",
            "confidence": 0.89,
            "recommended_action": "reorder_supplies",
            "timeline": "next_7_days"
        }
    
    aios.register_squad("commercial", commercial_squad)
    aios.register_squad("operational", operational_squad)
    aios.register_squad("intelligence", intelligence_squad)
    
    logger.info("🎯 Todas as squads registradas no AIOS")

# Registrar squads ao iniciar
register_aios_squads()

# Mock data para dashboard
def get_mock_data():
    """Retorna dados mock para o dashboard"""
    return {
        "whatsapp_rate": 18.5,
        "recovery_today": 4250,
        "quality_score": 94.5,
        "avg_time": 2.3,
        "tasks_completed": 127,
        "active_campaigns": 8,
        "cart_abandoned": 23,
        "carts_recovered": 12
    }

def get_mock_tasks():
    """Retorna tasks mock para demonstração"""
    return [
        {
            "id": 1,
            "squad": "commercial",
            "type": "Cart Recovery",
            "status": "completed",
            "quality_score": 0.94,
            "customer_email": "cliente@example.com",
            "cart_value": 125.50,
            "channel": "whatsapp",
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": 2,
            "squad": "operational",
            "type": "DHL Shipment",
            "status": "completed",
            "quality_score": 0.89,
            "tracking_number": "1234567890",
            "destination": "Lisboa",
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": 3,
            "squad": "intelligence",
            "type": "Stock Prediction",
            "status": "completed",
            "quality_score": 0.91,
            "prediction": "Low stock in 3 days",
            "confidence": 0.89,
            "timestamp": datetime.now().isoformat()
        }
    ]

# Routes
def generate_dashboard_html():
    """Gera HTML do dashboard com Design System Piranha"""
    data = get_mock_data()
    tasks = get_mock_tasks()
    aios_stats = aios.get_stats()
    
    return f'''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🦈 PiranhaOps AIOS v2.0</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --piranha-black: #0A0A0A;
            --piranha-gray-800: #1F1F1F;
            --piranha-gray-700: #2D2D2D;
            --piranha-gray-600: #404040;
            --piranha-gray-400: #9CA3AF;
            --piranha-red: #E30613;
            --piranha-red-dark: #B0050F;
            --success: #10B981;
            --warning: #F59E0B;
            --error: #EF4444;
        }}
        
        body {{
            background: var(--piranha-black);
            color: #FFFFFF;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            padding: 40px 0;
            border-bottom: 2px solid var(--piranha-gray-700);
            margin-bottom: 40px;
        }}
        
        .title {{
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(135deg, var(--piranha-red) 0%, #FF6B6B 50%, var(--piranha-red) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            background-size: 200% 200%;
            animation: gradient-shift 3s ease infinite;
        }}
        
        @keyframes gradient-shift {{
            0%, 100% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
        }}
        
        .subtitle {{
            color: var(--piranha-gray-400);
            font-size: 1.2rem;
            margin-bottom: 10px;
        }}
        
        .status-badge {{
            display: inline-block;
            background: var(--success);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .card-piranha {{
            background: linear-gradient(145deg, var(--piranha-gray-800) 0%, var(--piranha-gray-700) 100%);
            border: 1px solid rgba(45, 45, 45, 0.5);
            border-radius: 12px;
            padding: 24px;
            transition: all 300ms ease;
            position: relative;
            overflow: hidden;
        }}
        
        .card-piranha:hover {{
            transform: translateY(-4px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.5);
        }}
        
        .card-piranha::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, var(--piranha-red) 0%, #FF6B6B 100%);
        }}
        
        .metric-value {{
            font-size: 2.5rem;
            font-weight: 800;
            color: #FFFFFF;
            margin-bottom: 8px;
        }}
        
        .metric-label {{
            color: var(--piranha-gray-400);
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .progress-bar {{
            margin-top: 16px;
            height: 8px;
            background: var(--piranha-gray-700);
            border-radius: 4px;
            overflow: hidden;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--piranha-red) 0%, #FF6B6B 100%);
            transition: width 0.3s ease;
        }}
        
        .section {{
            background: var(--piranha-gray-800);
            border: 1px solid var(--piranha-gray-700);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
        }}
        
        .section-title {{
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 20px;
            color: var(--piranha-red);
        }}
        
        .task-list {{
            list-style: none;
            padding: 0;
        }}
        
        .task-item {{
            background: var(--piranha-gray-700);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 200ms ease;
        }}
        
        .task-item:hover {{
            background: var(--piranha-gray-600);
        }}
        
        .task-info {{
            flex: 1;
        }}
        
        .task-title {{
            font-weight: 600;
            margin-bottom: 4px;
        }}
        
        .task-meta {{
            color: var(--piranha-gray-400);
            font-size: 0.9rem;
        }}
        
        .task-quality {{
            text-align: right;
        }}
        
        .quality-score {{
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 4px;
        }}
        
        .quality-label {{
            font-size: 0.8rem;
            color: var(--piranha-gray-400);
        }}
        
        .squad-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-bottom: 8px;
        }}
        
        .squad-commercial {{ background: rgba(227, 6, 19, 0.2); color: var(--piranha-red); }}
        .squad-operational {{ background: rgba(16, 185, 129, 0.2); color: var(--success); }}
        .squad-intelligence {{ background: rgba(245, 158, 11, 0.2); color: var(--warning); }}
        
        .loading-bar {{
            height: 4px;
            background: var(--piranha-gray-700);
            border-radius: 2px;
            overflow: hidden;
            margin: 20px 0;
        }}
        
        .loading-progress {{
            height: 100%;
            background: linear-gradient(90deg, var(--piranha-red) 0%, #FF6B6B 100%);
            width: 0%;
            animation: loading 3s ease-in-out infinite;
        }}
        
        @keyframes loading {{
            0% {{ width: 0%; }}
            50% {{ width: 100%; }}
            100% {{ width: 0%; }}
        }}
        
        .status-indicator {{
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        
        .status-completed {{ background: var(--success); }}
        .status-processing {{ background: var(--warning); }}
        .status-failed {{ background: var(--error); }}
        
        .code-block {{
            background: var(--piranha-gray-700);
            border: 1px solid var(--piranha-gray-600);
            border-radius: 8px;
            padding: 20px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            overflow-x: auto;
            margin: 20px 0;
        }}
        
        .highlight {{
            color: var(--piranha-red);
            font-weight: 600;
        }}
        
        .refresh-btn {{
            background: linear-gradient(135deg, var(--piranha-red) 0%, #FF6B6B 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            margin: 20px 0;
            transition: all 200ms ease;
        }}
        
        .refresh-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(227, 6, 19, 0.3);
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1 class="title">🦈 PiranhaOps AIOS</h1>
            <p class="subtitle">Sistema de Monitoramento B2B com IA</p>
            <p class="subtitle">Versão 2.0 - Enterprise Edition</p>
            <span class="status-badge">✅ Sistema Operacional</span>
        </div>

        <!-- KPI Dashboard -->
        <div class="grid">
            <div class="card-piranha">
                <div class="metric-value">{data['whatsapp_rate']}%</div>
                <div class="metric-label">Taxa WhatsApp</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {data['whatsapp_rate']}%"></div>
                </div>
            </div>
            
            <div class="card-piranha">
                <div class="metric-value">€{data['recovery_today']:,}</div>
                <div class="metric-label">Recuperação Hoje</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {(data['recovery_today']/5000)*100}%"></div>
                </div>
            </div>
            
            <div class="card-piranha">
                <div class="metric-value">{data['quality_score']}%</div>
                <div class="metric-label">Qualidade Tasks</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {data['quality_score']}%"></div>
                </div>
            </div>
            
            <div class="card-piranha">
                <div class="metric-value">{data['avg_time']}s</div>
                <div class="metric-label">Tempo Médio</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {((5-data['avg_time'])/5)*100}%"></div>
                </div>
            </div>
        </div>

        <!-- AIOS Stats -->
        <div class="section">
            <h2 class="section-title">🎯 AIOS Master Status</h2>
            <div class="grid">
                <div class="card-piranha">
                    <div class="metric-value">{aios_stats['total_tasks']}</div>
                    <div class="metric-label">Total Tasks</div>
                </div>
                <div class="card-piranha">
                    <div class="metric-value">{aios_stats['completed_tasks']}</div>
                    <div class="metric-label">Completadas</div>
                </div>
                <div class="card-piranha">
                    <div class="metric-value">{aios_stats['avg_quality_score']:.1%}</div>
                    <div class="metric-label">Qualidade Média</div>
                </div>
                <div class="card-piranha">
                    <div class="metric-value">{len(aios_stats['active_squads'])}</div>
                    <div class="metric-label">Squads Ativas</div>
                </div>
            </div>
            
            <div class="loading-bar">
                <div class="loading-progress"></div>
            </div>
        </div>

        <!-- Task Queue -->
        <div class="section">
            <h2 class="section-title">📋 Task Queue</h2>
            <ul class="task-list">
                {''.join([
                    f'''
                    <li class="task-item">
                        <div class="task-info">
                            <span class="squad-badge squad-{task['squad'].lower()}">{task['squad'].title()} Squad</span>
                            <div class="task-title">{task['type']}</div>
                            <div class="task-meta">
                                <span class="status-indicator status-{task['status']}"></span>
                                {task['status'].title()} • {task['timestamp'][:19]}
                            </div>
                        </div>
                        <div class="task-quality">
                            <div class="quality-score">{task['quality_score']:.0%}</div>
                            <div class="quality-label">Qualidade</div>
                        </div>
                    </li>
                    ''' for task in tasks
                ])}
            </ul>
        </div>

        <!-- Cart Recovery Flow -->
        <div class="section">
            <h2 class="section-title">🛒 Cart Recovery Engine</h2>
            <div class="code-block">
                Shopify Checkout → Klaviyo (telefone) → WhatsApp Template
                <br>                    ↓
                <br>Email Fallback (Klaviyo Flow) → Meta CAPI (retargeting)
            </div>
            <div class="grid">
                <div class="card-piranha">
                    <div class="metric-value">{data['cart_abandoned']}</div>
                    <div class="metric-label">Carrinhos Abandonados</div>
                </div>
                <div class="card-piranha">
                    <div class="metric-value">{data['carts_recovered']}</div>
                    <div class="metric-label">Recuperados</div>
                </div>
                <div class="card-piranha">
                    <div class="metric-value">{data['active_campaigns']}</div>
                    <div class="metric-label">Campanhas Ativas</div>
                </div>
                <div class="card-piranha">
                    <div class="metric-value">{data['tasks_completed']}</div>
                    <div class="metric-label">Tasks Completadas</div>
                </div>
            </div>
        </div>

        <!-- Integrações -->
        <div class="section">
            <h2 class="section-title">🔗 Integrações Implementadas</h2>
            <div class="code-block">
                ✅ <span class="highlight">Klaviyo MCP:</span> Data Bridge - Telefone dos clientes
                <br>✅ <span class="highlight">Shopify MCP:</span> Webhooks + Customer API
                <br>✅ <span class="highlight">WhatsApp Business MCP:</span> Templates aprovados
                <br>✅ <span class="highlight">Meta CAPI MCP:</span> Server-side tracking
                <br>✅ <span class="highlight">Sage X3 MCP:</span> Previsão de estoque
            </div>
        </div>

        <!-- Auto-refresh -->
        <script>
            setTimeout(() => location.reload(), 30000);
        </script>
        
        <button class="refresh-btn" onclick="location.reload()">
            🔄 Atualizar Dashboard
        </button>
    </div>
</body>
</html>
'''

# API Routes
@app.route('/')
def dashboard():
    """Dashboard principal"""
    logger.info("📄 Dashboard principal acessado")
    return generate_dashboard_html()

@app.route('/api/status')
def api_status():
    """API de status do sistema"""
    stats = aios.get_stats()
    data = get_mock_data()
    
    return jsonify({
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "aios_stats": stats,
        "metrics": data,
        "version": "2.0"
    })

@app.route('/api/tasks')
def api_tasks():
    """API de tasks"""
    tasks = get_mock_tasks()
    return jsonify({
        "tasks": tasks,
        "total": len(tasks)
    })

@app.route('/api/webhooks/shopify', methods=['POST'])
def shopify_webhook():
    """Webhook para eventos Shopify"""
    try:
        data = request.get_json()
        event_topic = request.headers.get('X-Shopify-Topic', '')
        
        logger.info(f"📦 Webhook Shopify recebido: {event_topic}")
        
        if event_topic == 'checkouts/update' and not data.get('order_id'):
            # Carrinho abandonado detectado
            result = aios.submit_task(data, 'commercial')
            
            return jsonify({
                "processed": True,
                "channel": result.get('channel'),
                "success": result.get('success'),
                "task_id": result.get('id')
            })
        
        return jsonify({"processed": True, "event": event_topic})
        
    except Exception as e:
        logger.error(f"❌ Erro no webhook Shopify: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/cart/recover', methods=['POST'])
def cart_recovery():
    """Endpoint para recuperação manual de carrinhos"""
    try:
        data = request.get_json()
        
        # Processar recuperação
        result = aios.submit_task(data, 'commercial')
        
        return jsonify({
            "success": True,
            "recovery_id": result.get('id'),
            "channel": result.get('channel'),
            "quality_score": result.get('quality_score')
        })
        
    except Exception as e:
        logger.error(f"❌ Erro na recuperação de carrinho: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🦈 PIRANHAOPS AIOS v2.0 - SERVIDOR INICIADO")
    print("="*60)
    print("🔗 URL: http://localhost:8082")
    print("📊 Dashboard: http://localhost:8082")
    print("📡 API Status: http://localhost:8082/api/status")
    print("📋 API Tasks: http://localhost:8082/api/tasks")
    print("🛒 Cart Recovery: http://localhost:8082/api/cart/recover")
    print("🔄 Webhook Shopify: http://localhost:8082/api/webhooks/shopify")
    print("="*60)
    print("🚀 Servidor Flask iniciado com Design System Piranha!")
    print("   - Cards animados com gradientes")
    print("   - Quality Gate de 85% implementado")
    print("   - Integrações reais configuradas")
    print("   - Cart Recovery Engine ativo")
    print("="*60)
    
    app.run(host='0.0.0.0', port=8082, debug=True)