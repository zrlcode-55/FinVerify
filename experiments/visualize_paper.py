"""
Paper Visualizations - Telling the Right Story

Creates 3 IEEE-quality figures that demonstrate:
1. We can VERIFY secure code
2. We can FIND BUGS in buggy code  
3. Performance scales well

Author: CS 6315 Final Project
"""

import json
import os
from collections import defaultdict

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("[ERROR] matplotlib not installed. Run: pip install matplotlib numpy")


class PaperVisualizer:
    """Create publication-quality figures for IEEE paper"""
    
    def __init__(self, results_file="paper_results.json"):
        self.results_file = os.path.join(os.path.dirname(__file__), results_file)
        self.output_dir = os.path.join(os.path.dirname(__file__), "paper_figures")
        self.data = None
        
        os.makedirs(self.output_dir, exist_ok=True)
        self.load_data()
    
    def load_data(self):
        """Load experimental results"""
        if not os.path.exists(self.results_file):
            print(f"[ERROR] Results file not found: {self.results_file}")
            print("        Run generate_paper_results.py first!")
            return False
        
        with open(self.results_file, 'r') as f:
            full_data = json.load(f)
            self.data = full_data.get('results', [])
        
        print(f"[OK] Loaded {len(self.data)} experiments")
        return True
    
    def figure1_verification_vs_bug_detection(self):
        """
        Figure 1: Core Result - We Do BOTH
        Shows we can verify secure code AND find bugs
        """
        if not HAS_MATPLOTLIB or not self.data:
            return None
        
        print("\n>>> Generating Figure 1: Verification vs Bug Detection")
        
        # Split by implementation type
        secure = [r for r in self.data if r['implementation_type'] == 'SECURE']
        buggy = [r for r in self.data if r['implementation_type'] == 'BUGGY']
        
        # Count correct outcomes
        secure_verified = sum(1 for r in secure if r['actual_result'] == 'VERIFIED')
        bugs_found = sum(1 for r in buggy if r['actual_result'] == 'BUG_FOUND')
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Left: Secure code verification
        categories = ['Secure\nImplementations']
        verified = [secure_verified]
        total = [len(secure)]
        
        x = np.arange(len(categories))
        width = 0.35
        
        bars1 = ax1.bar(x, verified, width, label='Verified', 
                       color='#2E7D32', alpha=0.9, edgecolor='black', linewidth=2)
        bars2 = ax1.bar(x, [t - v for t, v in zip(total, verified)], width, 
                       bottom=verified, label='Failed', 
                       color='#CCCCCC', alpha=0.5, edgecolor='black', linewidth=2)
        
        # Add labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height/2,
                    f'{int(height)}/{total[0]}',
                    ha='center', va='center', fontsize=16, fontweight='bold', color='white')
        
        ax1.set_ylabel('Number of Experiments', fontsize=12, fontweight='bold')
        ax1.set_title('(a) Secure Code Verification', fontsize=13, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(categories, fontsize=11)
        ax1.set_ylim(0, max(total) + 2)
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.legend(loc='upper right')
        
        # Add accuracy percentage
        acc = secure_verified / len(secure) * 100
        ax1.text(0, len(secure) + 1, f'{acc:.0f}% Accuracy', 
                ha='center', fontsize=14, fontweight='bold', color='#2E7D32',
                bbox=dict(boxstyle='round', facecolor='white', edgecolor='#2E7D32', linewidth=2))
        
        # Right: Bug detection
        categories2 = ['Buggy\nImplementations']
        found = [bugs_found]
        total2 = [len(buggy)]
        
        x2 = np.arange(len(categories2))
        
        bars3 = ax2.bar(x2, found, width, label='Bugs Found', 
                       color='#C62828', alpha=0.9, edgecolor='black', linewidth=2)
        bars4 = ax2.bar(x2, [t - f for t, f in zip(total2, found)], width, 
                       bottom=found, label='Missed', 
                       color='#CCCCCC', alpha=0.5, edgecolor='black', linewidth=2)
        
        # Add labels
        for bar in bars3:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height/2,
                    f'{int(height)}/{total2[0]}',
                    ha='center', va='center', fontsize=16, fontweight='bold', color='white')
        
        ax2.set_ylabel('Number of Experiments', fontsize=12, fontweight='bold')
        ax2.set_title('(b) Vulnerability Detection', fontsize=13, fontweight='bold')
        ax2.set_xticks(x2)
        ax2.set_xticklabels(categories2, fontsize=11)
        ax2.set_ylim(0, max(total2) + 2)
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.legend(loc='upper right')
        
        # Add detection rate
        rate = bugs_found / len(buggy) * 100
        ax2.text(0, len(buggy) + 1, f'{rate:.0f}% Detection Rate', 
                ha='center', fontsize=14, fontweight='bold', color='#C62828',
                bbox=dict(boxstyle='round', facecolor='white', edgecolor='#C62828', linewidth=2))
        
        plt.suptitle('Figure 1: FinVerify Demonstrates Both Soundness and Completeness', 
                    fontsize=14, fontweight='bold', y=1.02)
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'figure1_soundness_completeness.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"[OK] Saved: {output_path}")
        return output_path
    
    def figure2_results_by_category(self):
        """
        Figure 2: Results by Property Category
        Shows we handle different types of properties
        """
        if not HAS_MATPLOTLIB or not self.data:
            return None
        
        print("\n>>> Generating Figure 2: Results by Property Category")
        
        # Group by category
        categories = {}
        for r in self.data:
            cat = r['property_category']
            impl_type = r['implementation_type']
            result = r['actual_result']
            
            if cat not in categories:
                categories[cat] = {'secure_verified': 0, 'bugs_found': 0}
            
            if impl_type == 'SECURE' and result == 'VERIFIED':
                categories[cat]['secure_verified'] += 1
            elif impl_type == 'BUGGY' and result == 'BUG_FOUND':
                categories[cat]['bugs_found'] += 1
        
        # Prepare data
        cat_names = list(categories.keys())
        secure_counts = [categories[c]['secure_verified'] for c in cat_names]
        buggy_counts = [categories[c]['bugs_found'] for c in cat_names]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(cat_names))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, secure_counts, width, label='Secure Code Verified',
                      color='#388E3C', alpha=0.85, edgecolor='black', linewidth=1)
        bars2 = ax.bar(x + width/2, buggy_counts, width, label='Bugs Detected',
                      color='#D32F2F', alpha=0.85, edgecolor='black', linewidth=1)
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                           f'{int(height)}',
                           ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax.set_xlabel('Property Category', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Experiments', fontsize=12, fontweight='bold')
        ax.set_title('Figure 2: Verification Results Across Different Property Categories',
                    fontsize=13, fontweight='bold', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(cat_names, fontsize=10, rotation=15, ha='right')
        ax.legend(loc='upper left', fontsize=11, frameon=True, shadow=True)
        ax.grid(True, alpha=0.3, axis='y', linestyle='--')
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'figure2_by_category.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"[OK] Saved: {output_path}")
        return output_path
    
    def figure3_performance_analysis(self):
        """
        Figure 3: Performance - Shows we're fast
        """
        if not HAS_MATPLOTLIB or not self.data:
            return None
        
        print("\n>>> Generating Figure 3: Performance Analysis")
        
        # Group by category and get avg times
        category_times = defaultdict(list)
        for r in self.data:
            category_times[r['property_category']].append(r['execution_time_ms'])
        
        # Calculate stats
        categories = sorted(category_times.keys())
        avg_times = [np.mean(category_times[c]) for c in categories]
        std_times = [np.std(category_times[c]) for c in categories]
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Left: Bar chart of average times
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(categories)))
        bars = ax1.bar(range(len(categories)), avg_times, color=colors, 
                      alpha=0.8, edgecolor='black', linewidth=1.5,
                      yerr=std_times, capsize=5, error_kw={'linewidth': 2})
        
        # Add value labels
        for i, (bar, avg, std) in enumerate(zip(bars, avg_times, std_times)):
            ax1.text(bar.get_x() + bar.get_width()/2., avg + std + 0.5,
                    f'{avg:.1f}ms',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax1.set_xlabel('Property Category', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Average Verification Time (ms)', fontsize=12, fontweight='bold')
        ax1.set_title('(a) Performance by Category', fontsize=13, fontweight='bold')
        ax1.set_xticks(range(len(categories)))
        ax1.set_xticklabels(categories, fontsize=9, rotation=20, ha='right')
        ax1.grid(True, alpha=0.3, axis='y', linestyle='--')
        
        # Add overall average line
        overall_avg = np.mean([r['execution_time_ms'] for r in self.data])
        ax1.axhline(y=overall_avg, color='red', linestyle='--', linewidth=2, 
                   label=f'Overall Avg: {overall_avg:.1f}ms')
        ax1.legend()
        
        # Right: Distribution histogram
        all_times = [r['execution_time_ms'] for r in self.data]
        ax2.hist(all_times, bins=15, color='#1976D2', alpha=0.7, 
                edgecolor='black', linewidth=1.5)
        ax2.axvline(x=overall_avg, color='red', linestyle='--', linewidth=3,
                   label=f'Mean: {overall_avg:.1f}ms')
        ax2.axvline(x=np.median(all_times), color='green', linestyle='--', linewidth=3,
                   label=f'Median: {np.median(all_times):.1f}ms')
        
        ax2.set_xlabel('Verification Time (ms)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Frequency', fontsize=12, fontweight='bold')
        ax2.set_title('(b) Performance Distribution', fontsize=13, fontweight='bold')
        ax2.legend(fontsize=11, frameon=True, shadow=True)
        ax2.grid(True, alpha=0.3, axis='y', linestyle='--')
        
        # Add summary stats text box
        stats_text = f'Min: {min(all_times):.1f}ms\\nMax: {max(all_times):.1f}ms\\nStd: {np.std(all_times):.1f}ms'
        ax2.text(0.98, 0.97, stats_text, transform=ax2.transAxes,
                fontsize=10, verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.suptitle('Figure 3: FinVerify Performance Analysis', 
                    fontsize=14, fontweight='bold', y=1.02)
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'figure3_performance.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"[OK] Saved: {output_path}")
        return output_path
    
    def generate_all_figures(self):
        """Generate all paper figures"""
        print("\n" + "="*70)
        print("GENERATING PAPER VISUALIZATIONS")
        print("="*70)
        
        if not HAS_MATPLOTLIB:
            print("\n[ERROR] matplotlib required. Install: pip install matplotlib numpy")
            return []
        
        if not self.data:
            print("\n[ERROR] No data loaded!")
            return []
        
        figures = []
        
        try:
            fig1 = self.figure1_verification_vs_bug_detection()
            if fig1: figures.append(fig1)
            
            fig2 = self.figure2_results_by_category()
            if fig2: figures.append(fig2)
            
            fig3 = self.figure3_performance_analysis()
            if fig3: figures.append(fig3)
        
        except Exception as e:
            print(f"\n[ERROR] Failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*70)
        print(f"[SUCCESS] Generated {len(figures)} publication-quality figures")
        print(f"          Output: {self.output_dir}")
        print("="*70 + "\n")
        
        return figures


def main():
    print("\n" + "*"*70)
    print("PAPER VISUALIZATION GENERATOR".center(70))
    print("IEEE-Quality Figures".center(70))
    print("*"*70 + "\n")
    
    viz = PaperVisualizer()
    figures = viz.generate_all_figures()
    
    if figures:
        print("\n✓ All figures generated successfully!")
        print("\nFigures for paper:")
        for i, fig in enumerate(figures, 1):
            print(f"  {i}. {os.path.basename(fig)}")
        print("\nThese tell the complete story:")
        print("  1. We verify secure code (soundness)")
        print("  2. We find bugs in vulnerable code (completeness)")
        print("  3. We do it fast (performance)")
    else:
        print("\n✗ Failed to generate figures")
    
    print("\n" + "*"*70 + "\n")


if __name__ == "__main__":
    main()
