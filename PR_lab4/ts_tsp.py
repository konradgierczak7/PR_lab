import random
import time
import math
from collections import deque
from multiprocessing import Pool

N_CITIES = 400          # liczba miast
ITERATIONS = 1000       # warunek stopu: liczba iteracji
TABU_TENURE = 30        # kadencja
SEED = 42

DIST = None

def init_worker(dist):
    global DIST
    DIST = dist

def generate_cities(n, seed):
    rnd = random.Random(seed)
    return [(rnd.uniform(0, 1000), rnd.uniform(0, 1000)) for _ in range(n)]

def distance_matrix(cities):
    return [[math.dist(a, b) for b in cities] for a in cities]

def tour_length(tour):
    """Funkcja celu: długość trasy (cykl zamknięty)."""
    return sum(DIST[tour[k]][tour[k + 1]] for k in range(len(tour) - 1)) + DIST[tour[-1]][tour[0]]

def edge(a, b):
    return (a, b) if a < b else (b, a)

def search_chunk(args):
    tour, i_values, tabu, cur_len, best_len = args
    n = len(tour)
    best = (math.inf, -1, -1)
    for i in i_values:
        a, b = tour[i], tour[i + 1]
        row_a, row_b = DIST[a], DIST[b]
        d_ab = row_a[b]
        for j in range(i + 2, n if i > 0 else n - 1):
            c, d = tour[j], tour[(j + 1) % n]
            delta = row_a[c] + row_b[d] - d_ab - DIST[c][d]
            if delta < best[0]:
                is_tabu = edge(a, c) in tabu or edge(b, d) in tabu
                aspiration = cur_len + delta < best_len - 1e-9
                if not is_tabu or aspiration:
                    best = (delta, i, j)
    return best

# ---------------- TABU SEARCH ----------------
def tabu_search(dist, workers):
    global DIST
    DIST = dist
    random.seed(SEED)
    n = len(dist)

    tour = random.sample(range(n), n)
    cur_len = tour_length(tour)
    best_tour, best_len = tour[:], cur_len

    tabu_queue = deque()
    tabu = set()

    i_parts = [list(range(w, n - 2, workers)) for w in range(workers)]

    with Pool(workers, initializer=init_worker, initargs=(dist,)) as pool:
        for it in range(ITERATIONS):
            tasks = [(tour, part, tabu, cur_len, best_len) for part in i_parts]
            results = pool.map(search_chunk, tasks)
            delta, i, j = min(results)
            if i < 0:
                break

            a, b, c, d = tour[i], tour[i + 1], tour[j], tour[(j + 1) % n]
            for e in (edge(a, b), edge(c, d)):
                tabu.add(e)
                tabu_queue.append(e)
            while len(tabu_queue) > 2 * TABU_TENURE:
                tabu.discard(tabu_queue.popleft())

            tour[i + 1:j + 1] = reversed(tour[i + 1:j + 1])
            cur_len += delta
            if cur_len < best_len:
                best_tour, best_len = tour[:], cur_len

            if it % 250 == 0:
                print(f"  iteracja {it:4d}: bieżąca = {cur_len:.2f}, najlepsza = {best_len:.2f}")

    return best_tour, best_len

if __name__ == "__main__":
    cities = generate_cities(N_CITIES, SEED)
    dist = distance_matrix(cities)

    tested = sorted({w for w in (1, 2, 4, 8) })
    times = {}
    for workers in tested:
        print(f"\n=== Tabu Search, liczba procesów: {workers} ===")
        t0 = time.perf_counter()
        best, best_len = tabu_search(dist, workers)
        t = time.perf_counter() - t0
        print(f"Najlepsza długość trasy: {best_len:.2f} ")
        print(f"Czas: {t:.2f} s")
        times[workers] = t

    print("\n=== PODSUMOWANIE ===")
    for w, t in times.items():
        print(f"procesy: {w:2d}  czas: {t:6.2f} s  przyspieszenie: {times[1] / t:.2f}x")