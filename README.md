
# PerturbPaths

  

Implementation and extension of [PATHPERTURB](https://arxiv.org/pdf/2107.03347.pdf), along with additional experiments

  

The main algorithm is contained in [general_attack.py](./general_attack.py)

In each iteration, it will:

- Select path(s) to add to the set being considered (code in [selector_classes.py](./selector_classes.py))

- Calculate (or approximate) the smallest perturbation of edge weights that will make all paths at least as long as some predefined goal (code in [perturbation_functions.py](./perturbation_functions.py))

- Check if this local optimum is also a global solution (i.e. a global optimum)

  

A series of experiments can be performed using [run_experiments.py](./run_experiments.py)

  

## References

Miller, Benjamin & Shafi, Zohair & Ruml, Wheeler & Vorobeychik, Yevgeniy & Eliassi-Rad, Tina & Alfeld, Scott. (2021). Optimal Edge Weight Perturbations to Attack Shortest Paths.
