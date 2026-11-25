"""Testes sem rede para os limites da coleta."""

import io
import time
import unittest

from collect_sources import read_limited


class CollectionLimitsTests(unittest.TestCase):
    def test_small_response_is_complete(self):
        self.assertEqual(
            read_limited(io.BytesIO(b"abc"), 8, time.monotonic() + 1),
            (b"abc", "saved"),
        )

    def test_large_response_stops_without_exceeding_allowance(self):
        response = io.BytesIO(b"x" * 50)
        payload, status = read_limited(response, 10, time.monotonic() + 1)
        self.assertEqual(
            (len(payload), status, response.tell()), (10, "limit_reached", 10)
        )

    def test_exact_limit_is_conservatively_rejected(self):
        self.assertEqual(
            read_limited(io.BytesIO(b"abcd"), 4, time.monotonic() + 1)[1],
            "limit_reached",
        )

    def test_expired_deadline_does_not_read(self):
        self.assertEqual(
            read_limited(io.BytesIO(b"abc"), 8, time.monotonic() - 1),
            (b"", "timeout"),
        )

    def test_partial_failure_retains_byte_count(self):
        class FailingResponse:
            calls = 0

            def read(self, size):
                self.calls += 1
                if self.calls == 1:
                    return b"abc"
                raise OSError("interrupted")

        self.assertEqual(
            read_limited(FailingResponse(), 8, time.monotonic() + 1),
            (b"abc", "download_error"),
        )


if __name__ == "__main__":
    unittest.main()
