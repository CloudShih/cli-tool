#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple plugin loading performance test
"""

import asyncio
import time
import logging
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set proper encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

try:
    from core.plugin_manager import PluginManager
    from core.fast_plugin_loader import create_optimized_plugin_manager, LoadingStrategy
    print("Successfully imported plugin manager modules")
except ImportError as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


def test_standard_loading():
    """Test standard plugin manager loading performance"""
    print("\n" + "="*50)
    print("Testing Standard Plugin Manager")
    print("="*50)
    
    start_time = time.time()
    
    try:
        # Create standard plugin manager
        manager = PluginManager()
        
        # Initialize
        manager.initialize()
        
        end_time = time.time()
        loading_time = end_time - start_time
        
        # Get results
        plugins = manager.get_all_plugins()
        available_plugins = manager.get_available_plugins()
        
        print(f"Loading time: {loading_time:.3f} seconds")
        print(f"Total plugins: {len(plugins)}")
        print(f"Available plugins: {len(available_plugins)}")
        print(f"Plugin list: {list(plugins.keys())}")
        
        return {
            'loading_time': loading_time,
            'total_plugins': len(plugins),
            'available_plugins': len(available_plugins),
            'plugin_list': list(plugins.keys())
        }
    except Exception as e:
        print(f"Standard loading failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_optimized_loading():
    """Test optimized plugin manager loading performance"""
    print("\n" + "="*50)
    print("Testing Optimized Plugin Manager")
    print("="*50)
    
    start_time = time.time()
    
    try:
        # Create loading strategy
        strategy = LoadingStrategy(
            use_cache=True,
            parallel_loading=True,
            max_workers=4,
            lazy_initialization=True,
            preload_critical=True,
            skip_tool_checks=False,
            cache_duration_hours=24
        )
        
        # Create optimized plugin manager
        manager = create_optimized_plugin_manager(strategy)
        
        # Async initialization
        success, message, stats = await manager.initialize_async()
        
        end_time = time.time()
        loading_time = end_time - start_time
        
        # Get results
        plugins = manager.get_all_plugins()
        available_plugins = manager.get_available_plugins()
        
        print(f"Loading time: {loading_time:.3f} seconds")
        print(f"Total plugins: {len(plugins)}")
        print(f"Available plugins: {len(available_plugins)}")
        print(f"Plugin list: {list(plugins.keys())}")
        print(f"Success: {success}")
        print(f"Message: {message}")
        print(f"Stats: {stats}")
        
        return {
            'loading_time': loading_time,
            'total_plugins': len(plugins),
            'available_plugins': len(available_plugins),
            'plugin_list': list(plugins.keys()),
            'success': success,
            'message': message,
            'stats': stats
        }
    except Exception as e:
        print(f"Optimized loading failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def compare_results(standard, optimized):
    """Compare loading results"""
    print("\n" + "="*50)
    print("Performance Comparison")
    print("="*50)
    
    if not standard or not optimized:
        print("Cannot compare - one of the tests failed")
        return
    
    standard_time = standard['loading_time']
    optimized_time = optimized['loading_time']
    
    improvement = ((standard_time - optimized_time) / standard_time) * 100
    
    print(f"Standard manager: {standard_time:.3f} seconds")
    print(f"Optimized manager: {optimized_time:.3f} seconds")
    print(f"Performance improvement: {improvement:+.1f}%")
    
    if improvement > 0:
        print(f"Optimized manager is {improvement:.1f}% faster")
    elif improvement < 0:
        print(f"Optimized manager is {abs(improvement):.1f}% slower")
    else:
        print("Performance is equivalent")
    
    # Check plugin consistency
    standard_plugins = set(standard['plugin_list'])
    optimized_plugins = set(optimized['plugin_list'])
    
    if standard_plugins == optimized_plugins:
        print("Plugin loading results are consistent")
    else:
        print("WARNING: Plugin loading results differ")
        missing = standard_plugins - optimized_plugins
        extra = optimized_plugins - standard_plugins
        if missing:
            print(f"Missing in optimized: {missing}")
        if extra:
            print(f"Extra in optimized: {extra}")


async def main():
    """Main test function"""
    print("Plugin Loading Performance Test")
    print("Comparing standard and optimized plugin managers")
    
    try:
        # Test standard plugin manager
        standard_result = test_standard_loading()
        
        # Small delay to separate tests
        await asyncio.sleep(0.5)
        
        # Test optimized plugin manager  
        optimized_result = await test_optimized_loading()
        
        # Compare results
        compare_results(standard_result, optimized_result)
        
        print("\nTest completed!")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())