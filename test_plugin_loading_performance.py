#!/usr/bin/env python3
"""
插件載入性能測試
比較標準插件管理器和優化插件管理器的載入時間
"""

import asyncio
import time
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加專案根目錄到 Python 路徑
import sys
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from core.plugin_manager import PluginManager
    from core.fast_plugin_loader import create_optimized_plugin_manager, LoadingStrategy
    print("成功導入插件管理器模組")
except ImportError as e:
    print(f"導入失敗: {e}")
    sys.exit(1)


def test_standard_plugin_loading():
    """測試標準插件管理器載入性能"""
    print("\n" + "="*50)
    print("測試標準插件管理器")
    print("="*50)
    
    start_time = time.time()
    
    # 創建標準插件管理器
    standard_manager = PluginManager()
    
    # 初始化
    standard_manager.initialize()
    
    end_time = time.time()
    loading_time = end_time - start_time
    
    # 獲取載入結果
    plugins = standard_manager.get_all_plugins()
    available_plugins = standard_manager.get_available_plugins()
    
    print(f"⏱️  載入時間: {loading_time:.3f} 秒")
    print(f"📦 總插件數: {len(plugins)}")
    print(f"✅ 可用插件: {len(available_plugins)}")
    print(f"📋 插件列表: {list(plugins.keys())}")
    
    return {
        'loading_time': loading_time,
        'total_plugins': len(plugins),
        'available_plugins': len(available_plugins),
        'plugin_list': list(plugins.keys())
    }


async def test_optimized_plugin_loading():
    """測試優化插件管理器載入性能"""
    print("\n" + "="*50)
    print("🚀 測試優化插件管理器")
    print("="*50)
    
    start_time = time.time()
    
    # 創建優化載入策略
    strategy = LoadingStrategy(
        use_cache=True,
        parallel_loading=True,
        max_workers=4,
        lazy_initialization=True,
        preload_critical=True,
        skip_tool_checks=False,
        cache_duration_hours=24
    )
    
    # 創建優化插件管理器
    optimized_manager = create_optimized_plugin_manager(strategy)
    
    # 異步初始化
    success, message, stats = await optimized_manager.initialize_async()
    
    end_time = time.time()
    loading_time = end_time - start_time
    
    # 獲取載入結果
    plugins = optimized_manager.get_all_plugins()
    available_plugins = optimized_manager.get_available_plugins()
    
    print(f"⏱️  載入時間: {loading_time:.3f} 秒")
    print(f"📦 總插件數: {len(plugins)}")
    print(f"✅ 可用插件: {len(available_plugins)}")
    print(f"📋 插件列表: {list(plugins.keys())}")
    print(f"📊 性能統計: {stats}")
    print(f"🎯 載入成功: {success}")
    print(f"💬 載入訊息: {message}")
    
    return {
        'loading_time': loading_time,
        'total_plugins': len(plugins),
        'available_plugins': len(available_plugins),
        'plugin_list': list(plugins.keys()),
        'success': success,
        'message': message,
        'stats': stats
    }


def compare_results(standard_result, optimized_result):
    """比較載入結果"""
    print("\n" + "="*50)
    print("📊 性能比較結果")
    print("="*50)
    
    standard_time = standard_result['loading_time']
    optimized_time = optimized_result['loading_time']
    
    improvement = ((standard_time - optimized_time) / standard_time) * 100
    
    print(f"標準管理器載入時間: {standard_time:.3f} 秒")
    print(f"優化管理器載入時間: {optimized_time:.3f} 秒")
    print(f"性能提升: {improvement:+.1f}%")
    
    if improvement > 0:
        print(f"🎉 優化管理器速度提升 {improvement:.1f}%")
    elif improvement < 0:
        print(f"⚠️  優化管理器慢了 {abs(improvement):.1f}%")
    else:
        print("⚖️  性能相當")
    
    # 檢查插件載入一致性
    standard_plugins = set(standard_result['plugin_list'])
    optimized_plugins = set(optimized_result['plugin_list'])
    
    if standard_plugins == optimized_plugins:
        print("✅ 插件載入結果一致")
    else:
        missing_in_optimized = standard_plugins - optimized_plugins
        extra_in_optimized = optimized_plugins - standard_plugins
        
        if missing_in_optimized:
            print(f"⚠️  優化管理器缺少插件: {missing_in_optimized}")
        if extra_in_optimized:
            print(f"ℹ️  優化管理器額外插件: {extra_in_optimized}")


async def main():
    """主測試函數"""
    print("🧪 插件載入性能測試")
    print("此測試將比較標準和優化插件管理器的載入性能")
    
    try:
        # 測試標準插件管理器
        standard_result = test_standard_plugin_loading()
        
        # 小延遲確保測試分離
        await asyncio.sleep(0.5)
        
        # 測試優化插件管理器  
        optimized_result = await test_optimized_plugin_loading()
        
        # 比較結果
        compare_results(standard_result, optimized_result)
        
        print("\n🏁 測試完成!")
        
    except Exception as e:
        logger.error(f"測試失敗: {e}")
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 運行異步測試
    asyncio.run(main())