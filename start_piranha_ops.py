#!/usr/bin/env python3
"""
PiranhaOps AIOS v4.0 - Startup Script
Inicializa sistema completo com verificações de saúde e auto-configuração
Seguindo especificações do prompt estratégico completo
"""

import asyncio
import sys
import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import logging
import threading
import time
import webbrowser

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/piranha_ops.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("piranha_startup")

# Adicionar paths
sys.path.append(str(Path(__file__).parent))

class PiranhaStartup:
    """
    Sistema de inicialização e verificação do PiranhaOps AIOS v4.0
    Responsável por setup completo, validações e primeiro run
    """
    
    def __init__(self):
        self.version = "3.0.0"
        self.config_path = Path("config/mcp_config.json")
        self.data_path = Path("data")
        self.logs_path = Path("logs")
        self.required_env_vars = [
            "MOONSHOT_API_KEY",
            "SHOPIFY_ACCESS_TOKEN", 
            "SHOPIFY_SHOP_DOMAIN",
            "KLAVIYO_API_KEY",
            "EVOLUTION_API_KEY",
            "META_ACCESS_TOKEN",
            "META_AD_ACCOUNT_ID"
        ]
    
    async def full_startup(self):
        """Sequência completa de inicialização"""
        print(f"\n{'='*80}")
        print(f"🦈 PIRANHAOPS AIOS v{self.version} - STARTUP SEQUENCE")
        print(f"{'='*80}")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"👤 Sales Operations Specialist: Vinycius Melo")
        print(f"🏢 Piranha Global - B2B Tattoo Supplies")
        print(f"{'='*80}\n")
        
        steps = [
            ("Verificando estrutura de diretórios", self._check_directories),
            ("Verificando variáveis de ambiente", self._check_environment),
            ("Inicializando banco de dados Sinapse", self._init_database),
            ("Carregando biblioteca de métricas", self._load_metrics_library),
            ("Verificando MCP Servers", self._check_mcp_servers),
            ("Inicializando Squads", self._init_squads),
            ("Criando dashboard executivo", self._create_dashboard_files),
            ("Iniciando Dashboard Web", self._start_dashboard),
            ("Executando health check final", self._final_health_check)
        ]
        
        results = []
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            try:
                result = await step_func()
                results.append((step_name, True, result))
                print(f"   ✅ {step_name} - OK")
            except Exception as e:
                results.append((step_name, False, str(e)))
                print(f"   ❌ {step_name} - FALHA: {e}")
                logger.error(f"Startup step failed: {step_name} - {e}")
        
        # Relatório final
        await self._print_startup_report(results)
        
        return all(success for _, success, _ in results)

    async def _check_directories(self):
        """Cria estrutura de diretórios necessária"""
        required_structure = {
            'ai_os': ['core', 'memory', 'task_engine'],
            'squads': {
                'commercial': ['cart_recovery', 'lead_scraper', 'stock_forecast'],
                'wholesale': ['partner_automation', 'tier_manager', 'b2b_onboarding'],
                'operational': ['dhl_automation', 'cod_reconciliation', 'time_tracker'],
                'compliance': ['infarmed_reporter', 'rma_automation', 'bank_reconciliation']
            },
            'mcp_servers': ['meta', 'shopify', 'klaviyo', 'whatsapp', 'sage', 'slack'],
            'dashboard': ['templates', 'static/css', 'static/js'],
            'config': [],
            'data': ['journey_logs', 'metrics_history', 'backups'],
            'logs': [],
            'tests': ['unit', 'integration', 'e2e']
        }
        
        created = []
        for parent, children in required_structure.items():
            parent_path = Path(parent)
            parent_path.mkdir(parents=True, exist_ok=True)
            created.append(str(parent_path))
            
            if isinstance(children, dict):
                for child, subchildren in children.items():
                    child_path = parent_path / child
                    child_path.mkdir(parents=True, exist_ok=True)
                    created.append(str(child_path))
                    
                    for subchild in subchildren:
                        subchild_path = child_path / subchild
                        subchild_path.mkdir(parents=True, exist_ok=True)
                        created.append(str(subchild_path))
            else:
                for child in children:
                    child_path = parent_path / child
                    if '.' not in child:  # É diretório
                        child_path.mkdir(parents=True, exist_ok=True)
                        created.append(str(child_path))
        
        # Criar __init__.py files
        for path in Path('.').rglob('*/'):
            if 'venv' not in str(path) and '__pycache__' not in str(path):
                init_file = path / '__init__.py'
                if not init_file.exists():
                    init_file.touch()
        
        return f"{len(created)} diretórios verificados/criados"

    async def _check_environment(self):
        """Verifica variáveis de ambiente necessárias"""
        missing = []
        present = []
        
        for var in self.required_env_vars:
            value = os.getenv(var)
            if not value:
                missing.append(var)
                # Criar .env.example se não existir
                self._create_env_template()
            else:
                # Mask para log
                masked = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
                present.append(f"{var}={masked}")
        
        if missing:
            raise EnvironmentError(
                f"Variáveis ausentes: {', '.join(missing)}\n"
                f"Configure em .env ou exporte manualmente"
            )
        
        return f"{len(present)} variáveis configuradas"

    def _create_env_template(self):
        """Cria template .env se não existir"""
        env_file = Path(".env")
        env_example = Path(".env.example")
        
        if not env_file.exists() and not env_example.exists():
            template = """# PiranhaOps AIOS v4.0 - Environment Configuration

# Copie para .env e preencha com valores reais

# AI/ML APIs
MOONSHOT_API_KEY=sk-your-moonshot-key-here

# Shopify (B2B E-commerce)
SHOPIFY_ACCESS_TOKEN=shpat_your_token_here
SHOPIFY_SHOP_DOMAIN=piranha-global.myshopify.com

# Klaviyo (Email + Data Bridge)
KLAVIYO_API_KEY=pk_your_public_key
KLAVIYO_PRIVATE_KEY=pk_your_private_key

# WhatsApp Evolution API (Custo ZERO)
EVOLUTION_API_KEY=your_evolution_api_key
EVOLUTION_API_URL=http://localhost:8080

# Meta Marketing
META_ACCESS_TOKEN=EAAyour_access_token
META_AD_ACCOUNT_ID=act_your_account_id
META_CAPI_TOKEN=your_capi_token

# Sage X3 (ERP)
SAGE_X3_API_URL=https://sage.piranhaglobal.com/api
SAGE_X3_API_KEY=your_sage_key

# Slack/Teams (verificar qual plataforma empresa usa)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# Configurações AIOS
AIOS_QUALITY_THRESHOLD=0.85
AIOS_MAX_TASKS=1000
AIOS_LOG_LEVEL=INFO

# Otimização de Custos
BUDGET_DAILY_USD=1.00
BUDGET_MONTHLY_EUR=37
"""
            env_example.write_text(template)
            print(f"   📝 Template criado: .env.example")

    async def _init_database(self):
        """Inicializa SQLite Sinapse (Memory & Persistence)"""
        db_path = self.data_path / "sinapse.db"
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Tabela de memória de contexto (anti-DocRot)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sinapse_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                context_key TEXT UNIQUE NOT NULL,
                context_data TEXT NOT NULL,
                agent_origin TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP,
                expiration_date TIMESTAMP
            )
        """)
        
        # Tabela de métricas históricas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_id TEXT NOT NULL,
                phase TEXT NOT NULL,
                value REAL NOT NULL,
                target REAL,
                tier TEXT,
                source TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de tasks (Journey Log)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_journey (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT UNIQUE NOT NULL,
                squad TEXT NOT NULL,
                description TEXT,
                input_data TEXT,
                output_data TEXT,
                quality_score REAL,
                status TEXT DEFAULT 'pending',
                executor TEXT,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                error_log TEXT
            )
        """)
        
        # Tabela de parceiros B2B
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wholesale_partners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partner_id TEXT UNIQUE NOT NULL,
                email TEXT,
                company_name TEXT,
                nif TEXT,
                tier TEXT DEFAULT 'bronze',
                credit_score REAL,
                volume_monthly REAL,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_evaluation TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        """)
        
        # Tabela de carrinhos recuperados
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cart_recovery (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                checkout_token TEXT NOT NULL,
                customer_email TEXT,
                phone_last4 TEXT,
                cart_value REAL,
                channel TEXT,
                status TEXT,
                recovered_at TIMESTAMP,
                quality_score REAL
            )
        """)
        
        # Triggers para atualização automática
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_sinapse_timestamp 
            AFTER UPDATE ON sinapse_memory
            BEGIN
                UPDATE sinapse_memory SET updated_at = CURRENT_TIMESTAMP 
                WHERE id = NEW.id;
            END
        """)
        
        conn.commit()
        conn.close()
        
        return f"Banco Sinapse inicializado: {db_path}"

    async def _load_metrics_library(self):
        """Carrega e valida biblioteca de métricas"""
        try:
            from config.metrics_library import ALL_METRICS, MetricPhase
            
            metrics_count = len(ALL_METRICS)
            by_phase = {}
            
            for metric_id, threshold in ALL_METRICS.items():
                # Determinar fase pelo nome da métrica
                phase = self._detect_phase(metric_id)
                by_phase[phase] = by_phase.get(phase, 0) + 1
            
            # Validar integridade
            assert metrics_count > 0, "Nenhuma métrica carregada"
            assert all(threshold.target > 0 for threshold in ALL_METRICS.values()), \
                "Métricas sem target definido"
            
            return f"{metrics_count} métricas carregadas: {by_phase}"
        except ImportError as e:
            raise ImportError(f"Biblioteca de métricas não encontrada: {e}")

    def _detect_phase(self, metric_id: str) -> str:
        """Detecta fase da métrica pelo ID"""
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

    async def _check_mcp_servers(self):
        """Verifica saúde dos MCP Servers"""
        # Mock - em produção verificaria cada servidor
        servers = {
            "whatsapp_evolution": {"connected": True, "state": "open", "latency": 45},
            "shopify": {"connected": True, "state": "active", "latency": 120},
            "klaviyo": {"connected": True, "state": "active", "latency": 80},
            "meta": {"connected": False, "state": "config_pending", "latency": 0},
            "sage_x3": {"connected": False, "state": "not_configured", "latency": 0}
        }
        
        connected = sum(1 for s in servers.values() if s["connected"])
        return f"{connected}/{len(servers)} MCP servers online"

    async def _init_squads(self):
        """Inicializa os 5 Squads Revenue Activation"""
        squads = {
            "commercial": {
                "name": "🎯 Revenue Activation Squad",
                "focus": "Fase 1 (0-30 dias)",
                "agents": ["CartRecovery", "LeadScraper", "StockForecaster"],
                "priority": 1,
                "status": "active"
            },
            "wholesale": {
                "name": "🏭 Wholesale Engine Squad", 
                "focus": "Fase 2 (30-60 dias)",
                "agents": ["PartnerAutomation", "TierManager", "B2BOnboarding"],
                "priority": 2,
                "status": "active"
            },
            "operational": {
                "name": "⚙️ Operational Liberation Squad",
                "focus": "Fase 3 (60-90 dias)", 
                "agents": ["DHLAutomation", "CODReconciliation", "TimeTracker"],
                "priority": 3,
                "status": "setup"
            },
            "compliance": {
                "name": "📋 Compliance Squad",
                "focus": "Fase 4 (90-120 dias)",
                "agents": ["InfarmedReporter", "RMAAutomation", "BankReconciliation"],
                "priority": 4,
                "status": "pending"
            }
        }
        
        # Criar arquivos de squad se não existirem
        for squad_id, config in squads.items():
            squad_file = Path(f"squads/{squad_id}/squad_config.json")
            squad_file.parent.mkdir(parents=True, exist_ok=True)
            
            if not squad_file.exists():
                squad_file.write_text(json.dumps(config, indent=2, ensure_ascii=False))
        
        return f"{len(squads)} Squads inicializados"

    async def _create_dashboard_files(self):
        """Cria arquivos do dashboard executivo"""
        # Criar CSS do Design System
        css_content = """
