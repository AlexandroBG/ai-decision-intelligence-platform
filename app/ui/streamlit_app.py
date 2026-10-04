import streamlit as st

from app.ui.client import (
    DecisionAPIClient,
    DecisionAPIError,
    DecisionAPIResponseError,
    DecisionAPITimeoutError,
    DecisionAPIUnavailableError,
    DecisionProviderRateLimitError,
    DecisionProviderUnavailableError,
)
from app.ui.formatting import (
    escape_markdown_currency,
)

DEFAULT_QUESTION = (
    "What is affecting revenue performance, and what should I investigate first?"
)


st.set_page_config(
    page_title="DecisionAI",
    page_icon="📊",
    layout="centered",
)


st.title("DecisionAI")

st.caption("Evidence-backed business decision intelligence.")


client = DecisionAPIClient()


with st.sidebar:
    st.subheader("System")

    try:
        health = client.health()

        st.success(f"{health.service} · {health.version}")

    except DecisionAPITimeoutError:
        st.error("DecisionAI API is responding too slowly.")

    except DecisionAPIUnavailableError:
        st.error("DecisionAI API is unavailable.")

        st.info("Start the FastAPI server before using the application.")

    except DecisionAPIError:
        st.error("DecisionAI health check failed.")


st.subheader("Business question")


question = st.text_area(
    "Ask DecisionAI",
    value=DEFAULT_QUESTION,
    height=120,
)


analyze_clicked = st.button(
    "Analyze",
    type="primary",
    use_container_width=True,
)


if analyze_clicked:
    normalized_question = question.strip()

    if not normalized_question:
        st.warning("Enter a business question before running the analysis.")

    else:
        with st.spinner("Analyzing business evidence..."):
            try:
                result = client.create_decision(question=normalized_question)

            except DecisionProviderRateLimitError:
                st.error("AI provider quota or rate limit has been reached.")

                st.info("Please try again after the provider quota resets.")

            except DecisionProviderUnavailableError:
                st.error("AI provider is temporarily unavailable.")

                st.info("Please try again later.")

            except DecisionAPITimeoutError:
                st.error("DecisionAI took too long to respond.")

                st.info("Please try again later.")

            except DecisionAPIUnavailableError:
                st.error("DecisionAI API is unavailable.")

                st.info("Check that the FastAPI server is running.")

            except DecisionAPIResponseError:
                st.error("DecisionAI returned an invalid response.")

                st.info(
                    "The request reached the API, "
                    "but the response could not be validated."
                )

            except DecisionAPIError as exc:
                st.error("DecisionAI could not complete the request.")

                st.caption(str(exc))

            else:
                if result.status == "completed":
                    st.subheader("Decision analysis")

                    formatted_answer = escape_markdown_currency(result.answer)

                    st.markdown(formatted_answer)

                    st.divider()

                    metric_columns = st.columns(3)

                    metric_columns[0].metric(
                        "Steps",
                        result.steps_used,
                    )

                    metric_columns[1].metric(
                        "Tool calls",
                        result.tool_calls,
                    )

                    metric_columns[2].metric(
                        "Evidence steps",
                        len(result.evidence_steps),
                    )

                    if result.evidence_steps:
                        st.caption(
                            "Evidence observations used: "
                            + ", ".join(str(step) for step in (result.evidence_steps))
                        )

                else:
                    st.error("DecisionAI could not complete the analysis.")

                    st.caption(
                        "The agent stopped before producing a validated final answer."
                    )
