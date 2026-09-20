import json
import unittest

from form import _schema_fields
from main import hidden_page_history


def schema_html(entries):
    return f"<script>var FB_PUBLIC_LOAD_DATA_ = {json.dumps([None, [None, entries]])};</script>"


class FormSchemaTests(unittest.TestCase):
    def test_uses_inner_answer_id_and_preserves_unicode_options(self):
        fields = _schema_fields(
            schema_html(
                [
                    [
                        111,
                        "Minimum order threshold",
                        None,
                        2,
                        [[222, [["₹100 – ₹300"], ["Above ₹300"]], 1]],
                    ]
                ]
            )
        )
        self.assertEqual(fields[0].name, "entry.222")
        self.assertEqual(fields[0].options, ["₹100 – ₹300", "Above ₹300"])

    def test_builds_history_for_sectioned_forms(self):
        html = schema_html(
            [
                [1, "Profile", None, 8],
                [2, "Question", None, 2, [[3, [["Yes"], ["No"]], 1]]],
                [4, "Operations", None, 8],
                [5, "Question", None, 2, [[6, [["Yes"], ["No"]], 1]]],
                [7, "Review", None, 8],
            ]
        )
        self.assertEqual(hidden_page_history(html), "0,1,2")


if __name__ == "__main__":
    unittest.main()
