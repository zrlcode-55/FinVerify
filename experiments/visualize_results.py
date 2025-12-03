"""
Visualization Generator for IEEE Paper
Creates 3 publication-quality figures

Author: CS 6315 Final Project
Date: December 2025
"""

import json
import os
import csv
from collections import defaultdict

# Try importing matplotlib, provide fallback
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("[WARNING] matplotlib not available. Install with: pip install matplotlib")


class ResultsVisualizer:
    """Generate IEEE-quality visualizations from experimental results"""
    
    def __init__(self, results_file="experimental_results.json"):
        self.results_file = os.path.join(os.path.dirname(__file__), results_file)
        self.output_dir = os.path.join(os.path.dirname(__file__), "figures")
        self.data = None
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load data
        self.load_data()
    
    def load_data(self):
        """Load experimental results from JSON"""
        if not os.path.exists(self.results_file):
            print(f"[ERROR] Results file not found: {self.results_file}")
            print("        Run generate_results.py first!")
            return False
        
        with open(self.results_file, 'r') as f:
            full_data = json.load(f)
            self.data = full_data.get('results', [])
        
        print(f"[OK] Loaded {len(self.data)} experimental results")
        return True
    
    def figure1_verification_time_vs_complexity(self):
        """
        Figure 1: Verification Time vs Problem Complexity
        Shows how verification time scales with number of constraints
        """
        if not HAS_MATPLOTLIB or not self.data:
            print("[SKIP] Cannot generate Figure 1")
            return
        
        print("\n>>> Generating Figure 1: Verification Time vs Complexity")
        
        # Extract data
        constraints = []
        times = []
        colors = []
        labels = []
        
        color_map = {
            'conservation': '#2E86AB',  # blue
            'cross_chain_invariant': '#A23B72',  # purple
            'arithmetic_safety': '#F18F01',  # orange
            'security': '#C73E1D'  # red
        }
        
        for result in self.data:
            if 'constraints' in result and 'execution_time_ms' in result:
                constraints.append(result['constraints'])
                times.append(result['execution_time_ms'])
                ptype = result.get('property_type', 'other')
                colors.append(color_map.get(ptype, '#666666'))
                labels.append(ptype)
        
        # Create figure with IEEE style
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Group by property type for legend
        property_types = list(set(labels))
        for ptype in property_types:
            mask = [l == ptype for l in labels]
            c = [constraints[i] for i, m in enumerate(mask) if m]
            t = [times[i] for i, m in enumerate(mask) if m]
            col = color_map.get(ptype, '#666666')
            ax.scatter(c, t, c=col, label=ptype.replace('_', ' ').title(), 
                      s=100, alpha=0.7, edgecolors='black', linewidth=0.5)
        
        ax.set_xlabel('Number of Constraints', fontsize=12, fontweight='bold')
        ax.set_ylabel('Verification Time (ms)', fontsize=12, fontweight='bold')
        ax.set_title('Figure 1: Verification Time vs Problem Complexity', 
                    fontsize=13, fontweight='bold', pad=15)
        ax.legend(loc='upper left', frameon=True, shadow=True)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Add trend line
        if len(constraints) > 1:
            z = np.polyfit(constraints, times, 1)
            p = np.poly1d(z)
            x_trend = np.linspace(min(constraints), max(constraints), 100)
            ax.plot(x_trend, p(x_trend), "k--", alpha=0.5, linewidth=2, 
                   label=f'Trend: {z[0]:.2f}x + {z[1]:.2f}')
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'figure1_time_complexity.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"[OK] Saved: {output_path}")
        return output_path
    
    def figure2_verification_results_breakdown(self):
        """
        Figure 2: Verification Results Breakdown
        Bar chart showing verified/violated properties by category
        """
        if not HAS_MATPLOTLIB or not self.data:
            print("[SKIP] Cannot generate Figure 2")
            return
        
        print("\n>>> Generating Figure 2: Verification Results Breakdown")
        
        # Organize data by property type
        results_by_type = defaultdict(lambda: {'verified': 0, 'violated': 0, 'unknown': 0})
        
        for result in self.data:
            ptype = result.get('property_type', 'other')
            result_str = result.get('result', '')
            
            if 'VERIFIED' in result_str:
                results_by_type[ptype]['verified'] += 1
            elif 'VIOLATED' in result_str:
                results_by_type[ptype]['violated'] += 1
            else:
                results_by_type[ptype]['unknown'] += 1
        
        # Prepare data for plotting
        property_types = list(results_by_type.keys())
        verified = [results_by_type[pt]['verified'] for pt in property_types]
        violated = [results_by_type[pt]['violated'] for pt in property_types]
        unknown = [results_by_type[pt]['unknown'] for pt in property_types]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = np.arange(len(property_types))
        width = 0.25
        
        bars1 = ax.bar(x - width, verified, width, label='Verified', 
                      color='#2E7D32', alpha=0.8, edgecolor='black', linewidth=0.5)
        bars2 = ax.bar(x, violated, width, label='Violated (Bug Found)', 
                      color='#C62828', alpha=0.8, edgecolor='black', linewidth=0.5)
        bars3 = ax.bar(x + width, unknown, width, label='Unknown', 
                      color='#757575', alpha=0.8, edgecolor='black', linewidth=0.5)
        
        # Add value labels on bars
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height)}',
                           ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax.set_xlabel('Property Type', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Experiments', fontsize=12, fontweight='bold')
        ax.set_title('Figure 2: Verification Results by Property Category', 
                    fontsize=13, fontweight='bold', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels([pt.replace('_', '\n').title() for pt in property_types], 
                          fontsize=10)
        ax.legend(loc='upper right', frameon=True, shadow=True)
        ax.grid(True, alpha=0.3, axis='y', linestyle='--')
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'figure2_results_breakdown.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"[OK] Saved: {output_path}")
        return output_path
    
    def figure3_attack_detection_success_rate(self):
        """
        Figure 3: Attack Detection Success Rate
        Shows effectiveness at finding different vulnerability types
        """
        if not HAS_MATPLOTLIB or not self.data:
            print("[SKIP] Cannot generate Figure 3")
            return
        
        print("\n>>> Generating Figure 3: Attack Detection Success Rate")
        
        # Define known attack types and whether they should be found
        attack_categories = {
            'Replay Attacks': {'found': 0, 'total': 0},
            'Integer Overflow': {'found': 0, 'total': 0},
            'Conservation Violations': {'found': 0, 'total': 0},
            'Authorization Bypass': {'found': 0, 'total': 0}
        }
        
        for result in self.data:
            name = result.get('experiment_name', '')
            result_str = result.get('result', '')
            
            # Categorize experiments
            if 'Replay' in name:
                attack_categories['Replay Attacks']['total'] += 1
                if 'VIOLATED' in result_str:
                    attack_categories['Replay Attacks']['found'] += 1
            
            elif 'Overflow' in name:
                attack_categories['Integer Overflow']['total'] += 1
                if 'VIOLATED' in result_str:
                    attack_categories['Integer Overflow']['found'] += 1
            
            elif 'Conservation' in name or 'ERC20' in name:
                attack_categories['Conservation Violations']['total'] += 1
                if 'VIOLATED' in result_str:
                    attack_categories['Conservation Violations']['found'] += 1
            
            elif 'Hoare' in name:
                attack_categories['Authorization Bypass']['total'] += 1
                if 'VIOLATED' in result_str or 'FAIL' in result_str:
                    attack_categories['Authorization Bypass']['found'] += 1
        
        # Calculate success rates
        categories = []
        success_rates = []
        counts = []
        
        for cat, data in attack_categories.items():
            if data['total'] > 0:
                categories.append(cat)
                rate = (data['found'] / data['total']) * 100
                success_rates.append(rate)
                counts.append(f"{data['found']}/{data['total']}")
        
        # Create figure  
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors = ['#D32F2F' if rate > 50 else '#388E3C' for rate in success_rates]
        bars = ax.barh(categories, success_rates, color=colors, alpha=0.8, 
                      edgecolor='black', linewidth=1.5)
        
        # Add percentage labels
        for i, (bar, rate, count) in enumerate(zip(bars, success_rates, counts)):
            width = bar.get_width()
            ax.text(width + 2, bar.get_y() + bar.get_height()/2,
                   f'{rate:.1f}% ({count})',
                   ha='left', va='center', fontsize=11, fontweight='bold')
        
        ax.set_xlabel('Detection Success Rate (%)', fontsize=12, fontweight='bold')
        ax.set_title('Figure 3: Vulnerability Detection Effectiveness', 
                    fontsize=13, fontweight='bold', pad=15)
        ax.set_xlim(0, 120)
        ax.grid(True, alpha=0.3, axis='x', linestyle='--')
        
        # Add legend explaining colors
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#D32F2F', alpha=0.8, edgecolor='black', 
                  label='Buggy (Expected Detection)'),
            Patch(facecolor='#388E3C', alpha=0.8, edgecolor='black', 
                  label='Secure (No Violation Expected)')
        ]
        ax.legend(handles=legend_elements, loc='lower right', frameon=True, shadow=True)
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'figure3_attack_detection.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"[OK] Saved: {output_path}")
        return output_path
    
    def generate_all_figures(self):
        """Generate all three figures for the paper"""
        print("\n" + "="*70)
        print("GENERATING IEEE PAPER VISUALIZATIONS")
        print("="*70)
        
        if not HAS_MATPLOTLIB:
            print("\n[ERROR] matplotlib required for visualizations")
            print("        Install: pip install matplotlib numpy")
            return []
        
        if not self.data:
            print("\n[ERROR] No data loaded. Run generate_results.py first!")
            return []
        
        figures = []
        
        try:
            fig1 = self.figure1_verification_time_vs_complexity()
            if fig1:
                figures.append(fig1)
            
            fig2 = self.figure2_verification_results_breakdown()
            if fig2:
                figures.append(fig2)
            
            fig3 = self.figure3_attack_detection_success_rate()
            if fig3:
                figures.append(fig3)
        
        except Exception as e:
            print(f"\n[ERROR] Failed to generate visualizations: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*70)
        print(f"[SUCCESS] Generated {len(figures)} figures")
        print(f"          Output directory: {self.output_dir}")
        print("="*70 + "\n")
        
        return figures


def main():
    """Main entry point"""
    print("\n" + "*"*70)
    print("FINVERIFY - VISUALIZATION GENERATOR".center(70))
    print("For IEEE Paper Submission".center(70))
    print("*"*70 + "\n")
    
    visualizer = ResultsVisualizer()
    figures = visualizer.generate_all_figures()
    
    if figures:
        print("\n[SUCCESS] All visualizations generated!")
        print("\nGenerated Figures:")
        for i, fig in enumerate(figures, 1):
            print(f"  {i}. {os.path.basename(fig)}")
        print("\nThese figures are ready for IEEE paper inclusion.")
    else:
        print("\n[FAILED] Could not generate visualizations")
        print("         Make sure to run generate_results.py first")
        print("         And install: pip install matplotlib numpy")
    
    print("\n" + "*"*70 + "\n")


if __name__ == "__main__":
    main()

