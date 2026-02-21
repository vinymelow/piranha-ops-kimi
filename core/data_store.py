"""
Data Store - Persistência local em JSON
Para baseline histórico e métricas de campanhas
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DataStore:
    """
    Armazena histórico de métricas para baseline e análise de tendências
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.campaigns_file = self.data_dir / "campaigns_history.json"
        self.baseline_file = self.data_dir / "baseline.json"
        self.alerts_file = self.data_dir / "alerts_history.json"
        self.metrics_file = self.data_dir / "daily_metrics.json"
        
        # Inicializar arquivos se não existirem
        self._init_files()
        
        logger.info(f"📊 DataStore inicializado em: {self.data_dir}")
    
    def _init_files(self):
        """Cria arquivos vazios se não existirem"""
        for file_path in [self.campaigns_file, self.baseline_file, self.alerts_file, self.metrics_file]:
            if not file_path.exists():
                self._save_json(file_path, [])
                logger.debug(f"📄 Criado arquivo: {file_path.name}")
    
    def _load_json(self, file_path: Path) -> List[Dict]:
        """Carrega dados JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.debug(f"📖 Carregados {len(data)} registros de {file_path.name}")
                return data
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning(f"⚠️ Erro ao carregar {file_path.name}: {e}")
            return []
    
    def _save_json(self, file_path: Path, data: List[Dict]):
        """Salva dados JSON"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            logger.debug(f"💾 Salvos {len(data)} registros em {file_path.name}")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar {file_path.name}: {e}")
    
    def save_campaign_snapshot(self, snapshot: Dict):
        """
        Salva snapshot diário de campanhas
        """
        try:
            history = self._load_json(self.campaigns_file)
            
            entry = {
                'timestamp': datetime.now().isoformat(),
                'date': datetime.now().strftime('%Y-%m-%d'),
                'hour': datetime.now().strftime('%H:%M'),
                'summary': snapshot.get('summary', {}),
                'campaigns': snapshot.get('campaigns', []),
                'scenario': snapshot.get('scenario', 'unknown')
            }
            
            history.append(entry)
            
            # Manter apenas últimos 90 dias (economizar espaço)
            cutoff = datetime.now() - timedelta(days=90)
            history = [
                h for h in history 
                if datetime.fromisoformat(h['timestamp']) > cutoff
            ]
            
            self._save_json(self.campaigns_file, history)
            print(f"✅ Snapshot salvo: {entry['date']} {entry['hour']} | {len(entry['campaigns'])} campanhas")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar snapshot: {e}")
    
    def get_baseline(self, days: int = 7) -> Dict:
        """
        Calcula baseline dos últimos N dias
        Retorna médias de ROAS, CTR, CPC, etc.
        """
        try:
            history = self._load_json(self.campaigns_file)
            
            if not history:
                logger.info("📊 Usando baseline padrão - sem histórico")
                return self._default_baseline()
            
            # Filtrar últimos N dias
            cutoff = datetime.now() - timedelta(days=days)
            recent = [
                h for h in history 
                if datetime.fromisoformat(h['timestamp']) > cutoff
            ]
            
            if not recent:
                logger.info("📊 Usando baseline padrão - sem dados recentes")
                return self._default_baseline()
            
            # Calcular médias ponderadas por número de campanhas
            total_campaigns = sum(r['summary'].get('total_campaigns', 0) for r in recent)
            
            if total_campaigns == 0:
                return self._default_baseline()
            
            # Médias ponderadas
            avg_roas = sum(r['summary'].get('avg_roas', 0) * r['summary'].get('total_campaigns', 0) for r in recent) / total_campaigns
            avg_ctr = sum(r['summary'].get('avg_ctr', 0) * r['summary'].get('total_campaigns', 0) for r in recent) / total_campaigns
            avg_cpc = sum(r['summary'].get('avg_cpc', 0) * r['summary'].get('total_campaigns', 0) for r in recent) / total_campaigns
            total_spend = sum(r['summary'].get('total_spend', 0) for r in recent)
            
            baseline = {
                'calculated_at': datetime.now().isoformat(),
                'period_days': days,
                'data_points': len(recent),
                'total_campaigns': total_campaigns,
                'metrics': {
                    'roas': round(avg_roas, 2),
                    'ctr': round(avg_ctr, 2),
                    'cpc': round(avg_cpc, 2),
                    'spend': round(total_spend, 2),
                    'spend_daily': round(total_spend / days, 2)
                },
                'thresholds': {
                    'roas_critical': round(avg_roas * 0.7, 2),  # 30% abaixo
                    'roas_warning': round(avg_roas * 0.85, 2),  # 15% abaixo
                    'ctr_critical': round(avg_ctr * 0.6, 2),    # 40% abaixo
                    'ctr_warning': round(avg_ctr * 0.8, 2)      # 20% abaixo
                }
            }
            
            # Salvar baseline calculado
            self._save_json(self.baseline_file, [baseline])
            logger.info(f"📊 Baseline calculado: ROAS {baseline['metrics']['roas']:.2f} | CTR {baseline['metrics']['ctr']:.2f}%")
            
            return baseline
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular baseline: {e}")
            return self._default_baseline()
    
    def _default_baseline(self) -> Dict:
        """Baseline padrão quando não há histórico"""
        return {
            'calculated_at': datetime.now().isoformat(),
            'period_days': 0,
            'data_points': 0,
            'total_campaigns': 0,
            'metrics': {
                'roas': 3.5,  # Benchmark B2B tattoo supplies
                'ctr': 1.5,
                'cpc': 0.75,
                'spend': 0,
                'spend_daily': 0
            },
            'thresholds': {
                'roas_critical': 2.5,
                'roas_warning': 3.0,
                'ctr_critical': 1.0,
                'ctr_warning': 1.2
            },
            'note': 'Usando benchmark padrão - sem histórico suficiente'
        }
    
    def save_alert(self, alert: Dict):
        """Salva alerta disparado"""
        try:
            history = self._load_json(self.alerts_file)
            
            entry = {
                'timestamp': datetime.now().isoformat(),
                'alert': alert,
                'resolved': False
            }
            
            history.append(entry)
            self._save_json(self.alerts_file, history)
            logger.info(f"🚨 Alerta salvo: {alert.get('title', 'Sem título')}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar alerta: {e}")
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict]:
        """Retorna alertas recentes"""
        try:
            history = self._load_json(self.alerts_file)
            cutoff = datetime.now() - timedelta(hours=hours)
            
            recent = [
                h for h in history 
                if datetime.fromisoformat(h['timestamp']) > cutoff
            ]
            
            logger.debug(f"📋 Retornados {len(recent)} alertas recentes ({hours}h)")
            return recent
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar alertas recentes: {e}")
            return []
    
    def get_trend(self, metric: str = 'roas', days: int = 7) -> Dict:
        """
        Analisa tendência de uma métrica
        Retorna: subindo, estável, caindo
        """
        try:
            history = self._load_json(self.campaigns_file)
            
            if len(history) < 3:
                return {'trend': 'insufficient_data', 'change_pct': 0, 'metric': metric}
            
            recent = history[-days:] if len(history) >= days else history
            values = [r['summary'].get(f'avg_{metric}', 0) for r in recent if r['summary'].get(f'avg_{metric}')]
            
            if len(values) < 2:
                return {'trend': 'insufficient_data', 'change_pct': 0, 'metric': metric}
            
            # Calcular tendência (primeira metade vs segunda metade)
            mid = len(values) // 2
            first_half = sum(values[:mid]) / mid if mid > 0 else 0
            second_half = sum(values[mid:]) / (len(values) - mid) if (len(values) - mid) > 0 else 0
            
            if first_half == 0:
                change_pct = 0
            else:
                change_pct = ((second_half - first_half) / first_half) * 100
            
            if change_pct > 10:
                trend = 'up'
            elif change_pct < -10:
                trend = 'down'
            else:
                trend = 'stable'
            
            result = {
                'trend': trend,
                'change_pct': round(change_pct, 1),
                'current_avg': round(second_half, 2),
                'previous_avg': round(first_half, 2),
                'metric': metric
            }
            
            logger.debug(f"📈 Tendência {metric}: {trend} ({change_pct:.1f}%)")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular tendência: {e}")
            return {'trend': 'error', 'change_pct': 0, 'metric': metric}
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do data store"""
        try:
            campaigns = self._load_json(self.campaigns_file)
            alerts = self._load_json(self.alerts_file)
            baseline = self._load_json(self.baseline_file)
            
            total_alerts_24h = len([a for a in alerts 
                if datetime.fromisoformat(a['timestamp']) > datetime.now() - timedelta(hours=24)])
            
            total_alerts_7d = len([a for a in alerts 
                if datetime.fromisoformat(a['timestamp']) > datetime.now() - timedelta(days=7)])
            
            stats = {
                'total_snapshots': len(campaigns),
                'date_range': {
                    'first': campaigns[0]['date'] if campaigns else None,
                    'last': campaigns[-1]['date'] if campaigns else None
                },
                'total_alerts_24h': total_alerts_24h,
                'total_alerts_7d': total_alerts_7d,
                'baseline_exists': len(baseline) > 0 and baseline[0].get('data_points', 0) > 0,
                'file_sizes': {
                    'campaigns': os.path.getsize(self.campaigns_file) if self.campaigns_file.exists() else 0,
                    'baseline': os.path.getsize(self.baseline_file) if self.baseline_file.exists() else 0,
                    'alerts': os.path.getsize(self.alerts_file) if self.alerts_file.exists() else 0
                }
            }
            
            logger.debug(f"📊 Stats: {stats['total_snapshots']} snapshots, {stats['total_alerts_24h']} alertas 24h")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter stats: {e}")
            return {'error': str(e)}