# Format design goals for prompt injection
def format_design_goals(goals_list):
    if not goals_list:
        return ""
    goals = ", ".join(goals_list)
    return f"The following redesign goals should be considered: {goals}. Please reflect these goals while analyzing or improving the UI."
