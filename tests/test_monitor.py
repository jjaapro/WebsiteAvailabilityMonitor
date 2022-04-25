import unittest
import inspect
from monitor import Monitor


class TestMonitor(unittest.TestCase):

    SITES = ["https://github.com/jjaapro"]
    CONFIG = 'tests/test_config.conf'

    def setUp(self):
        self.monitor = Monitor(
            self.SITES,
            config_path=self.CONFIG
        )

    def test_start_monitoring(self):
        self.monitor.start_monitoring()
        for thread in self.monitor.threads: 
            thread.join()


if __name__ == "__main__":
    test_src = inspect.getsource(TestMonitor)
    unittest.TestLoader.sortTestMethodsUsing = lambda _, x, y: (
        test_src.index(f"def {x}") - test_src.index(f"def {y}")
    )
    unittest.main()
