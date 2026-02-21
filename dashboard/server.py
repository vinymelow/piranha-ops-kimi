"""
Dashboard Web PiranhaOps - Versão Corrigida
Servidor simples para visualizar alertas e métricas
"""

import json
import http.server
import socketserver
import threading
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import logging

logger = logging.getLogger(__name__)

# Importar data store
import sys
import os
sys.path.append(str(Path(__file__).parent.parent))
from core.data_store import DataStore

PORT = 8080

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Handler do dashboard"""
    
    def __init__(self, *args, **kwargs):
        self.store = DataStore()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Processa requisições GET"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        logger.info(f"📡 Requisição GET: {path}")
        
        if path == '/':
            self._serve_dashboard()
        elif path == '/api/status':
            self._serve_api_status()
        elif path == '/api/alerts':
            self._serve_api_alerts()
        elif path == '/api/baseline':
            self._serve_api_baseline()
        elif path == '/api/trends':
            self._serve_api_trends()
        elif path == '/favicon.ico':
            self.send_response(404)
            self.end_headers()
        else:
            logger.warning(f"❌ Rota não encontrada: {path}")
            self.send_error(404)
    
    def _serve_dashboard(self):
        """Serve página principal do dashboard"""
        try:
            html = self._generate_html()
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
            logger.info("📄 Dashboard servido com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao servir dashboard: {e}")
            self.send_error(500, str(e))
    
    def _serve_api_status(self):
        """API: Status do sistema"""
        try:
            stats = self.store.get_stats()
            baseline = self.store.get_baseline(7)
            
            data = {
                'status': 'ok',
                'timestamp': datetime.now().isoformat(),
                'stats': stats,
                'baseline': baseline
            }
            
            self._send_json(data)
            logger.info("📊 API status servida")
            
        except Exception as e:
            logger.error(f"❌ Erro na API status: {e}")
            self._send_json({'status': 'error', 'message': str(e)}, status=500)
    
    def _serve_api_alerts(self):
        """API: Alertas recentes"""
        try:
            alerts = self.store.get_recent_alerts(24)
            self._send_json({'alerts': alerts})
            logger.info(f"🚨 API alerts servida: {len(alerts)} alertas")
        except Exception as e:
            logger.error(f"❌ Erro na API alerts: {e}")
            self._send_json({'alerts': [], 'error': str(e)}, status=500)
    
    def _serve_api_baseline(self):
        """API: Baseline atual"""
        try:
            baseline = self.store.get_baseline(7)
            self._send_json(baseline)
            logger.info("📈 API baseline servida")
        except Exception as e:
            logger.error(f"❌ Erro na API baseline: {e}")
            self._send_json({'error': str(e)}, status=500)
    
    def _serve_api_trends(self):
        """API: Tendências"""
        try:
            trends = {
                'roas': self.store.get_trend('roas', 7),
                'ctr': self.store.get_trend('ctr', 7),
                'cpc': self.store.get_trend('cpc', 7)
            }
            self._send_json(trends)
            logger.info("📈 API trends servida")
        except Exception as e:
            logger.error(f"❌ Erro na API trends: {e}")
            self._send_json({'error': str(e)}, status=500)
    
    def _send_json(self, data, status=200):
        """Envia resposta JSON"""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # CORS para desenvolvimento
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, default=str).encode('utf-8'))
    
    def _generate_html(self) -> str:
        """Gera HTML do dashboard"""
        try:
            stats = self.store.get_stats()
            baseline = self.store.get_baseline(7)
            recent_alerts = self.store.get_recent_alerts(24)
            trends = {
                'roas': self.store.get_trend('roas', 7),
                'ctr': self.store.get_trend('ctr', 7)
            }
            
            # Cores para alertas
            alert_count = len(recent_alerts)
            status_color = '#e74c3c' if alert_count > 0 else '#27ae60'
            status_text = f'{alert_count} ALERTAS' if alert_count > 0 else 'SISTEMA OK'
            
            logger.debug(f"🎨 Gerando HTML: {status_text}, {len(recent_alerts)} alertas")
            
            # HTML simplificado mas funcional
            html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🦈 PiranhaOps Dashboard</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
        }}
        
        .container {{ max-width: 1200px; margin: 0 auto; }}
        
        header {{ text-align: center; padding: 20px 0; border-bottom: 2px solid #334155; margin-bottom: 30px; }}
        
        h1 {{ 
            font-size: 2.5em;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        
        .subtitle {{ color: #94a3b8; font-size: 1.1em; }}
        
        .status-bar {{
            background: {status_color};
            color: white;
            padding: 15px 30px;
            border-radius: 10px;
            text-align: center;
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 30px;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: #1e293b;
            border-radius: 12px;
            padding: 25px;
            border: 1px solid #334155;
        }}
        
        .card h3 {{ color: #94a3b8; font-size: 0.9em; margin-bottom: 10px; }}
        
        .metric {{
            font-size: 2.2em;
            font-weight: bold;
            color: #f8fafc;
        }}
        
        .metric.positive {{ color: #10b981; }}
        .metric.negative {{ color: #ef4444; }}
        .metric.warning {{ color: #f59e0b; }}
        
        .section {{
            background: #1e293b;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            border: 1px solid #334155;
        }}
        
        .section h2 {{ color: #f8fafc; margin-bottom: 20px; }}
        
        .alert {{
            background: #7f1d1d;
            border-left: 4px solid #ef4444;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 6px;
        }}
        
        .alert-title {{ font-weight: bold; margin-bottom: 5px; }}
        .alert-time {{ font-size: 0.85em; color: #94a3b8; }}
        
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ text-align: left; padding: 12px; border-bottom: 1px solid #334155; }}
        th {{ color: #94a3b8; }}
        
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .badge.good {{ background: #064e3b; color: #10b981; }}
        .badge.warning {{ background: #451a03; color: #f59e0b; }}
        .badge.bad {{ background: #450a0a; color: #ef4444; }}
        
        .refresh {{
            background: #667eea;
            color: white;
            border: none;
            padding: 15px 25px;
            border-radius: 50px;
            cursor: pointer;
            font-size: 1em;
            margin: 20px 0;
        }}
        
        .refresh:hover {{ background: #764ba2; }}
        
        .empty-state {{ text-align: center; padding: 40px; color: #64748b; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🦈 PiranhaOps</h1>
            <p class="subtitle">Sistema de Monitoramento B2B - Tattoo Supplies</p>
        </header>
        
        <div class="status-bar">
            {status_text} | Última atualização: {datetime.now().strftime('%H:%M:%S')}
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>Baseline ROAS (7d)</h3>
                <div class="metric {'positive' if baseline['metrics']['roas'] >= 3 else 'warning'}">
                    {baseline['metrics']['roas']:.2f}x
                </div>
                <div style="color: {'#10b981' if trends['roas']['trend'] == 'up' else '#ef4444' if trends['roas']['trend'] == 'down' else '#94a3b8'}">
                    {'↑' if trends['roas']['trend'] == 'up' else '↓' if trends['roas']['trend'] == 'down' else '→'} 
                    {trends['roas']['change_pct']}% vs período anterior
                </div>
            </div>
            
            <div class="card">
                <h3>Baseline CTR (7d)</h3>
                <div class="metric {'positive' if baseline['metrics']['ctr'] >= 1.5 else 'warning'}">
                    {baseline['metrics']['ctr']:.2f}%
                </div>
                <div style="color: {'#10b981' if trends['ctr']['trend'] == 'up' else '#ef4444' if trends['ctr']['trend'] == 'down' else '#94a3b8'}">
                    {'↑' if trends['ctr']['trend'] == 'up' else '↓' if trends['ctr']['trend'] == 'down' else '→'}
                    {trends['ctr']['change_pct']}% vs período anterior
                </div>
            </div>
            
            <div class="card">
                <h3>CPC Médio</h3>
                <div class="metric">
                    €{baseline['metrics']['cpc']:.2f}
                </div>
                <div style="color: #94a3b8;">Baseline calculado em {baseline['data_points']} dias</div>
            </div>
            
            <div class="card">
                <h3>Alertas 24h</h3>
                <div class="metric {'negative' if alert_count > 0 else 'positive'}">
                    {alert_count}
                </div>
                <div style="color: #94a3b8;">Total 7d: {stats['total_alerts_7d']}</div>
            </div>
        </div>
        
        <div class="section">
            <h2>🚨 Alertas Recentes (24h)</h2>
            {self._generate_alerts_html(recent_alerts)}
        </div>
        
        <div class="section">
            <h2>📊 Thresholds de Alerta</h2>
            <table>
                <tr>
                    <th>Métrica</th>
                    <th>Status OK</th>
                    <th>Atenção</th>
                    <th>Crítico</th>
                </tr>
                <tr>
                    <td>ROAS</td>
                    <td><span class="badge good">≥ {baseline['thresholds']['roas_warning']:.2f}x</span></td>
                    <td><span class="badge warning">{baseline['thresholds']['roas_critical']:.2f}x - {baseline['thresholds']['roas_warning']:.2f}x</span></td>
                    <td><span class="badge bad">< {baseline['thresholds']['roas_critical']:.2f}x</span></td>
                </tr>
                <tr>
                    <td>CTR</td>
                    <td><span class="badge good">≥ {baseline['thresholds']['ctr_warning']:.2f}%</span></td>
                    <td><span class="badge warning">{baseline['thresholds']['ctr_critical']:.2f}% - {baseline['thresholds']['ctr_warning']:.2f}%</span></td>
                    <td><span class="badge bad">< {baseline['thresholds']['ctr_critical']:.2f}%</span></td>
                </tr>
            </table>
        </div>
        
        <div class="section">
            <h2>💾 Status do Data Store</h2>
            <p><strong>Total de snapshots:</strong> {stats['total_snapshots']}</p>
            <p><strong>Período:</strong> {stats['date_range']['first'] or 'N/A'} até {stats['date_range']['last'] or 'N/A'}</p>
            <p><strong>Tamanho dos dados:</strong> {(stats['file_sizes']['campaigns'] + stats['file_sizes']['baseline'] + stats['file_sizes']['alerts']) / 1024:.1f} KB</p>
            <p><strong>Baseline calculado:</strong> {'Sim' if baseline.get('data_points', 0) > 0 else 'Não (usando padrão)'}</p>
        </div>
        
        <button class="refresh" onclick="location.reload()">
            🔄 Atualizar
        </button>
        
        <script>
            // Auto-refresh a cada 30 segundos
            setTimeout(() => location.reload(), 30000);
        </script>
    </div>
</body>
</html>
"""
            return html
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar HTML: {e}")
            return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>🦈 PiranhaOps Dashboard - Erro</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f8fafc; padding: 40px; }}
        .error {{ background: #fee2e2; border: 2px solid #ef4444; padding: 20px; border-radius: 8px; }}
        h1 {{ color: #ef4444; }}
    </style>
</head>
<body>
    <div class="error">
        <h1>🚨 Erro no Dashboard</h1>
        <p>{str(e)}</p>
        <p>Tente recarregar a página ou verificar os logs.</p>
        <button onclick="location.reload()">Recarregar</button>
    </div>
</body>
</html>
"""
    
    def _generate_alerts_html(self, alerts: list) -> str:
        """Gera HTML da lista de alertas"""
        if not alerts:
            return '<div class="empty-state">✅ Nenhum alerta nas últimas 24 horas</div>'
        
        html = ''
        for alert_data in alerts:
            alert = alert_data.get('alert', {})
            level = alert.get('level', 'MEDIUM').lower()
            title = alert.get('title', 'Alerta')
            message = alert.get('description', alert.get('message', ''))
            time = datetime.fromisoformat(alert_data['timestamp']).strftime('%d/%m %H:%M')
            
            html += f"""
            <div class="alert {level}">
                <div class="alert-title">{title}</div>
                <div>{message}</div>
                <div class="alert-time">{time}</div>
            </div>
            """
        
        return html
    
    def log_message(self, format, *args):
        """Silencia logs do servidor"""
        pass

def start_dashboard(port: int = PORT):
    """Inicia o servidor do dashboard"""
    handler = DashboardHandler
    
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"\n{'='*60}")
            print(f"🌐 DASHBOARD PIRANHAOPS RODANDO")
            print(f"{'='*60}")
            print(f"🔗 URL: http://localhost:{port}")
            print(f"📊 Acesse no navegador para visualizar métricas")
            print(f"⏱️  Auto-refresh: 30 segundos")
            print(f"{'='*60}")
            
            # Abrir navegador automaticamente
            try:
                import webbrowser
                webbrowser.open(f'http://localhost:{port}')
            except:
                pass
            
            print("\n🚀 Servidor iniciado! Pressione Ctrl+C para parar")
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido")
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor: {e}")

if __name__ == "__main__":
    start_dashboard()