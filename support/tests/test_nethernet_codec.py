import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "diagnostics"
sys.path.insert(0, str(TOOLS))

from nethernet_codec import decode_packet, encode_packet, encode_server_data  # noqa: E402


class NetherNetCodecTests(unittest.TestCase):
    def test_packet_round_trip(self):
        packet = encode_packet(2, 0x1122334455667788, b"payload")
        self.assertEqual((2, 0x1122334455667788, b"payload"), decode_packet(packet))

    def test_server_data_matches_android_golden_sample(self):
        encoded = encode_server_data(
            server_name="VenturaD4727",
            level_name="test",
            game_type=0,
            player_count=1,
            max_player_count=5,
            editor_world=False,
            hardcore=False,
            accepts_online_auth=True,
            accepts_self_signed_auth=True,
            nonce="e0aa4bbea63692f9",
            transport_layer=2,
            connection_type=4,
        )
        self.assertEqual(
            "060c56656e747572614434373237047465737400010000000500000000000101"
            "10653061613462626561363336393266390408",
            encoded.hex(),
        )


if __name__ == "__main__":
    unittest.main()
