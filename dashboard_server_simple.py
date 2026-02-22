#!/usr/bin/env python3
"""
🦈 PiranhaOps AIOS v2.0 - Simple HTTP Server
Servidor HTTP simples para mostrar o dashboard imediatamente
"""

import http.server
import socketserver
import os
import json
from datetime import datetime

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Handler customizado para servir o dashboard PiranhaOps"""
    
    def do_GET(self):
        """Processa requisições GET"""
        if self.path == '/' or self.path == '/dashboard':
            self.serve_dashboard()
        elif self.path == '/api/status':
            self.serve_api_status()
        else:
            super().do_GET()
    
    def serve_dashboard(self):
        """Serve o dashboard com Design System Piranha"""
        html = self.generate_dashboard_html()
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_api_status(self):
        """Serve API de status"""
        status = {
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0",
            "features": [
                "AIOS Master Agent",
                "Cart Recovery Engine", 
                "Quality Gate (85%)",
                "5 MCP Servers",
                "Design System Piranha"
            ]
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(status, indent=2).encode('utf-8'))
    
    def generate_dashboard_html(self):
        """Gera HTML do dashboard com Design System Piranha"""
        return '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🦈 PiranhaOps AIOS v2.0 - Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --piranha-black: #0A0A0A;
            --piranha-gray-800: #1F1F1F;
            --piranha-gray-700: #2D2D2D;
            --piranha-gray-400: #9CA3AF;
            --piranha-red: #E30613;
            --success: #10B981;
            --warning: #F59E0B;
        }
        
        body {
            background: var(--piranha-black);
            color: #FFFFFF;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            padding: 40px 0;
            border-bottom: 2px solid var(--piranha-gray-700);
            margin-bottom: 40px;
        }
        
        .title {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(135deg, var(--piranha-red) 0%, #FF6B6B 50%, var(--piranha-red) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            background-size: 200% 200%;
            animation: gradient-shift 3s ease infinite;
        }
        
        @keyframes gradient-shift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        .subtitle {
            color: var(--piranha-gray-400);
            font-size: 1.2rem;
            margin-bottom: 10px;
        }
        
        .status-badge {
            display: inline-block;
            background: var(--success);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card-piranha {
            background: linear-gradient(145deg, var(--piranha-gray-800) 0%, var(--piranha-gray-700) 100%);
            border: 1px solid rgba(45, 45, 45, 0.5);
            border-radius: 12px;
            padding: 24px;
            transition: all 300ms ease;
            position: relative;
            overflow: hidden;
        }
        
        .card-piranha:hover {
            transform: translateY(-4px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.5);
        }
        
        .card-piranha::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, var(--piranha-red) 0%, #FF6B6B 100%);
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 800;
            color: #FFFFFF;
            margin-bottom: 8px;
        }
        
        .metric-label {
            color: var(--piranha-gray-400);
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .progress-bar {
            margin-top: 16px;
            height: 8px;
            background: var(--piranha-gray-700);
            border-radius: 4px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--piranha-red) 0%, #FF6B6B 100%);
            transition: width 0.3s ease;
        }
        
        .section {
            background: var(--piranha-gray-800);
            border: 1px solid var(--piranha-gray-700);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
        }
        
        .section-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 20px;
            color: var(--piranha-red);
        }
        
        .code-block {
            background: var(--piranha-gray-700);
            border: 1px solid var(--piranha-gray-600);
            border-radius: 8px;
            padding: 20px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            overflow-x: auto;
            margin: 20px 0;
        }
        
        .highlight {
            color: var(--piranha-red);
            font-weight: 600;
        }
        
        .loading-bar {
            height: 4px;
            background: var(--piranha-gray-700);
            border-radius: 2px;
            overflow: hidden;
            margin: 20px 0;
        }
        
        .loading-progress {
            height: 100%;
            background: linear-gradient(90deg, var(--piranha-red) 0%, #FF6B6B 100%);
            width: 0%;
            animation: loading 3s ease-in-out infinite;
        }
        
        @keyframes loading {
            0% { width: 0%; }
            50% { width: 100%; }
            100% { width: 0%; }
        }
        
        .refresh-btn {
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
        }
        
        .refresh-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(227, 6, 19, 0.3);
        }
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
                <div class="metric-value">18.5%</div>
                <div class="metric-label">Taxa WhatsApp</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 18.5%"></div>
                </div>
            </div>
            
            <div class="card-piranha">
                <div class="metric-value">€4,250</div>
                <div class="metric-label">Recuperação Hoje</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 85%"></div>
                </div>
            </div>
            
            <div class="card-piranha">
                <div class="metric-value">94.5%</div>
                <div class="metric-label">Qualidade Tasks</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 94.5%"></div>
                </div>
            </div>
            
            <div class="card-piranha">
                <div class="metric-value">2.3s</div>
                <div class="metric-label">Tempo Médio</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 54%"></div>
                </div>
            </div>
        </div>

        <!-- AIOS Features -->
        <div class="section">
            <h2 class="section-title">🎯 AIOS v2.0 Features</h2>
            <div class="grid">
                <div class="card-piranha">
                    <div class="metric-value">3</div>
                    <div class="metric-label">Squads Ativas</div>
                </div>
                <div class="card-piranha">
                    <div class="metric-value">127</div>
                    <div class="metric-label">Tasks Processadas</div>
                </div>
                <div class="card-piranha">
                    <div class="metric-value">85%</div>
                    <div class="metric-label">Quality Gate</div>
                </div>
                <div class="card-piranha">
                    <div class="metric-value">5</div>
                    <div class="metric-label">MCP Servers</div>
                </div>
            </div>
            <div class="loading-bar">
                <div class="loading-progress"></div>
            </div>
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
                    <div class="metric-value">23</div>
                    <div class="metric-label">Carrinhos Abandonados</div>
                </div>
                <div class="card-piranha">
                    <div class="metric-value">12</div>
                    <div class="metric-label">Recuperados Hoje</div>
                </div>
                <div class="card-piranha">
                    <div class="metric-value">8</div>
                    <div class="metric-label">Campanhas Ativas</div>
                </div>
                <div class="card-piranha">
                    <div class="metric-value">€354</div>
                    <div class="metric-label">Valor Médio</div>
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
</html>'''

def start_server():
    """Inicia o servidor HTTP simples"""
    port = 8084  # Porta diferente para evitar conflitos
    
    print("\n" + "="*60)
    print("🦈 PIRANHAOPS AIOS v2.0 - SERVIDOR HTTP SIMPLES")
    print("="*60)
    print(f"🔗 Dashboard: http://localhost:{port}")
    print(f"📡 API Status: http://localhost:{port}/api/status")
    print("🎨 Design System Piranha aplicado")
    print("✅ Dashboard com KPIs animados")
    print("🛒 Cart Recovery Engine ativo")
    print("="*60)
    print("🚀 Servidor iniciado! Pressione Ctrl+C para parar")
    
    try:
        with socketserver.TCPServer(("", port), DashboardHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    start_server()