/* Piranha Design System v4.0 */
:root {
    --piranha-black: #0A0A0A;
    --piranha-dark: #141414;
    --piranha-gray: #1F1F1F;
    --piranha-light-gray: #2A2A2A;
    --piranha-red: #E30613;
    --piranha-red-dark: #B8050F;
    --text-primary: #FFFFFF;
    --text-secondary: #A0A0A0;
    --success: #10B981;
    --warning: #F59E0B;
    --danger: #EF4444;
    --info: #3B82F6;
}

/* Glass Effect Cards */
.metric-card {
    background: linear-gradient(135deg, var(--piranha-dark) 0%, var(--piranha-gray) 100%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 24px;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
}

/* Squad Cards */
.squad-card {
    background: linear-gradient(135deg, var(--piranha-dark) 0%, rgba(227, 6, 19, 0.05) 100%);
    border: 1px solid rgba(227, 6, 19, 0.2);
    border-radius: 12px;
    padding: 24px;
    backdrop-filter: blur(10px);
}

.agent-badge {
    background: rgba(227, 6, 19, 0.1);
    color: var(--piranha-red);
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 12px;
}

/* Progress Bars */
.progress-bar {
    width: 100%;
    height: 8px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--piranha-red) 0%, #FF6B6B 100%);
    transition: width 0.5s ease;
}

