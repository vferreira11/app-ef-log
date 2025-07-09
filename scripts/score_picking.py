import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

def score_ergonomico_altura(
    altura_mm: float,
    ideal_mm: float = 1200.0,
    min_score_baixo: float = 0.1
) -> float:
    """
    Score ergonômico em formato Gaussiano:
      – pico = 1.0 em ideal_mm
      – score ≈ min_score_baixo em 0 mm
    """
    sigma = ideal_mm / np.sqrt(-2 * np.log(min_score_baixo))
    score = np.exp(-0.5 * ((altura_mm - ideal_mm) / sigma) ** 2)
    return round(score, 4)

def plot_gradient(alturas: np.ndarray, scores: np.ndarray, max_altura: float):
    image = scores.reshape(-1, 1)
    cmap = LinearSegmentedColormap.from_list("custom", ["red", "yellow", "green"])
    fig, ax = plt.subplots(figsize=(2.5, 12))
    ax.imshow(image, cmap=cmap, aspect='auto',
              extent=[0, 1, 0, max_altura], origin='lower')
    for h in range(0, max_altura + 1, 100):
        s = scores[h]
        ax.text(1.08, h, f"{s:.3f}", va='center', fontsize=7)
        ax.text(-0.2, h, f"{h} mm", va='center', fontsize=7, ha='right')
    ax.set_xlim(-0.4, 1.8)
    ax.set_ylim(0, max_altura)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_ylabel("Altura (mm)", labelpad=35)
    ax.set_title("Gradient: Score contínuo de Picking", fontsize=12)
    ax.spines['left'].set_visible(False)
    plt.tight_layout()

def plot_curva(alturas: np.ndarray, scores: np.ndarray):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(alturas, scores, linewidth=2)
    ax.set_xlabel('Altura (mm)')
    ax.set_ylabel('Score ergonômico')
    ax.set_title('Curva de Score Ergonômico × Altura (Gaussiano)')
    plt.tight_layout()

if __name__ == '__main__':
    ideal_mm = 1200.0
    min_score = 0.1
    alcance = 2400.0
    max_altura = int(ideal_mm + alcance)
    alturas = np.arange(0, max_altura + 1)
    scores = np.array([score_ergonomico_altura(h, ideal_mm, min_score) for h in alturas])

    plot_gradient(alturas, scores, max_altura)
    plot_curva(alturas, scores)
    plt.show()
