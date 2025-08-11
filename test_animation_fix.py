#!/usr/bin/env python3
"""
測試動畫修復
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_animation_manager():
    """測試動畫管理器"""
    print("Testing animation manager fix")
    print("=" * 50)
    
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QSequentialAnimationGroup, QPropertyAnimation, QRect
        from ui.animation_effects import animation_manager
        
        # 創建應用程式（如果不存在）
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 創建一個動畫組來測試
        animation_group = QSequentialAnimationGroup()
        
        # 創建兩個子動畫
        anim1 = QPropertyAnimation()
        anim1.setDuration(100)
        
        anim2 = QPropertyAnimation()
        anim2.setDuration(150)
        
        animation_group.addAnimation(anim1)
        animation_group.addAnimation(anim2)
        
        print(f"Original durations: {anim1.duration()}, {anim2.duration()}")
        print(f"Animation group total duration: {animation_group.duration()}")
        
        # 測試註冊動畫（這裡之前會崩潰）
        animation_manager.register_animation("test_group", animation_group)
        
        print(f"After registration durations: {anim1.duration()}, {anim2.duration()}")
        print("[PASS] Animation group registration successful")
        
        # 測試單個動畫
        single_anim = QPropertyAnimation()
        single_anim.setDuration(200)
        
        print(f"Single animation original duration: {single_anim.duration()}")
        animation_manager.register_animation("test_single", single_anim)
        print(f"Single animation after registration: {single_anim.duration()}")
        print("[PASS] Single animation registration successful")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Animation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函數"""
    print("Animation Fix Test")
    print("=" * 50)
    
    success = test_animation_manager()
    
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    if success:
        print("[PASS] Animation fix successful")
        print("The setDuration issue has been resolved")
        return True
    else:
        print("[FAIL] Animation fix failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)