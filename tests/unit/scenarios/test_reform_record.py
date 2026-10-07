"""Reform run identities retain changed payloads without a code commit."""

from poltika.scenarios.reform_record import reform_run_id, results_sha256


def test_identical_payloads_produce_the_same_reform_run_id() -> None:
    first = {"workbench": {"headline": [], "synthetic": True}, "distribution": []}
    reordered = {"distribution": [], "workbench": {"synthetic": True, "headline": []}}

    assert reform_run_id("scenario", ("option",), results_sha256=results_sha256(first)) == (
        reform_run_id("scenario", ("option",), results_sha256=results_sha256(reordered))
    )


def test_a_changed_payload_gets_a_new_id_when_option_ids_are_unchanged() -> None:
    # Installed deployments have no source commit. A corrected output can
    # therefore share the option run IDs with the earlier deployment.
    first = {"workbench": {"limitations": ["Original limitation"]}, "distribution": []}
    corrected = {"workbench": {"limitations": ["Corrected limitation"]}, "distribution": []}

    assert reform_run_id("scenario", ("same_option_id",), results_sha256=results_sha256(first)) != (
        reform_run_id("scenario", ("same_option_id",), results_sha256=results_sha256(corrected))
    )
