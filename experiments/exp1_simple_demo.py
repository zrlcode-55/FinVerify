"""
SIMPLE DEMO: Quick 2-minute demonstration of formal verification

This is a simplified version that shows the core concept clearly.
Run this FIRST to see verification in action!
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from z3 import *


def demo_token_conservation():
    """
    Demonstrates proving that token transfers cannot create or destroy tokens.
    This is the CORE financial property that prevents theft.
    """
    print("\n" + "="*60)
    print("SIMPLE DEMO: Proving Token Conservation")
    print("="*60)
    print()
    
    # Create Z3 solver
    solver = Solver()
    
    # Variables representing token balances
    alice_before = Int('alice_before')
    bob_before = Int('bob_before')
    transfer_amount = Int('transfer_amount')
    
    # After transfer
    alice_after = Int('alice_after')
    bob_after = Int('bob_after')
    
    # Initial constraints
    print("Setting up the problem...")
    print("  - Alice and Bob start with some tokens")
    print("  - Alice transfers some amount to Bob")
    print("  - Checking: Can total supply change?")
    print()
    
    solver.add(alice_before >= 0)
    solver.add(bob_before >= 0)
    solver.add(transfer_amount > 0)
    solver.add(transfer_amount <= alice_before)  # Alice must have enough
    
    # Transfer logic
    solver.add(alice_after == alice_before - transfer_amount)
    solver.add(bob_after == bob_before + transfer_amount)
    
    # Try to VIOLATE conservation
    # "Can total before != total after?"
    total_before = alice_before + bob_before
    total_after = alice_after + bob_after
    
    solver.add(total_before != total_after)
    
    print("Asking Z3: Can total supply change during transfer?")
    result = solver.check()
    
    if result == unsat:
        print("\nResult: UNSAT (impossible!)")
        print()
        print("[PROVEN] Token conservation is GUARANTEED!")
        print("   Tokens cannot be created or destroyed in transfers.")
        print("   This is a mathematical certainty, not just a test.")
    else:
        print("\nResult: SAT (possible!)")
        print("[BUG] Bug found!")
        print("Model:", solver.model())


def demo_buggy_contract():
    """
    Demonstrates finding a bug in a poorly designed contract
    """
    print("\n" + "="*60)
    print("SIMPLE DEMO: Finding a Bug")
    print("="*60)
    print()
    
    solver = Solver()
    
    # Buggy mint function that doesn't check authorization
    minted = Int('minted')
    user_request = Int('user_request')
    
    print("Analyzing a buggy mint function...")
    print("  - Function: mint(amount)")
    print("  - Bug: No authorization check!")
    print("  - Checking: Can user mint infinite tokens?")
    print()
    
    solver.add(minted >= 0)
    solver.add(user_request > 0)
    
    # Buggy logic: Just mint whatever is requested!
    new_minted = minted + user_request
    
    # Check if user can mint 1 million tokens
    solver.add(new_minted >= 1000000)
    
    print("Asking Z3: Can user mint 1,000,000 tokens without authorization?")
    result = solver.check()
    
    if result == sat:
        print("\nResult: SAT (possible!)")
        print()
        print("[CRITICAL BUG FOUND!]")
        model = solver.model()
        print(f"   User can request: {model.eval(user_request)} tokens")
        print(f"   Total minted: {model.eval(new_minted)} tokens")
        print()
        print("   FIX: Add authorization: require(msg.sender == owner)")
    else:
        print("\nResult: UNSAT")
        print("[No bug found]")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("FinVerify: Formal Verification Made Simple")
    print("Using Z3 SMT Solver")
    print("="*60)
    
    demo_token_conservation()
    demo_buggy_contract()
    
    print("\n" + "="*60)
    print("KEY TAKEAWAYS")
    print("="*60)
    print()
    print("1. Z3 can PROVE properties (not just test them)")
    print("2. Automatically finds bugs when properties violated")
    print("3. Provides mathematical guarantees")
    print("4. Fast and automated")
    print()
    print("This is REAL formal verification!")
    print("="*60)
    print()

