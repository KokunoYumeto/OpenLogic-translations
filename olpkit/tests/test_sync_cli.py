import contextlib
import io
import unittest
from unittest.mock import patch

from olpkit.cli import main


class SyncCliTests(unittest.TestCase):
    def test_same_pin_needs_no_output_directory_and_writes_nothing(self):
        output = io.StringIO()
        with patch('olpkit.cli.delta', return_value=({'files': []}, {})), \
                patch('olpkit.cli.plan') as write_plan, contextlib.redirect_stdout(output):
            result = main(['sync', 'plan', '--from', 'same', '--to', 'same'])
        self.assertEqual(result, 0)
        self.assertEqual(output.getvalue(), '0 changed files\n')
        write_plan.assert_not_called()

    def test_nonempty_delta_without_output_is_rejected_without_writing(self):
        errors = io.StringIO()
        with patch('olpkit.cli.delta', return_value=({'files': [{'path': 'content/a.tex'}]}, {})), \
                patch('olpkit.cli.plan') as write_plan, contextlib.redirect_stderr(errors):
            result = main(['sync', 'plan', '--from', 'old', '--to', 'new'])
        self.assertEqual(result, 1)
        self.assertIn('nonempty sync plan requires --out', errors.getvalue())
        write_plan.assert_not_called()


if __name__ == '__main__':
    unittest.main()
