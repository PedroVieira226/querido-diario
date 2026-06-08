import unittest
from unittest.mock import MagicMock

from spidermon.exceptions import NotConfigured

from gazette.monitors import SuccessRateMonitor  # ainda não existe → ImportError


def make_monitor(stats, settings=None):
    """Helper: monta um monitor com data mockado."""
    monitor = SuccessRateMonitor("test_success_rate")
    monitor.data = MagicMock()
    monitor.data.stats = stats
    monitor.data.crawler.settings.get = lambda key, default=None: (settings or {}).get(
        key, default
    )
    return monitor


class TestSuccessRateMonitor(unittest.TestCase):
    def test_passes_when_rate_above_minimum(self):
        """Taxa 95% com limiar 90% → deve passar."""
        m = make_monitor(
            {
                "downloader/response_status_count/200": 95,
                "downloader/request_count": 100,
            }
        )
        m.test_success_rate()  # não deve lançar AssertionError

    def test_fails_when_rate_below_minimum(self):
        """Taxa 70% com limiar 90% → deve falhar."""
        m = make_monitor(
            {
                "downloader/response_status_count/200": 70,
                "downloader/request_count": 100,
            }
        )
        with self.assertRaises(AssertionError):
            m.test_success_rate()

    def test_skips_when_no_requests(self):
        """Sem requisições → não deve falhar (spider vazio ou filtrado)."""
        m = make_monitor({"downloader/request_count": 0})
        m.test_success_rate()  # não deve lançar

    def test_custom_threshold_via_setting(self):
        """Setting customizado QUERIDODIARIO_MIN_SUCCESS_RATE=0.8."""
        m = make_monitor(
            {
                "downloader/response_status_count/200": 82,
                "downloader/request_count": 100,
            },
            settings={"QUERIDODIARIO_MIN_SUCCESS_RATE": 0.8},
        )
        m.test_success_rate()  # 82% > 80% → passa

    def test_counts_all_2xx_codes(self):
        """200 + 201 + 204 somados devem contar como sucesso."""
        m = make_monitor(
            {
                "downloader/response_status_count/200": 80,
                "downloader/response_status_count/201": 10,
                "downloader/response_status_count/204": 5,
                "downloader/request_count": 100,
            }
        )
        m.test_success_rate()  # 95% > 90% → passa


if __name__ == "__main__":
    unittest.main()
