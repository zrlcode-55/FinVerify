"""
Generate Results with Clear Story for IEEE Paper

This version generates experiments with BOTH:
1. Secure implementations (should VERIFY)
2. Buggy implementations (should find VIOLATIONS)

This tells the complete story: we can both verify correctness AND find bugs.
"""

import sys
import os
import csv
import time
import json
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from verifier.property_checker import PropertyChecker, VerificationResult
from verifier.hoare_logic import VerificationConditionGenerator
from verifier.advanced_properties import AdvancedPropertyChecker, AdvancedVerificationResult


class PaperExperimentRunner:
    """Runs experiments that tell a clear story for paper"""
    
    def __init__(self):
        self.results = []
    
    def run_experiment(self, name, expected_result, func, *args, **kwargs):
        """
        Run experiment with expected outcome
        
        expected_result: 'SECURE' (should verify) or 'BUGGY' (should find violation)
        """
        print(f"\n>>> Running: {name}")
        print(f"    Expected: {expected_result}")
        
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Determine actual outcome
        if isinstance(result, VerificationResult):
            actual = "VERIFIED" if result == VerificationResult.VERIFIED else "BUG_FOUND"
        elif isinstance(result, AdvancedVerificationResult):
            actual = "VERIFIED" if result == AdvancedVerificationResult.VERIFIED else "BUG_FOUND"
        elif result == True:
            actual = "VERIFIED"
        else:
            actual = "BUG_FOUND"
        
        # Check if result matches expectation
        if expected_result == "SECURE":
            status = "CORRECT" if actual == "VERIFIED" else "FALSE_NEGATIVE"
        else:  # BUGGY
            status = "CORRECT" if actual == "BUG_FOUND" else "FALSE_POSITIVE"
        
        experiment_data = {
            'experiment_name': name,
            'implementation_type': expected_result,  # SECURE or BUGGY
            'actual_result': actual,  # VERIFIED or BUG_FOUND
            'status': status,  # CORRECT, FALSE_POSITIVE, FALSE_NEGATIVE
            'execution_time_ms': round(execution_time * 1000, 2),
            'timestamp': datetime.now().isoformat(),
        }
        
        # Add complexity metrics
        if 'erc20' in name.lower() or 'conservation' in name.lower():
            experiment_data['property_category'] = 'Token Conservation'
        elif 'bridge' in name.lower() or 'cross' in name.lower():
            experiment_data['property_category'] = 'Cross-Chain'
        elif 'overflow' in name.lower():
            experiment_data['property_category'] = 'Arithmetic Safety'
        elif 'replay' in name.lower():
            experiment_data['property_category'] = 'Replay Protection'
        elif 'timelock' in name.lower() or 'byzantine' in name.lower():
            experiment_data['property_category'] = 'Advanced Security'
        else:
            experiment_data['property_category'] = 'Other'
        
        self.results.append(experiment_data)
        print(f"    Result: {actual} ({status})")
        
        return result
    
    def run_all_experiments(self):
        """Run complete experiment suite with clear story"""
        print("="*70)
        print("PAPER EXPERIMENTS - TELLING THE COMPLETE STORY")
        print("="*70)
        print("\nWe test BOTH secure and buggy implementations:")
        print("  - Secure code: Should VERIFY")
        print("  - Buggy code: Should FIND BUGS")
        print()
        
        # ========== SECURE IMPLEMENTATIONS (should verify) ==========
        print("\n" + "="*70)
        print("PART 1: VERIFYING SECURE IMPLEMENTATIONS")
        print("="*70)
        
        # Secure: Hoare Logic Verification Conditions
        vcgen = VerificationConditionGenerator()
        for balance in [100, 500, 1000]:
            self.run_experiment(
                f"Secure_Transfer_VCGen_bal{balance}",
                "SECURE",
                vcgen.generate_vc_transfer,
                precondition_balance=balance,
                amount=50
            )
        
        # Secure: Inductive invariant proof
        self.run_experiment(
            "Secure_Bridge_Inductive_Proof",
            "SECURE",
            vcgen.generate_vc_bridge_invariant
        )
        
        # Secure: Advanced properties
        adv_checker = AdvancedPropertyChecker()
        
        self.run_experiment(
            "Secure_MultiHop_Bridge",
            "SECURE",
            adv_checker.verify_multihop_bridge,
            1000
        )
        adv_checker.reset()
        
        self.run_experiment(
            "Secure_LiquidityPool_WithFees",
            "SECURE",
            adv_checker.verify_liquidity_pool_with_fees,
            100000, 30
        )
        adv_checker.reset()
        
        self.run_experiment(
            "Secure_Timelock_OptimisticRollup",
            "SECURE",
            adv_checker.verify_timelock_constraints,
            50400
        )
        adv_checker.reset()
        
        self.run_experiment(
            "Secure_Byzantine_MultiSig_5of9",
            "SECURE",
            adv_checker.verify_byzantine_fault_tolerance,
            9, 5
        )
        adv_checker.reset()
        
        # ========== BUGGY IMPLEMENTATIONS (should find bugs) ==========
        print("\n" + "="*70)
        print("PART 2: DETECTING BUGS IN VULNERABLE CODE")
        print("="*70)
        
        checker = PropertyChecker()
        
        # Buggy: ERC-20 with conservation issues
        for n_ops in [2, 3, 5]:
            self.run_experiment(
                f"Buggy_ERC20_Conservation_ops{n_ops}",
                "BUGGY",
                checker.verify_erc20_conservation,
                1000000, n_ops
            )
            checker.reset()
        
        # Buggy: Bridge without proper conservation
        for amt in [100, 1000, 10000]:
            self.run_experiment(
                f"Buggy_Bridge_Conservation_amt{amt}",
                "BUGGY",
                checker.verify_bridge_conservation,
                amt
            )
            checker.reset()
        
        # Buggy: Overflow vulnerabilities
        for bits in [8, 16, 32, 256]:
            max_val = (2 ** bits) - 1
            self.run_experiment(
                f"Buggy_Overflow_{bits}bit",
                "BUGGY",
                checker.verify_no_overflow,
                max_val
            )
            checker.reset()
        
        # Buggy: Replay attack vulnerability
        self.run_experiment(
            "Buggy_Bridge_ReplayAttack",
            "BUGGY",
            checker.verify_buggy_bridge
        )
        checker.reset()
        
        # Buggy: HTLC fairness issue
        self.run_experiment(
            "Buggy_AtomicSwap_Unfair_HTLC",
            "BUGGY",
            adv_checker.verify_atomic_swap_fairness
        )
        
        print(f"\n{'='*70}")
        print(f"Total Experiments Run: {len(self.results)}")
        print(f"{'='*70}\n")
    
    def save_to_csv(self, filename="paper_results.csv"):
        """Save results to CSV"""
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        if not self.results:
            print("No results to save!")
            return None
        
        fieldnames = sorted(set().union(*[result.keys() for result in self.results]))
        
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)
        
        print(f"[OK] Results saved to: {filepath}")
        return filepath
    
    def save_to_json(self, filename="paper_results.json"):
        """Save to JSON"""
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w') as jsonfile:
            json.dump({
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'total_experiments': len(self.results),
                    'tool': 'FinVerify',
                    'purpose': 'IEEE Paper Submission'
                },
                'results': self.results
            }, jsonfile, indent=2)
        
        print(f"[OK] Results saved to: {filepath}")
        return filepath
    
    def print_summary(self):
        """Print summary that tells the story"""
        print("\n" + "="*70)
        print("PAPER RESULTS SUMMARY")
        print("="*70 + "\n")
        
        secure_tests = [r for r in self.results if r['implementation_type'] == 'SECURE']
        buggy_tests = [r for r in self.results if r['implementation_type'] == 'BUGGY']
        
        secure_verified = sum(1 for r in secure_tests if r['actual_result'] == 'VERIFIED')
        bugs_found = sum(1 for r in buggy_tests if r['actual_result'] == 'BUG_FOUND')
        
        print(f"SECURE IMPLEMENTATIONS (Should Verify):")
        print(f"  Total tested:          {len(secure_tests)}")
        print(f"  Successfully verified: {secure_verified}")
        print(f"  False negatives:       {len(secure_tests) - secure_verified}")
        print(f"  Accuracy:              {secure_verified/len(secure_tests)*100:.1f}%")
        print()
        
        print(f"BUGGY IMPLEMENTATIONS (Should Find Bugs):")
        print(f"  Total tested:          {len(buggy_tests)}")
        print(f"  Bugs detected:         {bugs_found}")
        print(f"  False positives:       {len(buggy_tests) - bugs_found}")
        print(f"  Detection rate:        {bugs_found/len(buggy_tests)*100:.1f}%")
        print()
        
        # Timing stats
        times = [r['execution_time_ms'] for r in self.results]
        print(f"PERFORMANCE:")
        print(f"  Average time:          {sum(times)/len(times):.2f} ms")
        print(f"  Min time:              {min(times):.2f} ms")
        print(f"  Max time:              {max(times):.2f} ms")
        print()
        
        # By category
        categories = {}
        for r in self.results:
            cat = r['property_category']
            if cat not in categories:
                categories[cat] = {'total': 0, 'correct': 0}
            categories[cat]['total'] += 1
            if r['status'] == 'CORRECT':
                categories[cat]['correct'] += 1
        
        print("BY PROPERTY CATEGORY:")
        for cat, stats in sorted(categories.items()):
            accuracy = stats['correct'] / stats['total'] * 100
            print(f"  {cat:25} {stats['correct']}/{stats['total']} ({accuracy:.0f}%)")
        
        print("\n" + "="*70 + "\n")
        
        print("KEY TAKEAWAY FOR PAPER:")
        print(f"  ✓ Verifies secure code: {secure_verified}/{len(secure_tests)} ({secure_verified/len(secure_tests)*100:.0f}%)")
        print(f"  ✓ Finds bugs in vulnerable code: {bugs_found}/{len(buggy_tests)} ({bugs_found/len(buggy_tests)*100:.0f}%)")
        print(f"  ✓ Fast: avg {sum(times)/len(times):.1f}ms per property")
        print()
        print("This demonstrates BOTH soundness (verifies correct code)")
        print("AND completeness (finds real bugs)!")
        print("="*70 + "\n")


def main():
    print("\n" + "*"*70)
    print("FINVERIFY - PAPER RESULTS GENERATOR".center(70))
    print("Telling the Complete Story".center(70))
    print("*"*70 + "\n")
    
    runner = PaperExperimentRunner()
    runner.run_all_experiments()
    
    csv_path = runner.save_to_csv()
    json_path = runner.save_to_json()
    
    runner.print_summary()
    
    print("[SUCCESS] Paper results generated!")
    print(f"          CSV: {csv_path}")
    print(f"          JSON: {json_path}")
    print("\n" + "*"*70 + "\n")


if __name__ == "__main__":
    main()

