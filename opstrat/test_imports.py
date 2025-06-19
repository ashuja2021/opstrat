#!/usr/bin/env python3
"""
Test script to verify all imports are working correctly
"""

print("Testing imports...")

try:
    import numpy as np
    print("✓ numpy imported successfully")
except ImportError as e:
    print(f"✗ numpy import failed: {e}")

try:
    import matplotlib.pyplot as plt
    print("✓ matplotlib imported successfully")
except ImportError as e:
    print(f"✗ matplotlib import failed: {e}")

try:
    import seaborn as sns
    print("✓ seaborn imported successfully")
except ImportError as e:
    print(f"✗ seaborn import failed: {e}")

try:
    import yfinance as yf
    print("✓ yfinance imported successfully")
except ImportError as e:
    print(f"✗ yfinance import failed: {e}")

try:
    from scipy.stats import norm
    print("✓ scipy imported successfully")
except ImportError as e:
    print(f"✗ scipy import failed: {e}")

try:
    import opstrat as op
    print("✓ opstrat imported successfully")
except ImportError as e:
    print(f"✗ opstrat import failed: {e}")

print("\nAll import tests completed!") 