import importlib.util
import os
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location("dogrula", os.path.join(ROOT, "dogrula.py"))
dogrula = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dogrula)

PASSIVE = '''metadata:
    language: v2-beta
    name: "Struts version disclosure"
    description: "x"
    author: "BurpUzman"
    tags: "passive"

given response then
    if {latest.response.body} matches "Apache Struts [0-9]+" then
        report issue:
            severity: info
            confidence: certain
            remediation: "hide version"
            detail: "version shown"
    end if
'''

HOST = '''metadata:
    language: v2-beta
    name: "Host callback"

define: collab = {generate_collaborator_address()}

given host then
    send request called probe:
        replacing headers: "Host": "x"
    if dns interactions then
        report issue and continue:
            severity: info
            confidence: certain
    else if http interactions then
        report issue:
            severity: high
            confidence: certain
    end if
'''

INSERTION = '''metadata:
    language: v2-beta
    name: "Quote probe"

given insertion point then
    send payload called quote_test:
        appending: "'"
    if not({quote_test.response.status_code} is {base.response.status_code}) then
        report issue:
            name: "Status changed"
            severity: medium
            confidence: tentative
            detail: "changed"
    end if
'''


def errs(text):
    return [m for _, m in dogrula.lint_bcheck(text)[0]]


class BCheckLint(unittest.TestCase):
    def test_valid_samples_pass(self):
        for sample in (PASSIVE, HOST, INSERTION):
            self.assertEqual(dogrula.lint_bcheck(sample)[0], [])

    def test_metadata_must_be_first(self):
        text = PASSIVE.replace("metadata:\n", "", 1)
        self.assertTrue(any("metadata" in m for m in errs(text)))

    def test_wrong_language_rejected(self):
        self.assertTrue(any("v2-beta" in m for m in errs(PASSIVE.replace("v2-beta", "v1-beta"))))

    def test_missing_name_rejected(self):
        text = PASSIVE.replace('    name: "Struts version disclosure"\n', "")
        self.assertTrue(any("name eksik" in m for m in errs(text)))

    def test_two_given_rejected(self):
        text = PASSIVE + "\ngiven request then\n"
        self.assertTrue(any("given" in m for m in errs(text)))

    def test_no_given_rejected(self):
        text = "metadata:\n    language: v2-beta\n    name: \"x\"\n"
        self.assertTrue(any("given" in m for m in errs(text)))

    def test_send_payload_needs_insertion_point(self):
        text = INSERTION.replace("given insertion point then", "given host then")
        self.assertTrue(any("send payload" in m for m in errs(text)))

    def test_send_request_invalid_with_given_response(self):
        text = HOST.replace("given host then", "given response then")
        self.assertTrue(any("send request" in m for m in errs(text)))

    def test_unbalanced_if_rejected(self):
        text = PASSIVE.replace("    end if\n", "")
        self.assertTrue(any("kapanmamis if" in m for m in errs(text)))

    def test_else_without_if_rejected(self):
        text = PASSIVE.replace("    if {latest", "    else then\n    if {latest")
        self.assertTrue(any("else" in m for m in errs(text)))

    def test_end_if_without_if_rejected(self):
        text = PASSIVE + "    end if\n"
        self.assertTrue(any("end if" in m for m in errs(text)))

    def test_bad_severity_rejected(self):
        text = PASSIVE.replace("severity: info", "severity: critical")
        self.assertTrue(any("severity" in m for m in errs(text)))

    def test_missing_confidence_rejected(self):
        text = PASSIVE.replace("            confidence: certain\n", "")
        self.assertTrue(any("confidence eksik" in m for m in errs(text)))

    def test_issue_property_order_enforced(self):
        text = PASSIVE.replace("severity: info\n            confidence: certain", "confidence: certain\n            severity: info")
        self.assertTrue(any("sira" in m for m in errs(text)))

    def test_no_report_issue_rejected(self):
        text = '''metadata:
    language: v2-beta
    name: "x"

given response then
    if {latest.response.body} matches "a" then
    end if
'''
        self.assertTrue(any("report issue yok" in m for m in errs(text)))

    def test_comment_line_rejected(self):
        self.assertTrue(any("yorum" in m for m in errs("# not\n" + PASSIVE)))

    def test_hash_inside_string_is_not_a_comment(self):
        text = PASSIVE.replace('"x"', '"has # inside"')
        self.assertEqual(dogrula.lint_bcheck(text)[0], [])

    def test_unterminated_string_rejected(self):
        text = PASSIVE.replace('detail: "version shown"', 'detail: "version shown')
        self.assertTrue(any("kapanmamis metin" in m for m in errs(text)))

    def test_keywords_inside_strings_are_ignored(self):
        text = PASSIVE.replace('"version shown"', '"end if given host then"')
        self.assertEqual(dogrula.lint_bcheck(text)[0], [])

    def test_model_attribution_rejected(self):
        text = PASSIVE.replace('"BurpUzman"', '"Written by Claude"')
        self.assertTrue(any("yasak ibare" in m for m in errs(text)))

    def test_reserved_variable_rejected(self):
        text = HOST.replace("define: collab", "define: latest")
        self.assertTrue(any("ayrilmis" in m for m in errs(text)))

    def test_reserved_request_name_rejected(self):
        text = HOST.replace("called probe", "called base")
        self.assertTrue(any("ayrilmis" in m for m in errs(text)))

    def test_insertion_point_variants_accepted(self):
        for given in ("given any insertion point then", "given query insertion point then",
                      "given header or cookie insertion point then"):
            text = INSERTION.replace("given insertion point then", given)
            self.assertEqual(dogrula.lint_bcheck(text)[0], [], given)

    def test_multiline_raw_request_string(self):
        text = HOST.replace('replacing headers: "Host": "x"', 'replacing path: "/a\nb"')
        self.assertEqual(dogrula.lint_bcheck(text)[0], [])

    def test_empty_file_rejected(self):
        self.assertTrue(dogrula.lint_bcheck("")[0])


