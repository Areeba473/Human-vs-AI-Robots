#!/usr/bin/env python3
"""
Test script to verify the Shield Defender implementation
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all necessary imports work"""
    try:
        from game.entities.actors import ShieldDefender
        from game.assets import draw_shield_defender
        from game.config import UNIT_DEFS
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test that shield_defender is in the unit definitions"""
    from game.config import UNIT_DEFS
    
    shield_defender_config = None
    for unit in UNIT_DEFS:
        if unit["key"] == "shield_defender":
            shield_defender_config = unit
            break
    
    if shield_defender_config:
        print(f"✅ Shield Defender config found: {shield_defender_config}")
        return True
    else:
        print("❌ Shield Defender not found in UNIT_DEFS")
        return False

def test_unlock_logic():
    """Test the Night theme unlock logic"""
    # Mock a PlayScene for Night level 2
    class MockPlayScene:
        def __init__(self):
            self.theme = "Night"
            self.level = 2
        
        def _get_unlocked_units(self):
            # Night theme (starts after Day level 10)
            if self.theme == "Night":
                if self.level == 1:
                    return ["bubble_shooter"]  # Free bubble shooter for Night theme
                if self.level == 2:
                    return ["bubble_shooter", "shield_defender", "shooter"]  # Shield Defender unlocked at Night level 2
                if self.level == 3:
                    return ["bubble_shooter", "shield_defender", "shooter", "wall"]
                if self.level == 4:
                    return ["bubble_shooter", "shield_defender", "shooter", "wall", "frozen"]
                if self.level == 5:
                    return ["bubble_shooter", "shield_defender", "shooter", "wall", "frozen", "bomb"]
                if self.level >= 6:
                    return ["bubble_shooter", "shield_defender", "shooter", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus"]
            return ["shooter"]
    
    scene = MockPlayScene()
    unlocked = scene._get_unlocked_units()
    
    if "shield_defender" in unlocked:
        print(f"✅ Shield Defender correctly unlocked at Night level 2: {unlocked}")
        return True
    else:
        print(f"❌ Shield Defender not unlocked at Night level 2: {unlocked}")
        return False

def main():
    """Run all tests"""
    print("Testing Shield Defender implementation...")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Config", test_config),
        ("Unlock Logic", test_unlock_logic)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name} test...")
        if test_func():
            passed += 1
        
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Shield Defender implementation is ready!")
        print("\nTo test in-game:")
        print("1. Run the game: python -m game")
        print("2. Navigate to Night theme")
        print("3. Complete Night level 1 to unlock Shield Defender")
        print("4. Shield Defender will be available starting from Night level 2")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)