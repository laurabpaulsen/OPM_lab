def determine_conversion_factor(unit:str, target_unit:str):
    """
    Determine the conversion factor between two units [m, cm, mm].
    """

    # check that the units are valid 
    if unit not in ["m", "cm", "mm"]:
        raise ValueError(f"Invalid unit {unit}")
    
    if target_unit not in ["m", "cm", "mm"]:
        raise ValueError(f"Invalid target_unit {target_unit}")

    # define the conversion factors
    conversion_factors = {
        "mm": 1000,
        "cm": 100,
        "m": 1
    }

    # calculate the conversion factor
    conversion_factor = conversion_factors[unit] / conversion_factors[target_unit]

    return conversion_factor