class StrictSyntax(unittest.TestCase):
    def test_garbage_condition_rejected(self):
        text = PASSIVE.replace('{latest.response.body} matches "Apache Struts [0-9]+"', "nonsense")
        self.assertTrue(any("kosul" in m for m in errs(text)))

    def test_trailing_garbage_after_then_rejected(self):
        text = PASSIVE.replace('[0-9]+" then', '[0-9]+" then trailing garbage')
        self.assertTrue(any("then ile bitmeli" in m for m in errs(text)))

    def test_unknown_request_property_is_not_consumed(self):
        text = HOST.replace('replacing headers: "Host": "x"', "replacing invalid nonsense")
        errors, warnings = dogrula.lint_bcheck(text)
        self.assertTrue(warnings)

    def test_unknown_line_fails_run_all(self):
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "bchecks"))
            with open(os.path.join(root, "bchecks", "x.bcheck"), "w") as fh:
                fh.write(HOST.replace('replacing headers: "Host": "x"', "replacing invalid nonsense"))
            with open(os.path.join(root, ".gitignore"), "w") as fh:
                fh.write("\n".join(dogrula.REQUIRED_IGNORE) + "\n")
            dogrula.manifest_write(root)
            _, problems, _ = dogrula.run_all(root)
            self.assertTrue(any("dogrulanamayan" in p for p in problems))

    def test_innocent_word_containing_model_name_passes(self):
        text = PASSIVE.replace('"BurpUzman"', '"octopus"')
        self.assertEqual(dogrula.lint_bcheck(text)[0], [])

    def test_removing_and_method_properties_accepted(self):
        text = HOST.replace('replacing headers: "Host": "x"',
                            'replacing method: "GET"\n        removing headers: "Cookie"\n        removing body')
        errors, warnings = dogrula.lint_bcheck(text)
        self.assertEqual((errors, warnings), ([], []))


