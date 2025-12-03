"""
Financial Property Checker using Z3 SMT Solver
Verifies critical financial properties in smart contracts

Author note: this implements the verification logic we discussed in class
"""

from z3 import *
from typing import List, Dict, Tuple
from enum import Enum

# using Z3 because its the most mature SMT solver and has good python bindings
# took me a while to figure out the right way to encode constraints


class VerificationResult(Enum):
    VERIFIED = "[VERIFIED]"
    VIOLATED = "[VIOLATED]"
    UNKNOWN = "[UNKNOWN]"  # sometimes solver times out


class PropertyChecker:
    """Core verification engine for financial properties"""
    
    def __init__(self, timeout_ms=30000):
        self.solver = Solver()
        self.solver.set("timeout", timeout_ms)  # 30 seconds should be enough for most properties
        self.violations = []   # keep track of found bugs

    def reset(self):
        """Reset the solver for a new verification"""
        self.solver.reset()
        self.violations = []


    def verify_erc20_conservation(self, initial_supply: int, num_operations: int = 3):
        """
        Verify ERC-20 Token Conservation Property:
        "Total supply must remain constant through transfers"
        
        This is a CRITICAL financial property - if violated, tokens can be
        created or destroyed, leading to financial loss.
        """
        print("\n" + "="*70)
        print("EXPERIMENT 1: ERC-20 Token Conservation")
        print("="*70)
        print(f"Initial Supply: {initial_supply} tokens")
        print(f"Operations: {num_operations} transfers")
        print()
        
        # State variables
        total_supply = Int('total_supply')
        
        # Create balance variables for multiple accounts
        balances = [Int(f'balance_{i}') for i in range(num_operations + 1)]
        
        # Initial constraints
        self.solver.add(total_supply == initial_supply)
        self.solver.add(total_supply > 0)
        
        # All balances start non-negative  (basic sanity check)
        for bal in balances:
            self.solver.add(bal >= 0)  # cant have negative tokens!
        
        # Initial distribution: all tokens in first account
        self.solver.add(balances[0] == total_supply)
        for i in range(1, len(balances)):
            self.solver.add(balances[i] == 0)
        
        # Simulate transfers
        transfer_amounts = [Int(f'transfer_{i}') for i in range(num_operations)]
        
        running_balances = [balances[0]]
        for i, amount in enumerate(transfer_amounts):
            self.solver.add(amount > 0)  # Transfers must be positive (no zero or negative transfers)
            
            # Source has enough balance
            self.solver.add(running_balances[i] >= amount)
            
            # After transfer: source decreases, dest increases
            new_source = running_balances[i] - amount
            new_dest = balances[i + 1] + amount
            
            running_balances.append(new_source)
            self.solver.add(new_dest >= 0)
        
        # CRITICAL PROPERTY: Total supply conservation
        # Sum of all balances must equal initial supply
        balance_sum = sum(running_balances)
        
        print("Checking: SUM(balances) == initial_supply")
        
        # Try to find a violation (negation approach from class)
        self.solver.add(balance_sum != total_supply)
        
        result = self.solver.check()
        
        if result == sat:
            print(f"\n{VerificationResult.VIOLATED.value}")
            print("\n[WARNING] CRITICAL BUG FOUND: Token conservation violated!")
            model = self.solver.model()
            print("\nCounterexample:")
            print(f"  Total Supply: {model.eval(total_supply)}")
            print(f"  Sum of Balances: {model.eval(balance_sum)}")
            for i, bal in enumerate(running_balances):
                print(f"  Account {i}: {model.eval(bal)} tokens")
            return VerificationResult.VIOLATED
        elif result == unsat:
            print(f"\n{VerificationResult.VERIFIED.value}")
            print("\n[SUCCESS] Token conservation PROVEN: Total supply remains constant!")
            print("   Property holds for all possible execution paths.")
            return VerificationResult.VERIFIED
        else:
            print(f"\n{VerificationResult.UNKNOWN.value}")
            return VerificationResult.UNKNOWN


    def verify_bridge_conservation(self, initial_amount: int):
        """
        Verify Cross-Chain Bridge Conservation:
        "Tokens locked on Chain A must equal tokens minted on Chain B"
        
        This is the CORE security property for bridges.
        Violations led to $2.8B in losses.
        """
        print("\n" + "="*70)
        print("EXPERIMENT 2: Cross-Chain Bridge Conservation")
        print("="*70)
        print(f"Initial Bridge Amount: {initial_amount} tokens")
        print()
        
        self.reset()
        
        # Chain A state
        locked_A = Int('locked_A')
        
        # Chain B state  
        minted_B = Int('minted_B')
        
        # Nonce for replay protection
        nonce = Int('nonce')
        processed = Bool('processed')
        
        # Initial state: nothing locked or minted
        self.solver.add(locked_A >= 0)
        self.solver.add(minted_B >= 0)
        self.solver.add(nonce == 0)
        self.solver.add(processed == False)
        
        # Operation 1: Lock tokens on Chain A
        amount1 = Int('amount1')
        locked_A_after_lock = Int('locked_A_after_lock')
        
        self.solver.add(amount1 == initial_amount)
        self.solver.add(amount1 > 0)
        self.solver.add(locked_A_after_lock == locked_A + amount1)
        
        # Operation 2: Mint on Chain B (should equal locked amount)
        amount2 = Int('amount2')
        minted_B_after_mint = Int('minted_B_after_mint')
        
        self.solver.add(amount2 == amount1)  # Same amount
        self.solver.add(minted_B_after_mint == minted_B + amount2)
        
        # CRITICAL PROPERTY: Conservation
        print("Checking: locked(Chain A) == minted(Chain B)")
        
        # Try to violate the invariant
        self.solver.add(locked_A_after_lock != minted_B_after_mint)
        
        result = self.solver.check()
        
        if result == sat:
            print(f"\n{VerificationResult.VIOLATED.value}")
            print("\n[WARNING] CRITICAL BUG FOUND: Bridge conservation violated!")
            model = self.solver.model()
            print("\nCounterexample:")
            print(f"  Locked on Chain A: {model.eval(locked_A_after_lock)} tokens")
            print(f"  Minted on Chain B: {model.eval(minted_B_after_mint)} tokens")
            print(f"  Difference: {model.eval(locked_A_after_lock - minted_B_after_mint)} tokens")
            print("\n[MONEY] This represents STOLEN VALUE!")
            return VerificationResult.VIOLATED
        elif result == unsat:
            print(f"\n{VerificationResult.VERIFIED.value}")
            print("\n[SUCCESS] Bridge conservation PROVEN: locked == minted!")
            print("   This bridge is safe from conservation violations.")
            return VerificationResult.VERIFIED
        else:
            print(f"\n{VerificationResult.UNKNOWN.value}")
            return VerificationResult.UNKNOWN


    def verify_no_overflow(self, max_value: int = 2**256 - 1):
        """
        Verify Arithmetic Safety:
        "No integer overflows in token operations"
        
        Integer overflows have led to major exploits (e.g., BECToken hack)
        """
        print("\n" + "="*70)
        print("EXPERIMENT 3: Integer Overflow Protection")
        print("="*70)
        print(f"Max Value: {max_value}")
        print()
        
        self.reset()
        
        # Account balances
        balance1 = Int('balance1')
        balance2 = Int('balance2')
        transfer_amount = Int('transfer_amount')
        
        # Constraints
        self.solver.add(balance1 >= 0)
        self.solver.add(balance2 >= 0)
        self.solver.add(transfer_amount > 0)
        self.solver.add(balance1 >= transfer_amount)  # Sufficient balance
        
        # After transfer
        new_balance2 = balance2 + transfer_amount
        
        # Check for overflow
        print("Checking: balance + amount <= MAX_VALUE")
        
        # Try to find an overflow
        self.solver.add(new_balance2 > max_value)
        
        result = self.solver.check()
        
        if result == sat:
            print(f"\n{VerificationResult.VIOLATED.value}")
            print("\n[WARNING] CRITICAL BUG FOUND: Integer overflow possible!")
            model = self.solver.model()
            print("\nCounterexample:")
            print(f"  Balance Before: {model.eval(balance2)}")
            print(f"  Transfer Amount: {model.eval(transfer_amount)}")
            print(f"  Balance After: {model.eval(new_balance2)}")
            print(f"  Max Allowed: {max_value}")
            print("\n[WARNING] This overflow could be exploited!")
            return VerificationResult.VIOLATED
        elif result == unsat:
            print(f"\n{VerificationResult.VERIFIED.value}")
            print("\n[SUCCESS] No overflow possible: All operations are safe!")
            print("   Arithmetic is protected against overflow attacks.")
            return VerificationResult.VERIFIED
        else:
            print(f"\n{VerificationResult.UNKNOWN.value}")
            return VerificationResult.UNKNOWN


    def verify_buggy_bridge(self):
        """
        Verify a BUGGY bridge to demonstrate bug finding capability
        BUG: Double minting without replay protection
        """
        print("\n" + "="*70)
        print("EXPERIMENT 4: Buggy Bridge Detection")
        print("="*70)
        print("Testing bridge with KNOWN vulnerability...")
        print()
        
        self.reset()
        
        locked_A = Int('locked_A')
        minted_B = Int('minted_B')
        
        # Initial state
        self.solver.add(locked_A == 0)
        self.solver.add(minted_B == 0)
        
        # Operation 1: Lock 1000 tokens
        amount = 1000
        locked_A_1 = Int('locked_A_1')
        self.solver.add(locked_A_1 == locked_A + amount)
        
        # Operation 2: Mint 1000 tokens (correct)
        minted_B_1 = Int('minted_B_1')
        self.solver.add(minted_B_1 == minted_B + amount)
        
        # Operation 3: BUG - Mint AGAIN with same proof (no replay protection!)
        minted_B_2 = Int('minted_B_2')
        self.solver.add(minted_B_2 == minted_B_1 + amount)  # Double mint!
        
        # Check if invariant can be violated
        print("Checking: locked(Chain A) == minted(Chain B)")
        print("Note: Bridge allows replay attacks...")
        
        # Try to show violation is possible
        self.solver.add(locked_A_1 != minted_B_2)
        
        result = self.solver.check()
        
        if result == sat:
            print(f"\n{VerificationResult.VIOLATED.value}")
            print("\n[EXPLOIT FOUND] Replay Attack Vulnerability!")
            model = self.solver.model()
            print("\nAttack Sequence:")
            print(f"  Step 1: Lock {amount} tokens on Chain A")
            print(f"          locked_A = {model.eval(locked_A_1)}")
            print(f"  Step 2: Mint {amount} tokens on Chain B")
            print(f"          minted_B = {model.eval(minted_B_1)}")
            print(f"  Step 3: Replay same mint transaction!")
            print(f"          minted_B = {model.eval(minted_B_2)}")
            print(f"\n[MONEY] Attacker Profit: {model.eval(minted_B_2 - locked_A_1)} tokens")
            print(f"\nROOT CAUSE: Missing replay protection")
            print(f"FIX: Add nonce tracking: require(!processed[messageHash])")
            return VerificationResult.VIOLATED
        else:
            print(f"\n{VerificationResult.VERIFIED.value}")
            print("No violation found (unexpected!)")
            return VerificationResult.VERIFIED



def generate_summary_report(results: List[Tuple[str, VerificationResult]]):
    """Generate a summary report of all verification results"""
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY REPORT")
    print("="*70)
    print()
    
    total = len(results)
    verified = sum(1 for _, r in results if r == VerificationResult.VERIFIED)
    violated = sum(1 for _, r in results if r == VerificationResult.VIOLATED)
    
    print(f"Total Properties Checked: {total}")
    print(f"  [OK] Verified: {verified}")
    print(f"  [FAIL] Violated: {violated}")
    print()
    
    print("Detailed Results:")
    print("-" * 70)
    for name, result in results:
        status = result.value
        print(f"{status} {name}")
    print()
    
    if violated > 0:
        print("[WARNING] CRITICAL: Vulnerabilities found! Review counterexamples above.")
    else:
        print("[SUCCESS] All properties verified! Contract appears secure.")
    
    print("="*70)

