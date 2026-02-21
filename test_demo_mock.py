#!/usr/bin/env python3
"""
Teste do Demo PiranhaOps em modo Mock puro
Simula o funcionamento completo sem API externa
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import Settings
from integrations.meta_ads_mock import MetaAdsMock

def test_meta_mock_scenarios():
    """Testa os 3 cenários do MetaAdsMock diretamente"""
    print("🚀 Testando MetaAdsMock - 3 Cenários")
    print("="*70)
    
    # Criar simulador
    meta_mock = MetaAdsMock("act_test_12345")
    
    scenarios = [
        ('normal', 'Operação Normal'),
        ('crisis', 'Crise de Performance'),
        ('boom', 'Performance Excelente')
    ]
    
    for scenario, description in scenarios:
        print(f"\n🎭 Cenário: {description}")
        print("-" * 50)
        
        # Configurar cenário
        meta_mock.set_scenario(scenario)
        
        # Obter dados
        data = meta_mock.get_insights("last_7d")
        
        # Análise básica
        summary = data['summary']
        campaigns = data['campaigns']
        issues = data['issues']
        
        print(f"📊 Campanhas: {summary['total_campaigns']}")
        print(f"💰 Spend total: €{summary['total_spend']}")
        print(f"📈 ROAS médio: {summary['avg_roas']}")
        print(f"🎯 CTR médio: {summary['avg_ctr']}%")
        print(f"🚨 Issues detectados: {len(issues)}")
        
        if campaigns:
            print(f"📋 Campanhas principais:")
            for campaign in campaigns[:2]:
                status_icon = "✅" if campaign['roas'] > 3.0 else "⚠️"
                print(f"   {status_icon} {campaign['name'][:30]}...")
                print(f"      ROAS: {campaign['roas']} | CTR: {campaign['ctr']}% | Spend: €{campaign['spend']}")
        
        if issues:
            print(f"   🔴 Problemas críticos:")
            for issue in issues[:2]:
                print(f"      - {issue['campaign']}: {issue['issue']} (€{issue.get('value', 0)})")
    
    print(f"\n✅ Teste MetaAdsMock concluído!")
    return True

def test_data_structure():
    """Testa estrutura dos dados gerados"""
    print("\n🔍 Testando estrutura dos dados...")
    
    meta_mock = MetaAdsMock()
    data = meta_mock.get_insights()
    
    # Verificar campos obrigatórios
    required_fields = ['campaigns', 'summary', 'issues', 'recommendations', 'trends']
    for field in required_fields:
        if field not in data:
            print(f"❌ Campo faltando: {field}")
            return False
    
    # Verificar campanhas
    if not data['campaigns']:
        print("❌ Nenhuma campanha encontrada")
        return False
    
    campaign = data['campaigns'][0]
    campaign_fields = ['id', 'name', 'status', 'objective', 'spend', 'impressions', 'clicks', 
                      'conversions', 'roas', 'cpc', 'ctr', 'cpm', 'conversion_rate']
    
    for field in campaign_fields:
        if field not in campaign:
            print(f"❌ Campo faltando na campanha: {field}")
            return False
    
    print("✅ Estrutura de dados válida!")
    print(f"✅ Campanha exemplo: {campaign['name']}")
    print(f"✅ Conversion rate: {campaign['conversion_rate']}%")
    return True

if __name__ == "__main__":
    print("🚀 INICIANDO TESTES DO SISTEMA PIRANHAOPS")
    print("="*70)
    
    success1 = test_meta_mock_scenarios()
    success2 = test_data_structure()
    
    if success1 and success2:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema pronto para produção quando você tiver as chaves!")
    else:
        print("\n❌ Alguns testes falharam")
    
    sys.exit(0 if (success1 and success2) else 1)