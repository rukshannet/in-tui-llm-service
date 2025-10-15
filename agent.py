from google.adk.agents import Agent
# Note: google.adk.agents.Agent is an alias for LlmAgent

# Create the main agent
travel_planner_agent = Agent(
    name="travel_planner_agent",
    model="gemini-2.5-flash", # Changed model to 2.5 flash
    instruction=(
        "You are a world-class travel planner and assistant. "
        "Your goal is to help users plan their dream vacations. "
        "You can use the available tools to get real-time information."
    ),
    # Add tools here if available, e.g., tools=[GoogleSearchTool()]
)
