import pytest
import asyncio
import struct
from tcp_proxy import PostgresProtocolParser, process_client

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

class MockWriter:
    def __init__(self):
        self.buffer = bytearray()
        self.closed = False

    def get_extra_info(self, name):
        return ("192.168.1.100", 54321)

    def write(self, data):
        self.buffer.extend(data)

    async def drain(self):
        pass

    def close(self):
        self.closed = True

    async def wait_closed(self):
        self.closed = True

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

@pytest.mark.asyncio
async def test_tcp_proxy_drops_sqli_socket():
    # 1. Startup message (V3)
    startup = struct.pack("!II", 8, 196608)
    
    # 2. Malicious DROP query
    sqli = "DROP TABLE users;"
    sqli_bytes = sqli.encode('utf-8') + b'\x00'
    q_msg = b'Q' + struct.pack("!I", len(sqli_bytes) + 4) + sqli_bytes
    
    reader = MockReader(startup + q_msg)
    writer = MockWriter()
    
    await process_client(reader, writer)
    
    # Verify socket was closed after blocking SQLi
    assert writer.closed is True
    # Verify error packet b'E' was written to client before drop
    assert b'E' in writer.buffer
    assert b'FATAL: Security Policy Violation' in writer.buffer

@pytest.mark.asyncio
async def test_tcp_proxy_allowed_query_exact_protocol_bytes():
    # 1. Startup message (V3)
    startup = struct.pack("!II", 8, 196608)
    
    # 2. Legitimate query
    query = "SELECT 1;"
    q_bytes = query.encode('utf-8') + b'\x00'
    q_msg = b'Q' + struct.pack("!I", len(q_bytes) + 4) + q_bytes
    
    reader = MockReader(startup + q_msg)
    writer = MockWriter()
    
    await process_client(reader, writer)
    
    # Expected PostgreSQL v3 byte sequence:
    # 1. AuthOk: 'R' (1) + length (4) + 0 (4) = 9 bytes
    # 2. ReadyForQuery: 'Z' (1) + length (4) + 'I' (1) = 6 bytes
    # 3. CommandComplete: 'C' (1) + length (4) + 'SELECT 1\x00' (9) = 14 bytes
    # 4. ReadyForQuery: 'Z' (1) + length (4) + 'I' (1) = 6 bytes
    # Total = 35 bytes
    expected_auth = b'R\x00\x00\x00\x08\x00\x00\x00\x00'
    expected_rfq = b'Z\x00\x00\x00\x05I'
    expected_cc = b'C\x00\x00\x00\rSELECT 1\x00'
    expected_stream = expected_auth + expected_rfq + expected_cc + expected_rfq
    
    assert bytes(writer.buffer) == expected_stream
    assert writer.closed is True

@pytest.mark.asyncio
async def test_tcp_proxy_clean_terminate_message():
    startup = struct.pack("!II", 8, 196608)
    # Terminate ('X') message
    terminate_msg = b'X\x00\x00\x00\x04'
    
    reader = MockReader(startup + terminate_msg)
    writer = MockWriter()
    
    await process_client(reader, writer)
    
    # Only handshake responses should have been written, no error or extra ReadyForQuery
    assert writer.closed is True
    assert writer.buffer == b'R\x00\x00\x00\x08\x00\x00\x00\x00Z\x00\x00\x00\x05I'

@pytest.mark.asyncio
async def test_tcp_proxy_multi_query_session():
    startup = struct.pack("!II", 8, 196608)
    
    # First query
    q1 = "SELECT id, model FROM vehicles;"
    q1_b = q1.encode('utf-8') + b'\x00'
    q1_msg = b'Q' + struct.pack("!I", len(q1_b) + 4) + q1_b
    
    # Second query
    q2 = "UPDATE displays SET status = 'HEALTHY';"
    q2_b = q2.encode('utf-8') + b'\x00'
    q2_msg = b'Q' + struct.pack("!I", len(q2_b) + 4) + q2_b
    
    # Followed by Terminate
    term = b'X\x00\x00\x00\x04'
    
    reader = MockReader(startup + q1_msg + q2_msg + term)
    writer = MockWriter()
    
    await process_client(reader, writer)
    
    assert writer.closed is True
    assert b'C\x00\x00\x00\rSELECT 1\x00' in writer.buffer
    assert b'C\x00\x00\x00\rUPDATE 1\x00' in writer.buffer

