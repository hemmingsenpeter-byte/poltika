"""Registered transformations, one module per dataset (v0.2 Task 3.3).

Each module registers itself with `poltika.data.transform.transformation`
and is imported here, so importing `poltika.data.context` registers them
all.
"""

from poltika.data.transforms import (  # noqa: F401  (registration on import)
    stats_nz_births,
    stats_nz_census_2018,
    stats_nz_hes,
    stats_nz_net_worth,
)
