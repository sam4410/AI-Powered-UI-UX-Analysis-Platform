import time
import streamlit as st

def timed_agent_task(agent_label, task_callable, log_container=None):
    """
    Measures execution time for a task (usually agent.run or task.run).
    - agent_label: Name of the agent or step
    - task_callable: Function or lambda to execute the agent's task
    - log_container: Optional streamlit container for inline updates

    Returns:
        output of the task + execution time in seconds
    """
    if log_container:
        log_container.markdown(f"⏳ `{agent_label}` is running...")

    start = time.time()
    try:
        result = task_callable()
        elapsed = time.time() - start
        msg = f"✅ `{agent_label}` completed in **{elapsed:.2f} seconds**"
        if log_container:
            log_container.success(msg)
        else:
            print(msg)
        return result, elapsed

    except Exception as e:
        elapsed = time.time() - start
        err_msg = f"❌ `{agent_label}` failed after {elapsed:.2f} seconds: {e}"
        if log_container:
            log_container.error(err_msg)
        else:
            print(err_msg)
        raise


def display_latency_summary(timing_dict):
    """
    Display total time summary in Streamlit sidebar
    """
    st.sidebar.markdown("### ⏱️ Agent Execution Times")
    for name, secs in timing_dict.items():
        st.sidebar.markdown(f"- `{name}`: **{secs:.2f}s**")
    st.sidebar.markdown("---")
