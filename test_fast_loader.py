#!/usr/bin/env python3
"""
Test fast plugin loader basic functionality
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import asyncio
import time

try:
    from core.fast_plugin_loader import create_optimized_plugin_manager, LoadingStrategy
    print("Import success: FastPluginLoader modules")
except ImportError as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


async def test_basic_functionality():
    """Test basic functionality of optimized plugin manager"""
    print("Testing optimized plugin manager basic functionality")
    
    try:
        # Create simple strategy
        strategy = LoadingStrategy(
            use_cache=False,  # Disable cache for simple test
            parallel_loading=False,  # Disable parallel for simple test
            lazy_initialization=False  # Disable lazy for simple test
        )
        
        # Create manager
        manager = create_optimized_plugin_manager(strategy)
        print("Created optimized plugin manager")
        
        # Simple sync initialization test
        start_time = time.time()
        
        # Try the sync method first
        try:
            manager.initialize()  # Try sync method
            sync_time = time.time() - start_time
            print(f"Sync initialization completed in {sync_time:.3f}s")
            
            plugins = manager.get_all_plugins()
            print(f"Found {len(plugins)} plugins: {list(plugins.keys())}")
            
        except Exception as sync_error:
            print(f"Sync initialization failed: {sync_error}")
            
            # Try async method
            start_time = time.time()
            success, message, stats = await manager.initialize_async()
            async_time = time.time() - start_time
            
            print(f"Async initialization: {success}")
            print(f"Message: {message}")
            print(f"Time: {async_time:.3f}s")
            print(f"Stats: {stats}")
            
            plugins = manager.get_all_plugins()
            print(f"Found {len(plugins)} plugins: {list(plugins.keys())}")
        
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("Fast Plugin Loader Basic Test")
    
    # Run basic test
    success = asyncio.run(test_basic_functionality())
    
    if success:
        print("Test completed successfully")
    else:
        print("Test failed")
        sys.exit(1)


if __name__ == "__main__":
    main()