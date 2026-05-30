import pytest

from app_streamlit.copy.disclaimers import assert_action_label_safe
from app_streamlit.copy.product_language import PRIMARY_ACTION_PREDICT, is_awkward_action_label


def test_predict_is_acceptable_manual_action_copy():
    assert PRIMARY_ACTION_PREDICT == "Predict"
    assert not is_awkward_action_label(PRIMARY_ACTION_PREDICT)
    assert_action_label_safe(PRIMARY_ACTION_PREDICT)


def test_request_educational_prediction_is_rejected():
    assert is_awkward_action_label("Request educational prediction")
    with pytest.raises(ValueError):
        assert_action_label_safe("Request educational prediction")
