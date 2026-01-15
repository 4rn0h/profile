# debug_admin.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# First check the imports work
try:
    from admin import admin_bp
    print("✅ Successfully imported admin_bp")
    
    # Check what routes are registered
    print("\nChecking admin_bp routes:")
    for rule in admin_bp.deferred_functions:
        print(f"  - {rule}")
        
except Exception as e:
    print(f"❌ Error importing admin_bp: {e}")
    import traceback
    traceback.print_exc()