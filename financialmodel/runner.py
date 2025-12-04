"""Orchestration utilities for running searches and returning structured results."""
from typing import Dict, Any, List
from financialmodel.costs import make_cost_fn
from financialmodel._optimizer import grid_search


class OptimizerRunner:
    def __init__(self, *, orientation: str = "S", tilt_angle: int = 30, tariff: str = "DynamicTariff", discount_rate: float = 0.05, pkl_path: str = None, cache: dict = None):
        self.orientation = orientation
        self.tilt_angle = tilt_angle
        self.tariff = tariff
        self.discount_rate = discount_rate
        self.pkl_path = pkl_path
        self.cache = cache

    def grid_search(self, param_grid: Dict[str, list], top_k: int = 10, progress: bool = False) -> List[Dict[str, Any]]:
        """Run grid search over param_grid using the cost function and return top_k detailed results.

        param_grid should contain keys matching the params expected by the cost function builder.
        Example params shape: {'solar': {...}, 'battery': {...}, 'inverter': {...}, 'contract': {...}}
        But grid_search expects flat parameter dicts; callers can construct a grid where each param is either a nested dict or a primitive.
        """
        cost_fn, compute_metrics = make_cost_fn(
            orientation=self.orientation,
            tilt_angle=self.tilt_angle,
            tariff=self.tariff,
            discount_rate=self.discount_rate,
            pkl_path=self.pkl_path,
            cache=self.cache,
        )

        # Use existing grid_search utility to obtain top param combos
        top_params = grid_search(param_grid, cost_fn, top_k=top_k, progress=progress)

        # Enrich with metrics
        detailed_results = []
        for entry in top_params:
            params = entry["params"]
            try:
                metrics = compute_metrics(params)
            except Exception as e:
                metrics = {"error": str(e)}
            detailed_results.append({"params": params, "cost": entry["cost"], "metrics": metrics})

        return detailed_results