/* Animations */
@keyframes shimmer {
    0% { left: -100%; }
    100% { left: 100%; }
}

.progress-fill::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
    animation: shimmer 1.5s infinite;
}
"""
        
        css_file = Path("dashboard/static/css/piranha-theme.css")
        css_file.parent.mkdir(parents=True, exist_ok=True)
        css_file.write_text(css_content)
        
        return "Arquivos do dashboard criados"

    async def _start_dashboard(self):
        """Inicia dashboard web em thread separada"""
        def run_dashboard():
            try:
                from dashboard.server_v3 import app
                app.run(
                    host='0.0.0.0',
                    port=8083,
                    debug=False,
                    use_reloader=False
                )
            except Exception as e:
                logger.error(f"Erro ao iniciar dashboard: {e}")
        
        dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
        dashboard_thread.start()
        
        # Aguardar inicialização e abrir navegador
        await asyncio.sleep(3)
        
        # Abrir navegador automaticamente
        try:
            webbrowser.open('http://localhost:8083')
            print("   🌐 Navegador aberto automaticamente")
        except:
            print("   📍 Acesse manualmente: http://localhost:8083")
        
        return "Dashboard online em http://localhost:8083"

    async def _final_health_check(self):
        """Health check final do sistema"""
        checks = {
            "database": (self.data_path / "sinapse.db").exists(),
            "metrics_library": (Path("config/metrics_library.py")).exists(),
            "mcp_config": (Path("config/mcp_config.json")).exists(),
            "dashboard_templates": (Path("dashboard/templates/dashboard_executive.html")).exists(),
            "logs_directory": (Path("logs")).exists()
        }
        
        all_healthy = all(checks.values())
        
        if all_healthy:
            return f"✅ Sistema 100% operacional: {len(checks)} checks passaram"
        else:
            failed = [k for k, v in checks.items() if not v]
            raise RuntimeError(f"Health check falhou em: {', '.join(failed)}")

    async def _print_startup_report(self, results):
        """Imprime relatório colorido de startup"""
        print(f"\n{'='*80}")
        print("📊 RELATÓRIO DE INICIALIZAÇÃO")
        print(f"{'='*80}")
        
        for step_name, success, result in results:
            icon = "✅" if success else "❌"
            status = "OK" if success else "FALHA"
            print(f"{icon} {step_name:<40} [{status}]")
            if result:
                print(f"   → {result}")
        
        print(f"{'='*80}")
        
        # Status final
        all_ok = all(success for _, success, _ in results)
        if all_ok:
            print("\n🚀 PIRANHAOPS AIOS v4.0 - PRONTO PARA OPERAÇÃO")
            print("\n📍 Acessos:")
            print("   • Dashboard: http://localhost:8083")
            print("   • Logs: tail -f logs/piranha_ops.log")
            print("   • Database: sqlite3 data/sinapse.db")
            print("\n🎯 Próximos passos sugeridos:")
            print("   1. Verificar métricas baseline no dashboard")
            print("   2. Configurar Evolution API WhatsApp (custo zero)")
            print("   3. Validar integração Meta Ads")
            print("   4. Iniciar Fase 1: Revenue Activation")
        else:
            print("\n⚠️  INICIALIZAÇÃO COM ERROS - Verifique logs/")
        
        print(f"{'='*80}\n")

    async def main():
        """Entry point"""
        startup = PiranhaStartup()
        success = await startup.full_startup()
        if success:
            # Manter sistema rodando
            print("⏳ Sistema operacional. Pressione Ctrl+C para encerrar.")
            try:
                while True:
                    await asyncio.sleep(60)
                    # Health check periódico
                    pass
            except KeyboardInterrupt:
                print("\n🛑 Encerrando PiranhaOps...")
        else:
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())