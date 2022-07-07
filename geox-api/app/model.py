import datetime
from enum import Enum
from typing import List, Optional

from pydantic import (
    BaseModel,
    Field,
    PositiveFloat,
    PositiveInt,
    root_validator,
    validator,
)


class EnumStringPrintMixin:
    """String enum mixin to print value."""

    def __str__(self):
        return str(self.value)


class TestSidedness(EnumStringPrintMixin, str, Enum):
    """Valid values of statistical test sidedness."""

    one_sided = "one_sided"
    two_sided = "two_sided"


class MarketSelectionInputDataRow(BaseModel):
    """Row of the input dataset for the  market"""

    location: str = Field(..., description="Location id.")
    date: datetime.date = Field(..., description="Date of the observation.")
    Y: float = Field(..., description="Response variable.")


class MarketSelectionInput(BaseModel):
    """Input parameters for the market selection input call."""

    data: List[MarketSelectionInputDataRow] = Field(..., description="Data ")
    # User intent
    cpic: PositiveFloat = Field(1, description="Cost per incremental conversion.")
    budget: Optional[PositiveFloat] = Field(
        None, description="Maximum budget that an experiment can spend."
    )
    include_locations: List[str] = Field(
        [], description="List of locations that must be included in treatment."
    )
    exclude_locations: List[str] = Field(
        [], description="List of locations that are not included in treatment."
    )
    # holdout: Optional[Tuple[int, int]] = Field(None, description="If `None`, then all market selections are used. Otherwise, it is list with the smallest and largest acceptable number of units in control.")
    # User intent with possible defaults
    treatment_periods: List[PositiveInt] = Field(
        [14, 28],
        description="List of the number of experiment lengths (in days) to simulation.",
    )
    num_locations: Optional[List[PositiveInt]] = Field(
        None, description="List of number of test markets to calculate power for."
    )
    effect_sizes: List[float] = Field(
        [0, 0.05, 0.10, 0.15, 0.20],
        description="Effect sizes for which to calculate simulations. These must all be in the same direction.",
    )
    # Details that could be ignored
    num_simulations: PositiveInt = Field(
        1, description="Number of simulations for each configuration to run."
    )
    side_of_test: TestSidedness = Field(TestSidedness.one_sided)
    alpha: float = Field(
        0.05, gt=0, lt=1, description="Statistical significance value."
    )

    @validator("include_locations", "exclude_locations", "effect_sizes", pre=True)
    def uniquify_list(cls, v):
        """Ensure locations are always unique."""
        return list(set(v))

    @validator("effect_sizes")
    def check_effect_sizes(cls, v: List[float]):
        """Check that all effect sizes have the same sign."""
        if any(x > 0 for x in v) and not all(x > 0 for x in v):
            raise ValueError(
                "Effect sizes must be either all positive or all negative."
            )
        return v

    @root_validator(pre=False)
    def check_include_locations(cls, values):
        """All include locations must be present in the set of locations."""
        include_locations = values.get("include_locations")
        if include_locations:
            locations = set(row.location for row in values.get("data"))
            missing_locations = set(include_locations) - locations
            if len(missing_locations) > 0:
                raise ValueError(
                    "Some locations in `include_locations` are not in `data`: {}".format(
                        ",".join(missing_locations)
                    )
                )
        return values

    @root_validator(pre=False)
    def check_exclude_locations(cls, values):
        """All include locations must be present in the set of locations."""
        exclude_locations = values.get("exclude_locations")
        if exclude_locations:
            locations = set(row.location for row in values.get("data"))
            missing_locations = set(exclude_locations) - locations
            if len(missing_locations) > 0:
                raise ValueError(
                    "Some locations in `exclude_locations` are not in `data`: {}".format(
                        ",".join(missing_locations)
                    )
                )
        return values
