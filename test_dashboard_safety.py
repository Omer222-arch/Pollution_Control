"""
Unit tests for dashboard safety functions.

Run with: python test_dashboard_safety.py
"""

import sys
from pathlib import Path

# Import the dashboard functions
sys.path.insert(0, str(Path(__file__).parent))
from dashboard import safe_construct_path, validate_directory


def test_safe_construct_path():
    """Test path construction with edge cases."""
    base = Path(__file__).parent / "test_dir"
    base.mkdir(exist_ok=True)
    
    test_cases = [
        # (pollutant, filename, expected_is_none, description)
        (None, "file.csv", True, "None pollutant"),
        ("", "file.csv", True, "Empty string pollutant"),
        ("   ", "file.csv", True, "Whitespace-only pollutant"),
        (123, "file.csv", True, "Non-string pollutant"),
        ("PM2.5", "model.csv", False, "Valid pollutant with dot"),
        ("NO2", "results.json", False, "Valid simple pollutant"),
        ("../../etc/passwd", "file.csv", True, "Path traversal attempt"),
    ]
    
    print("Testing safe_construct_path():")
    for pollutant, filename, should_be_none, desc in test_cases:
        result = safe_construct_path(base, pollutant, filename)
        is_none = result is None
        status = "✓" if is_none == should_be_none else "✗"
        print(f"  {status} {desc}: {repr(pollutant)} → {result}")
        assert is_none == should_be_none, f"Failed: {desc}"
    
    # Cleanup
    base.rmdir()
    print("\n✓ All safe_construct_path() tests passed\n")


def test_validate_directory():
    """Test directory validation."""
    test_dir = Path(__file__).parent / "test_validate"
    test_dir.mkdir(exist_ok=True)
    test_file = test_dir / "test.txt"
    test_file.write_text("test")
    
    print("Testing validate_directory():")
    
    # Valid directory
    result = validate_directory(test_dir, "test")
    print(f"  ✓ Valid directory: {result}")
    assert result is True
    
    # Non-existent directory
    result = validate_directory(test_dir / "nonexistent", "test")
    print(f"  ✓ Non-existent directory: {result}")
    assert result is False
    
    # File instead of directory
    result = validate_directory(test_file, "test")
    print(f"  ✓ File path (not dir): {result}")
    assert result is False
    
    # Non-Path object
    result = validate_directory("/some/string/path", "test")
    print(f"  ✓ String path (not Path): {result}")
    assert result is False
    
    # Cleanup
    test_file.unlink()
    test_dir.rmdir()
    print("\n✓ All validate_directory() tests passed\n")


def test_none_handling():
    """Test that None is handled gracefully throughout."""
    print("Testing None handling in path operations:")
    
    # Test that None doesn't cause TypeError
    base = Path(__file__).parent
    result = safe_construct_path(base, None, "file.csv")
    print(f"  ✓ safe_construct_path(base, None, 'file.csv') = {result}")
    assert result is None
    
    # Test with invalid types
    result = safe_construct_path(base, 123, "file.csv")
    print(f"  ✓ safe_construct_path(base, 123, 'file.csv') = {result}")
    assert result is None
    
    print("\n✓ All None handling tests passed\n")


if __name__ == "__main__":
    print("=" * 70)
    print("DASHBOARD SAFETY TEST SUITE")
    print("=" * 70 + "\n")
    
    try:
        test_safe_construct_path()
        test_validate_directory()
        test_none_handling()
        
        print("=" * 70)
        print("ALL TESTS PASSED ✓")
        print("=" * 70)
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