class ConfigJson(unittest.TestCase):
    def test_valid_config_passes(self):
        self.assertEqual(dogrula.check_config_json('{"crawler": {"depth": 5}, "passive": true}'), [])

    def test_invalid_json_rejected(self):
        self.assertTrue(dogrula.check_config_json("{"))

    def test_non_object_rejected(self):
        self.assertTrue(dogrula.check_config_json("[1]"))

    def test_secret_value_rejected(self):
        self.assertTrue(dogrula.check_config_json('{"login": {"password": "hunter2"}}'))
        self.assertTrue(dogrula.check_config_json('{"api_key": "abc"}'))

    def test_secret_list_and_nested_forms_rejected(self):
        self.assertTrue(dogrula.check_config_json('{"password": ["dummy"]}'))
        self.assertTrue(dogrula.check_config_json('{"headers": [{"name": "Authorization", "value": "Bearer dummy"}]}'))
        self.assertTrue(dogrula.check_config_json('{"a": {"b": ["Bearer abcdef123456"]}}'))
        self.assertTrue(dogrula.check_config_json('{"a": "eyJhbGciOi.eyJzdWIiOi.sig"}'))
        self.assertTrue(dogrula.check_config_json('{"cookie": {"x": "y"}}'))

    def test_boolean_and_numeric_secret_named_keys_pass(self):
        self.assertEqual(dogrula.check_config_json('{"cookie_handling": true, "token_length": 32}'), [])

    def test_subdirectory_json_is_scanned(self):
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "configs", "exported", "sub"))
            with open(os.path.join(root, "configs", "exported", "sub", "t.json"), "w") as fh:
                fh.write('{"password": "x"}')
            with open(os.path.join(root, ".gitignore"), "w") as fh:
                fh.write("\n".join(dogrula.REQUIRED_IGNORE) + "\n")
            dogrula.manifest_write(root)
            _, problems, _ = dogrula.run_all(root)
            self.assertTrue(any("sir olabilir" in p for p in problems))

    def test_empty_secret_and_lookalike_keys_pass(self):
        self.assertEqual(dogrula.check_config_json('{"password": "", "passive_checks": "on"}'), [])


class Manifest(unittest.TestCase):
    def make_root(self):
        tmp = tempfile.TemporaryDirectory()
        root = tmp.name
        os.makedirs(os.path.join(root, "bchecks"))
        with open(os.path.join(root, "bchecks", "a.bcheck"), "w") as fh:
            fh.write("a")
        return tmp, root

    def test_roundtrip_passes(self):
        tmp, root = self.make_root()
        with tmp:
            dogrula.manifest_write(root)
            self.assertEqual(dogrula.manifest_check(root), [])

    def test_tamper_detected(self):
        tmp, root = self.make_root()
        with tmp:
            dogrula.manifest_write(root)
            with open(os.path.join(root, "bchecks", "a.bcheck"), "w") as fh:
                fh.write("b")
            self.assertTrue(any("hash" in m for m in dogrula.manifest_check(root)))

    def test_unlisted_file_detected(self):
        tmp, root = self.make_root()
        with tmp:
            dogrula.manifest_write(root)
            with open(os.path.join(root, "bchecks", "b.bcheck"), "w") as fh:
                fh.write("b")
            self.assertTrue(any("manifestte yok" in m for m in dogrula.manifest_check(root)))

    def test_missing_file_detected(self):
        tmp, root = self.make_root()
        with tmp:
            dogrula.manifest_write(root)
            os.remove(os.path.join(root, "bchecks", "a.bcheck"))
            self.assertTrue(any("eksik" in m for m in dogrula.manifest_check(root)))

    def test_missing_manifest_detected(self):
        tmp, root = self.make_root()
        with tmp:
            self.assertEqual(dogrula.manifest_check(root), ["manifest.sha256 yok"])


class Gitignore(unittest.TestCase):
    def test_missing_entries_reported(self):
        with tempfile.TemporaryDirectory() as root:
            with open(os.path.join(root, ".gitignore"), "w") as fh:
                fh.write("*.burp\n")
            problems = dogrula.check_gitignore(root)
            self.assertTrue(any("auth/private/" in p for p in problems))
            self.assertFalse(any("*.burp" in p for p in problems))

    def test_missing_file_reported(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual(dogrula.check_gitignore(root), [".gitignore yok"])

    def test_negation_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            with open(os.path.join(root, ".gitignore"), "w") as fh:
                fh.write("\n".join(dogrula.REQUIRED_IGNORE) + "\n!*.har\n")
            self.assertTrue(any("negasyon" in p for p in dogrula.check_gitignore(root)))


if __name__ == "__main__":
    unittest.main()
