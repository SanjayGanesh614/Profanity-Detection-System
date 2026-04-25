import pyaudio
import websockets
import asyncio
import json

# Configuration
URL = "ws://localhost:8000/ws/audio"
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

async def stream_audio():
    print(f"Connecting to {URL}...")
    try:
        async with websockets.connect(URL) as websocket:
            print("Connected! Start speaking...")
            
            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

            try:
                while True:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    await websocket.send(data)
                    
                    # Receive feedback if any (optional, backend sends segments)
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=0.01)
                        print(f"\nBackend: {response}")
                    except asyncio.TimeoutError:
                        pass
            except KeyboardInterrupt:
                print("Stopping...")
            finally:
                stream.stop_stream()
                stream.close()
                p.terminate()
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure the backend is running with 'python -m app.main'")

if __name__ == "__main__":
    asyncio.run(stream_audio())
