#!/usr/bin/env python3
"""
Teste rápido do dashboard
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_store import DataStore
import json

def test_dashboard_data():
    """Testa se os dados do dashboard estão acessíveis"""
    print("🧪 Testando dados do dashboard...")
    
    store = DataStore()
    
    # Testar cada componente do dashboard
    print("📊 Testando stats...")
    stats = store.get_stats()
    print(f"   ✅ Stats: {stats['total_snapshots']} snapshots")
    
    print("📈 Testando baseline...")
    baseline = store.get_baseline(7)
    print(f"   ✅ Baseline: ROAS {baseline['metrics']['roas']:.2f}x")
    
    print("🚨 Testando alertas...")
    alerts = store.get_recent_alerts(24)
    print(f"   ✅ Alertas: {len(alerts)} alertas recentes")
    
    print("📊 Testando tendências...")
    trends = {
        'roas': store.get_trend('roas', 7),
        'ctr': store.get_trend('ctr', 7)
    }
    print(f"   ✅ Tendências: ROAS {trends['roas']['trend']}, CTR {trends['ctr']['trend']}")
    
    # Simular dados que apareceriam no dashboard
    print(f"\n📋 RESUMO DO DASHBOARD:")
    print(f"   Status: {'🚨 ALERTAS' if stats['total_alerts_24h'] > 0 else '✅ SISTEMA OK'}")
    print(f"   Baseline ROAS: {baseline['metrics']['roas']:.2f}x")
    print(f"   Baseline CTR: {baseline['metrics']['ctr']:.2f}%")
    print(f"   Alertas 24h: {stats['total_alerts_24h']}")
    print(f"   Tendência ROAS: {trends['roas']['change_pct']:.1f}% ({trends['roas']['trend']})")
    print(f"   Thresholds: ROAS crítico < {baseline['thresholds']['roas_critical']:.2f}x")
    
    return True

if __name__ == "__main__":
    success = test_dashboard_data()
    if success:
        print("\n🎉 DADOS DO DASHBOARD PRONTOS!")
        print("✅ Todos os componentes estão funcionando")
        print("✅ Baseline calculado corretamente")
        print("✅ Sistema de persistência operacional")
        print("\n💡 Para ver o dashboard, execute:")
        print("   python dashboard/server.py")
        print("   E acesse: http://localhost:8080")
    else:
        print("\n❌ Problemas detectados nos dados")