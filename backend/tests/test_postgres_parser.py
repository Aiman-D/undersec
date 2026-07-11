import pytest
import asyncio
import struct
from tcp_proxy import PostgresProtocolParser

class MockReader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    async def readexactly(self, n: int) -> bytes:
        if self.pos + n > len(self.data):
            raise asyncio.IncompleteReadError(self.data[self.pos:], n)
        chunk = self.data[self.pos:self.pos+n]
        self.pos += n
        return chunk

@pytest.mark.asyncio
async def test_read_startup_message_ssl():
    # Length (4), Code for SSLRequest (80877102)
    payload = struct.pack("!II", 8, 80877102)
    reader = MockReader(payload)
    
    msg_type = await PostgresProtocolParser.read_startup_message(reader)
    assert msg_type == "SSLRequest"

@pytest.mark.asyncio
async def test_read_startup_message_v3():
    # Length (4), Code for V3 (196608)
    payload = struct.pack("!II", 8, 196608)
    reader = MockReader(payload)
    
    msg_type = await PostgresProtocolParser.read_startup_message(reader)
    assert msg_type == "StartupMessage"

@pytest.mark.asyncio
async def test_read_query_message():
    query_str = "SELECT 1;"
    query_bytes = query_str.encode('utf-8') + b'\x00'
    length = len(query_bytes) + 4
    
    # 'Q' (1), Length (4), Query String (N)
    payload = b'Q' + struct.pack("!I", length) + query_bytes
    reader = MockReader(payload)
    
    query, msg_type = await PostgresProtocolParser.read_query_message(reader)
    assert msg_type == b'Q'
    assert query == "SELECT 1;"
