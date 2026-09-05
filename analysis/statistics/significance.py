"""
Two-Tailed Significance Level Classification.
"""
def classify_significance(p_value: float) -> str:
    if p_value < 0.001:
        return "EXTREMELY_SIGNIFICANT (p < 0.001)"
    elif p_value < 0.01:
        return "HIGHLY_SIGNIFICANT (p < 0.01)"
    elif p_value < 0.05:
        return "SIGNIFICANT (p < 0.05)"
    return "NOT_SIGNIFICANT (p >= 0.05)"
