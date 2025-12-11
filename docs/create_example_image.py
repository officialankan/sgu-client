#!/usr/bin/env python3
"""
Script to create a placeholder example output image for the documentation.
Run this after installing matplotlib: pip install matplotlib
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def create_example_image():
    """Create a sample DataFrame output image."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.axis('off')

    # Sample data for display
    data = [
        ['observation_date', 'grundvattenniva_m_o_h', 'metod_for_matning'],
        ['2023-01-15 10:00:00', '45.23', 'Manual measurement'],
        ['2023-02-10 09:30:00', '45.67', 'Automatic logger'],
        ['2023-03-05 11:15:00', '44.89', 'Manual measurement'],
        ['2023-04-12 14:20:00', '46.12', 'Automatic logger'],
        ['2023-05-18 08:45:00', '45.98', 'Manual measurement'],
    ]

    # Create table
    table = ax.table(cellText=data, cellLoc='left', loc='center',
                    colWidths=[0.35, 0.35, 0.3])

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)

    # Style header row
    for i in range(3):
        table[(0, i)].set_facecolor('#2E86AB')
        table[(0, i)].set_text_props(weight='bold', color='white')

    # Style data rows
    for i in range(1, 6):
        for j in range(3):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#F0F0F0')
            else:
                table[(i, j)].set_facecolor('white')

    # Add title
    plt.title('SGU Client - DataFrame Output Example',
              fontsize=14, fontweight='bold', pad=20)

    # Add footer text
    fig.text(0.5, 0.05, 'Example: Groundwater measurements converted to pandas DataFrame',
             ha='center', fontsize=9, style='italic', color='gray')

    plt.tight_layout()
    plt.savefig('source/_static/example_output.png', dpi=100, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print('✓ Placeholder image created successfully at source/_static/example_output.png')

if __name__ == '__main__':
    try:
        create_example_image()
    except ImportError as e:
        print(f"Error: {e}")
        print("\nPlease install matplotlib to generate the example image:")
        print("  pip install matplotlib")
        print("\nAlternatively, the SVG placeholder will be used.")
