def generate_distribution(N=18, podium=(25,18,14), drop_4th=0.6, drop_5th=0.6, decay=0.6, min_val=1):
    """
    Strictly decreasing distribution with no repeated values.
    
    - Top 3 fixed
    - 4th = drop_4th * 3rd
    - 5th = drop_5th * 4th
    - 6th+ = previous * decay, floored at min_val
    """
    distribution = []
    a,b,c = podium
    distribution.append((1,a))
    distribution.append((2,b))
    distribution.append((3,c))
    distribution_scalars = [a, b, c]
    
    val4 = c * drop_4th
    distribution.append((4,val4))
    distribution_scalars.append(val4)
    
    val5 = val4 * drop_5th
    distribution.append((5,val5))
    distribution_scalars.append(val5)

    # 6th onward
    prev = val5
    for i in range(6, N+1):
        val = max(prev * decay, min_val)  # ensure strictly decreasing
        if val >= prev:
            val = prev * 0.99  # safety: make strictly less than previous
        distribution.append((i,val))
        distribution_scalars.append(val)
        prev = val

    # Normalize to 100%
    totalPercent = sum(distribution_scalars)

    scale = 100 / totalPercent
    distribution = [(pos, val * scale) for pos, val in distribution]
    distribution_scalars = [v * scale for v in distribution_scalars]

    totalPercent = sum(distribution_scalars)
    print(f"Total percentage allocated: {totalPercent:.2f}%")

    return (distribution, distribution_scalars)

def print_distribution(dist):
    print("Place | Value")
    print("-------------")
    for place,val in dist:
        print(f"{place:>5} | {val:.2f}")

# GRAPHIC GENERATION
import matplotlib.pyplot as plt

def plot_distribution_side_by_side(dist):
    places = [place for place, val in dist]
    values = [val for place, val in dist]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14,6), gridspec_kw={'width_ratios':[2, 1]})

    # --- Left: Line chart ---
    ax1.plot(places, values, marker='o', linestyle='-', color='blue')
    ax1.set_title("Strictly Decreasing Points Distribution")
    ax1.set_xlabel("Place")
    ax1.set_ylabel("Points")
    ax1.set_xticks(places)
    ax1.grid(True, linestyle='--', alpha=0.6)

    # --- Right: Table ---
    table_data = [[place, f"{val:.2f}"] for place, val in dist]
    ax2.axis('off')  # hide axes
    ax2.table(cellText=table_data,
              colLabels=["Place", "Points"],
              cellLoc="center",
              colLoc="center",
              loc="center")
    ax2.set_title("Points Table")

    plt.tight_layout()
    plt.show()

def main():
    dist, scalars = generate_distribution(
        N=18,
        podium=(25,18,14),
        drop_4th=0.6,
        drop_5th=0.8,
        decay=0.8,
        min_val=1
    )
    print(scalars)
    print_distribution(dist)
    plot_distribution_side_by_side(dist)

if __name__ == "__main__":
    main()
