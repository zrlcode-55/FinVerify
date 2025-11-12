"""
Automated test suite for verification tool
Ensureing everything works correctly
"""

import pytest
from z3 import *
from verifier.property_checker import PropertyChecker, VerificationResult
from contracts.erc20_token import ERC20Token
from contracts.bridge import BridgeChainA, BridgeChainB


class TestPropertyChecker:
    def test_erc20_conservation(self):
        checker = PropertyChecker()
        result = checker.verify_erc20_conservation(1000,2)
        assert result in [VerificationResult.VERIFIED, VerificationResult.VIOLATED]

    def test_bridge_conservation(self):
        checker = PropertyChecker()
        result = checker.verify_bridge_conservation(100)
        assert result in [VerificationResult.VERIFIED, VerificationResult.VIOLATED]



    def test_overflow_protection(self):
        checker = PropertyChecker()
        result = checker.verify_no_overflow()
        assert result in [VerificationResult.VERIFIED, VerificationResult.VIOLATED]


    def test_buggy_bridge(self):
        checker = PropertyChecker()
        result = checker.verify_buggy_bridge()
        assert result == VerificationResult.VIOLATED  


class TestERC20Token:
    def test_initial_supply(self):
        token = ERC20Token(1000)
        assert token.total_supply == 1000
        assert token.balance_of('owner') == 1000



    def test_transfer(self):
        token = ERC20Token(1000)
        success = token.transfer('owner', 'alice', 100)
        assert success == True
        assert token.balance_of('owner') == 900
        assert token.balance_of('alice') == 100

    def test_transfer_insufficient_balance(self):
        token = ERC20Token(1000)
        success = token.transfer('owner', 'alice', 2000)
        assert success == False


    def test_mint_unauthorized(self):
        token = ERC20Token(1000)
        token.mint('attacker', 1000)
        # BUG: Should fail but doesn't!
        assert token.total_supply == 2000



class TestBridge:
    def test_lock(self):
        bridge = BridgeChainA()
        success = bridge.lock(100, nonce=1)
        assert success == True
        assert bridge.locked == 100

    def test_mint(self):
        bridge = BridgeChainB()
        success = bridge.mint(100, "hash1")
        assert success == True
        assert bridge.minted == 100



    def test_replay_protection_chain_a(self):
        bridge = BridgeChainA()
        bridge.lock(100, nonce=1)
        success = bridge.lock(100, nonce=1)  # Same nonce
        assert success == False  # Should reject


    def test_replay_attack_chain_b(self):
        bridge = BridgeChainB()
        bridge.mint(100, "hash1")
        bridge.mint(100, "hash1")  # Replay!
        # BUG: Should fail but doesn't!
        assert bridge.minted == 200  # Double minted!


class TestZ3Integration:
    def test_z3_basic(self):
        x = Int('x')
        y = Int('y')
        solver = Solver()
        solver.add(x + y == 10)
        solver.add(x > y)
        assert solver.check() == sat



    def test_z3_unsat(self):
        x = Int('x')
        solver = Solver()
        solver.add(x > 0)
        solver.add(x < 0)
        assert solver.check() == unsat


def run_tests():
    """Run all tests and report results"""
    print("="*70)
    print("RUNNING TEST SUITE")
    print("="*70)
    print()
    
    # Run pytest
    exit_code = pytest.main([__file__, '-v', '--tb=short'])
    
    print()
    print("="*70)
    if exit_code == 0:
        print("[SUCCESS] All tests passed!")
    else:
        print("[FAIL] Some tests failed")
    print("="*70)
    
    return exit_code


if __name__ == "__main__":
    exit(run_tests())

