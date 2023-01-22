from tqdm import tqdm
import time
import networkx as nx

class State:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


# Make every path between s and t have length of at least goal
def attack(c):
    add_times = []
    perturb_times = []

    G = c.G.copy()
    # TODO: Merge edge perturbations for undirected graphs
    if type(G) == nx.Graph:
        G = G.to_directed(as_view=True)

    state = State(
        G_prime=G.copy(),
        perturbation_dict=dict(),
        paths = set(),
        all_path_edges = set(),
        current_distance = c.path_selector.distance(G),
    )

    perturbation_result = dict()

    status= "Fail: Unknown"
    for i in range(c.max_iterations):
        # Add Paths
        add_start_time = time.time()
        new_paths = c.path_selector.get_next(state=state)
        add_times.append(time.time() - add_start_time)

        # Update State
        if not new_paths:
            status = "Fail: No Paths Returned By Selector"
            break
        else:
            state.paths.update(new_paths)
            for new_path in new_paths: 
                state.all_path_edges.update(zip(new_path[:-1], new_path[1:]))

        # Perturb Graph
        perturb_start_time = time.time()
        c.perturber.add_paths(new_paths)
        perturbation_result = c.perturber.perturb()
        perturb_times.append(time.time() - perturb_start_time)

        if perturbation_result["Perturbation Failure"]:
            status = "Fail: Failure in Perturber"
            break

        for edge, perturbation in state.perturbation_dict.items():
            state.G_prime.edges[edge[0], edge[1]]["weight"] -= perturbation

        state.perturbation_dict = perturbation_result["Perturbation Dict"]

        # Create Perturbed Graph TODO: make this more efficient
        # G_prime = G.copy()
        for edge, perturbation in state.perturbation_dict.items():
            state.G_prime.edges[edge[0], edge[1]]["weight"] += perturbation
        # state.G_prime = G_prime

        # Check if we are done
        state.current_distance = c.path_selector.distance(state.G_prime)
        if state.current_distance >= c.path_selector.goal:
            status = "Success"
            break

    if status != "Success" and c.max_iterations == i+1:
        status = "Fail: Max Iterations"

    stats_dict = {
        "Number of Paths": len(state.paths),
        "Number of Edges": len(state.all_path_edges),
        "Add Times": add_times,
        "Perturb Times": perturb_times,
        "Iterations": i+1,
        "Final Distance": state.current_distance,
        "Status": status,
        **perturbation_result
    }

    return stats_dict