import json
from pathlib import Path


EVAL_DIR = Path("agents/portfolio_manager/evals")


def test_context_routing_evalset_has_required_adk_shape() -> None:
    evalset_path = EVAL_DIR / "context_routing.evalset.json"
    payload = json.loads(evalset_path.read_text(encoding="utf-8"))

    assert payload["eval_set_id"] == "portfolio_manager_context_routing"
    assert payload["eval_cases"]

    for eval_case in payload["eval_cases"]:
        assert eval_case["eval_id"]
        assert eval_case["session_input"]["app_name"] == "portfolio_manager"
        assert eval_case["conversation"]

        for invocation in eval_case["conversation"]:
            assert invocation["user_content"]["role"] == "user"
            assert invocation["user_content"]["parts"][0]["text"]
            assert invocation["final_response"]["role"] == "model"
            assert invocation["final_response"]["parts"][0]["text"]
            tool_uses = invocation["intermediate_data"]["tool_uses"]
            assert tool_uses
            assert tool_uses[0]["name"] in {
                "load_private_context",
                "remember_session_fact",
                "forget_session_memory",
            }


def test_context_routing_eval_config_sets_lenient_starter_thresholds() -> None:
    config_path = EVAL_DIR / "context_routing_config.json"
    payload = json.loads(config_path.read_text(encoding="utf-8"))

    criteria = payload["criteria"]
    assert criteria["tool_trajectory_avg_score"] == 0.8
    assert criteria["response_match_score"] == 0.5
