import asyncio
import struct
import time
import httpx
import traceback
import random

from app.core.feature_extractor import extract_features, features_to_vector
from app.ml.predictor import predict_query_risk

API_URL = "http://localhost:8000/api/log_proxy_query"

class PostgresProtocolParser:
    """A minimal parser for the PostgreSQL v3 Wire Protocol."""
    
    @staticmethod
    async def read_startup_message(reader):
        """Reads the initial StartupMessage sent by a Postgres client."""
        try:
            length_bytes = await reader.readexactly(4)
            length = struct.unpack("!I", length_bytes)[0]
            payload = await reader.readexactly(length - 4)
            version = struct.unpack("!I", payload[:4])[0]
            
            if version == 80877102:
                return "SSLRequest"
            elif version == 196608:
                return "StartupMessage"
            return "Unknown"
        except asyncio.IncompleteReadError:
            return None

    @staticmethod
    async def read_query_message(reader):
        """Reads a Query ('Q') message."""
        try:
            msg_type = await reader.readexactly(1)
            if msg_type != b'Q':
                return None, msg_type
            
            length_bytes = await reader.readexactly(4)
            length = struct.unpack("!I", length_bytes)[0]
            
            payload = await reader.readexactly(length - 4)
            query_string = payload[:-1].decode('utf-8', errors='ignore')
            return query_string, b'Q'
        except asyncio.IncompleteReadError:
            return None, None

async def send_log_to_backend(payload: dict):
    """Fire-and-forget logging to the backend."""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(API_URL, json=payload, timeout=2.0)
    except Exception as e:
        print(f"[Proxy] Warning: Failed to send log to backend: {e}")

async def process_client(reader, writer):
    addr = writer.get_extra_info('peername')
    user_ip = addr[0]
    print(f"[Proxy] Connection accepted from Postgres Client at {addr}")
    
    try:
        # 1. Handle Startup Handshake
        msg_type = await PostgresProtocolParser.read_startup_message(reader)
        
        if msg_type == "SSLRequest":
            writer.write(b'N')
            await writer.drain()
            msg_type = await PostgresProtocolParser.read_startup_message(reader)
            
        if msg_type == "StartupMessage":
            writer.write(struct.pack("!ciI", b'R', 8, 0))
            writer.write(struct.pack("!ciI", b'Z', 5, b'I'[0]))
            await writer.drain()
        else:
            print(f"[Proxy] Invalid Startup Message from {addr}")
            writer.close()
            return
            
        print(f"[Proxy] Handshake complete for {addr}. Listening for queries...")
        
        # 2. Intercept Queries
        while True:
            query, packet_type = await PostgresProtocolParser.read_query_message(reader)
            if not packet_type:
                break 
                
            if packet_type != b'Q':
                writer.write(struct.pack("!ciI", b'Z', 5, b'I'[0]))
                await writer.drain()
                continue
                
            if not query:
                continue
                
            print(f"[Proxy] Intercepted Query: {query}")
            start_time = time.time()
            
            q_upper = query.upper()
            
            estimated_rows = 10000 if any(kw in q_upper for kw in ["DROP", "DELETE", "TRUNCATE", "ALTER"]) else 1
            features = extract_features(query, user_ip, 14, estimated_rows)
            feature_vector = features_to_vector(features)
            
            # Predict risk inline!
            ml_result = predict_query_risk(feature_vector, -0.05)
            fuzzed_score = round(ml_result["score"] + random.uniform(-0.005, 0.005), 4)
            
            final_status = ml_result["status"]
            final_level = ml_result["level"]
            is_hardcoded = False

            if features.get("schema_change", 0) > 0 or any(kw in q_upper for kw in ["DROP", "TRUNCATE", "ALTER"]):
                final_status = "BLOCKED"
                final_level = "HIGH RISK"
                is_hardcoded = True
            elif "UNION" in q_upper or "1=1" in q_upper or "--" in q_upper:
                final_status = "BLOCKED"
                final_level = "HIGH RISK"
                is_hardcoded = True
            elif q_upper.count(" OR ") >= 2 or q_upper.count("SELECT") > 1:
                if final_status != "BLOCKED":
                    final_status = "FLAGGED"
                    final_level = "MEDIUM RISK"
                    is_hardcoded = True
                    
            execution_time = round((time.time() - start_time) * 1000, 2)
            q_type = q_upper.split()[0] if q_upper else "UNKNOWN"
            
            # Asynchronously send log to backend (fire-and-forget)
            log_payload = {
                "query": query,
                "user": user_ip,
                "q_type": q_type,
                "score": fuzzed_score,
                "status": final_status,
                "level": final_level,
                "execution_time_ms": execution_time,
                "features": features,
                "is_hardcoded": is_hardcoded
            }
            asyncio.create_task(send_log_to_backend(log_payload))

            if final_status == "BLOCKED":
                print(f"[Proxy] BLOCKED query from {addr}. Dropping connection.")
                err_msg = "FATAL: Security Policy Violation. Connection Dropped by Undersec ML Engine.\x00"
                err_payload = b'S' + b'FATAL\x00' + b'C' + b'XX000\x00' + b'M' + err_msg.encode() + b'\x00'
                writer.write(struct.pack("!ci", b'E', len(err_payload) + 4) + err_payload)
                await writer.drain()
                break # Forcefully kill socket
            else:
                print(f"[Proxy] ALLOWED query from {addr}.")
                writer.write(struct.pack("!ciI", b'C', 13, b'SELECT 1\x00'[0]))
                writer.write(struct.pack("!ciI", b'Z', 5, b'I'[0]))
                await writer.drain()
                
    except Exception as e:
        print(f"[Proxy] Error handling {addr}: {e}")
        traceback.print_exc()
    finally:
        print(f"[Proxy] Socket closed for {addr}")
        writer.close()
        await writer.wait_closed()

async def main():
    port = 5432
    try:
        server = await asyncio.start_server(process_client, '0.0.0.0', port)
    except OSError:
        port = 9000
        server = await asyncio.start_server(process_client, '0.0.0.0', port)
        
    print(f"=========================================")
    print(f"[Proxy] PostgreSQL Deep Packet Inspection Proxy")
    print(f"[Proxy] Listening on 0.0.0.0:{port}")
    print(f"=========================================")
    
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Proxy] Shutting down.")
