"""Public demo status banner helpers."""


def format_demo_banner(status: dict) -> dict:
    release_status = status.get("release_status", "unavailable")
    if release_status == "full":
        message = "Public demo predictions are available with approved data and a real approved model."
    elif release_status == "degraded":
        message = "Full public prediction is not available. This degraded demo shows the product flow and limitations."
    else:
        message = "Public demo is unavailable."
    return {
        "release_status": release_status,
        "message": message,
        "limitations": status.get("demo_limitations", ""),
        "data_as_of": status.get("data_as_of"),
    }


def render_demo_banner(status: dict, st=None) -> dict:
    banner = format_demo_banner(status)
    if st is not None:
        if banner["release_status"] == "full":
            st.success(banner["message"])
        else:
            st.warning(banner["message"])
        if banner["data_as_of"]:
            st.caption(f"Demo data as of: {banner['data_as_of']}")
        if banner["limitations"]:
            st.caption(banner["limitations"])
    return banner

