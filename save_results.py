"""
Save verification results to file for milestone documentation
"""

import sys
import time
import io
from contextlib import redirect_stdout
from run_full_pipeline import main


def save_results():
    """Run pipeline and save output"""
    
    # Capture output
    output = io.StringIO()
    
    print("Running full verification pipeline...")
    print("This will take about 0.1 seconds...")
    
    start = time.time()
    with redirect_stdout(output):
        main()
    elapsed = time.time() - start
    
    results = output.getvalue()
    
    # Save to file
    with open('verification_results.txt', 'w') as f:
        f.write(results)
    
    print(f"\n[SUCCESS] Results saved to verification_results.txt")
    print(f"Execution time: {elapsed:.2f} seconds")
    print(f"Output size: {len(results)} characters")
    
    # Generate summary
    bugs_found = results.count('[VIOLATED]')
    properties_verified = results.count('[SUCCESS]')
    
    summary = f"""
VERIFICATION RUN SUMMARY
========================
Date: {time.strftime('%Y-%m-%d %H:%M:%S')}
Execution Time: {elapsed:.2f} seconds
Properties Checked: {bugs_found + properties_verified}
Bugs Found: {bugs_found}
Properties Verified: {properties_verified}

Files Generated:
- verification_results.txt (full output)

Use this for milestone reports and documentation.
"""
    
    with open('summary.txt', 'w') as f:
        f.write(summary)
    
    print(summary)
    print("[OK] Ready for milestone submission!")


if __name__ == "__main__":
    save_results()

