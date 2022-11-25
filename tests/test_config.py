"""
Tests for basic input-output nad iterative loop.
"""

import pandas as pd
import pytest
from baybe.core import BayBE, BayBEConfig

# Dictionary containing items describing config tests that should throw an error.
# Key is a string describing the test and is displayed by pytest. Each value is a pair
# of the first item being the config dictionary update that is done to the default
# fixture and the second item being the expected exception type.
from baybe.utils import StrictValidationError
from pydantic import ValidationError

invalid_config_updates = {
    "param_num_duplicated": {
        "parameters": [
            {
                "name": "Numerical_New",
                "type": "NUM_DISCRETE",
                "values": [1, 2, 3, 2],
            }
        ],
    },
    "param_cat_duplicated": {
        "parameters": [
            {
                "name": "Categorical_New",
                "type": "CAT",
                "values": ["very bad", "bad", "OK", "OK"],
            }
        ],
    },
    "param_substance_invalid_field": {
        "parameters": [
            {
                "name": "Substance_New",
                "type": "SUBSTANCE",
                # Substance parameter does not use 'values' but 'data' field
                "values": {"water": "O", "methane": "C"},
            }
        ],
    },
    "param_substance_invalid_SMILES": {
        "parameters": [
            {
                "name": "Invalid_Substance",
                "type": "SUBSTANCE",
                "data": {"valid1": "C", "valid2": "CC", "invalid": "cc"},
            }
        ],
    },
    "param_custom_duplicated_index": {
        "parameters": [
            {
                "name": "Custom_1",
                "type": "CUSTOM",
                "data": pd.DataFrame(
                    {
                        "D1": [1.1, 1.4, 1.7, 0.8],
                        "D2": [11, 23, 55, 23],
                        "D3": [-4, -13, 4, -2],
                    },
                    index=["mol1", "mol2", "mol3", "mol1"],
                ),
            },
        ],
    },  #
    "empty_parameter_list": {
        "parameters": [],
    },
    "empty_target_list": {
        "objective": {
            "mode": "SINGLE",
            "targets": [],
        }
    },  #
    "targets_match_no_bounds": {
        "objective": {
            "mode": "SINGLE",
            "targets": [
                {
                    "name": "Target_1",
                    "type": "NUM",
                    "mode": "MATCH",
                },
            ],
        }
    },
    "targets_match_invalid_linear_transform": {
        "objective": {
            "mode": "SINGLE",
            "targets": [
                {
                    "name": "Target_1",
                    "type": "NUM",
                    "mode": "MATCH",
                    "bounds": (0, 100),
                    "bounds_transform_func": "LINEAR",
                },
            ],
        }
    },
    "targets_match_invalid_other_transform": {
        "objective": {
            "mode": "SINGLE",
            "targets": [
                {
                    "name": "Target_1",
                    "type": "NUM",
                    "mode": "MATCH",
                    "bounds": (0, 100),
                    "bounds_transform_func": "SOME_STUFF",
                },
            ],
        }
    },
    "desirability_no_bounds_provided": {
        "objective": {
            "mode": "DESIRABILITY",
            "combine_func": "MEAN",
            "targets": [
                {
                    "name": "Target_1",
                    "type": "NUM",
                    "mode": "MAX",
                    "bounds": (0, 100),
                },
                {
                    "name": "Target_2",
                    "type": "NUM",
                    "mode": "MIN",
                },
            ],
        }
    },
    "desirability_unknown_avg_function": {
        "objective": {
            "mode": "DESIRABILITY",
            "combine_func": "FALSE_STUFF",
            "targets": [
                {
                    "name": "Target_1",
                    "type": "NUM",
                    "mode": "MAX",
                    "bounds": (0, 100),
                },
                {
                    "name": "Target_2",
                    "type": "NUM",
                    "mode": "MIN",
                    "bounds": (0, 100),
                },
            ],
        }
    },
    "desirability_bad_weights1": {
        "objective": {
            "mode": "DESIRABILITY",
            "combine_func": "MEAN",
            "weights": [1, 2, 3],
            "targets": [
                {
                    "name": "Target_1",
                    "type": "NUM",
                    "mode": "MAX",
                    "bounds": (0, 100),
                },
                {
                    "name": "Target_2",
                    "type": "NUM",
                    "mode": "MIN",
                    "bounds": (0, 100),
                },
            ],
        }
    },
    "desirability_bad_weights2": {
        "objective": {
            "mode": "DESIRABILITY",
            "combine_func": "MEAN",
            "weights": [1, "ABC"],
            "targets": [
                {
                    "name": "Target_1",
                    "type": "NUM",
                    "mode": "MAX",
                    "bounds": (0, 100),
                },
                {
                    "name": "Target_2",
                    "type": "NUM",
                    "mode": "MIN",
                    "bounds": (0, 100),
                },
            ],
        }
    },
    "desirability_bad_weights3": {
        "objective": {
            "mode": "DESIRABILITY",
            "combine_func": "MEAN",
            "weights": "ABC",
            "targets": [
                {
                    "name": "Target_1",
                    "type": "NUM",
                    "mode": "MAX",
                    "bounds": (0, 100),
                },
                {
                    "name": "Target_2",
                    "type": "NUM",
                    "mode": "MIN",
                    "bounds": (0, 100),
                },
            ],
        }
    },
}


@pytest.mark.parametrize("config_update_key", invalid_config_updates.keys())
def test_invalid_config(config_basic_1target, config_update_key):
    """
    Ensure invalid configurations trigger defined exceptions.
    """
    config_update = invalid_config_updates[config_update_key]
    config_basic_1target.update(config_update)

    with pytest.raises((StrictValidationError, ValidationError)):
        # some raises are done at config and some others at baybe object level
        BayBE(BayBEConfig(**config_basic_1target))
