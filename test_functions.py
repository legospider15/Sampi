"""Run from the project folder: python3 -m unittest -v test_functions"""

import io
import unittest
from contextlib import redirect_stdout

from sampi import vm_run


class FunctionTests(unittest.TestCase):
    def test_parameter_shadows_global_without_changing_it(self):
        # A global named x currently overrides identity(5)'s argument, so the
        # program prints 100 twice. The argument should win inside the function,
        # while the global should keep its original value after the call.
        code = """
set x to 100
func identity x:
    return x
end
say(identity(5))
say(x)
"""
        output = io.StringIO()
        with redirect_stdout(output):
            vm_run(code)

        self.assertEqual(output.getvalue(), "5\n100\n")


if __name__ == "__main__":
    unittest.main()
