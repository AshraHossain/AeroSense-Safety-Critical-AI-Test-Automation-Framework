from src.test_runner.runner import parse_junit_xml, run_suite


def test_parse_junit_xml_extracts_pass_fail(tmp_path):
    xml = tmp_path / "results.xml"
    xml.write_text(
        '<?xml version="1.0"?>\n'
        '<testsuite tests="2" failures="1">\n'
        '  <testcase classname="tests.test_x" name="test_pass"></testcase>\n'
        '  <testcase classname="tests.test_x" name="test_fail">'
        '<failure message="boom">trace</failure></testcase>\n'
        "</testsuite>\n"
    )
    results = parse_junit_xml(xml)
    assert results == {"test_pass": "passed", "test_fail": "failed"}


def test_run_suite_executes_pytest_and_returns_results(tmp_path):
    target = tmp_path / "test_inline.py"
    target.write_text("def test_ok():\n    assert True\n")
    junit_path = tmp_path / "junit.xml"
    results = run_suite(target_dir=tmp_path, junit_path=junit_path)
    assert results == {"test_ok": "passed"}
