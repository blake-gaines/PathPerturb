import time
from DataSets import DataSets
import networkx as nx
from data import get_graph
import numpy as np
from general_attack import attack, PathSelector
import random
from itertools import product
from utils import *
import pandas as pd
from tqdm import tqdm

weighted = False

path_selectors = [
    PathSelector("Ours", nx.shortest_simple_paths, update_every_iteration=False, weight="weight"),
    PathSelector("Theirs", nx.shortest_simple_paths, update_every_iteration=True, weight="weight"),
    # PathSelector("One Sided Random", random_one_sided, update_every_iteration=False, weight="weight"),
    # PathSelector("Static Random", random_paths, update_every_iteration=False, weight="weight"),
    # PathSelector("Dynamic Random", random_paths, update_every_iteration=False, weight="weight"),
]



if __name__ == "__main__":
    random.seed(7)


    G = DataSets.get_directed_networkx_graph(dataset=DataSets.FACEBOOK, lcc=False)
    if weighted:
        nx.set_edge_attributes(G, {e: random.randint(1,10) for e in G.edges()}, "weight")
    else:
        nx.set_edge_attributes(G, 1, "weight")

    print("Graph Information")
    print('nodes: {} \nedges: {}\n'.format(G.number_of_nodes(), G.number_of_edges()))

    # node_pairs = [[2565,999],[2254,996],[2308,65],[3067,2743],[1259,933],
    #         [2310,1934],[2130,402],[2569,1577],[2272,857],[1808,936],
    #         [3452,371],[2818,1670],[2000,87],[1969,1286],[2733,26],
    #         [963,423],[3285,2789],[1041,414],[3414,3051],[1888,1715]]
    node_pairs = []
    while len(node_pairs) < 20:
        a,b = random.choices(list(G.nodes()),k=2)
        if nx.has_path(G, a, b):
            node_pairs.append((a,b))
    print("Node Pairs:", node_pairs)



    epsilon = 1
    n_trials = 1

    configuration_ranges = dict(
        node_pair = node_pairs,
        k = [2,3],
        global_budget = [1000],
        local_budget = [5,6,7],
        top_k = [1, 50],
    )
    print(configuration_ranges)

    results = []

    for trial_number in range(n_trials):
        for iteration, config_values in enumerate(tqdm(product(*configuration_ranges.values()))):
            config = dict(zip(configuration_ranges.keys(), config_values))
            print("\n========\nConfig:", config)

            source, target = config["node_pair"]
            original_path_length = nx.shortest_path_length(G, source, target, weight="weight")
            goal = original_path_length * config["k"] + epsilon
            # print(f"Original Path Length: {original_path_length} | Goal: {goal}")

            for path_selector in path_selectors:
                print("Selector:", path_selector.name)
                if "Random" in path_selector.name:
                    path_selector.generator_function_kwargs["goal"] = goal

                start_time = time.time()
                perturbations, stats_dict = attack(G, source, target, goal, path_selector, config["global_budget"], config["local_budget"], top_k=config["top_k"], max_iterations=100)
                perturbations = {k:v for k,v in perturbations.items() if v != 0}
                time_taken = time.time() - start_time

                if perturbations is None:
                    print("No solution found")

                # print("Cost: ", sum(perturbations.values()))

                results.append({
                    "Trial Number": trial_number,
                    "Original Path Length": original_path_length,
                    "Time Taken": time_taken,
                    "Perturbations": perturbations,
                    "Total Perturbation": sum(perturbations.values()) if perturbations is not None else None,
                    "Path Selector": path_selector.name,
                    "Epsilon": epsilon,
                    "Goal": goal,
                    **config,
                    **(stats_dict if stats_dict is not None else dict())
                })
                print()
    
            pd.DataFrame.from_records(results).to_pickle("results.pkl")