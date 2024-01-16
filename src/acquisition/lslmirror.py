"""
LSL Module to mirror data from the buffer into a websocket
"""
from collections import deque
import logging
import json
from websockets.server import serve
import asyncio
import time
import threading
import numpy as np

class LSLMirror:
    def __init__(self, discovery, port=8333):
        self.discovery = discovery
        self.web_stream_dict = {}
        self.port = port  # Port for websocket. Default: 8333
        self.running = False
        self.thread = None

    async def _stream_to_websocket(self, websocket):
        """
        Retrieve the latest sample from the deque object for each stream.
        Create an object with those samples & information
        Stream that object to a websocket
        """
        print("Connected to", websocket)
        if not self.discovery.info_by_uid:
            return

        # If I wanted to perform some data processing
        # Go fetch data processing function using the stream info
        
        while self.running:
            for uid, stream in self.discovery.streams_by_uid.items():
                info = self.discovery.info_by_uid[uid]
                key = info.name()
                
                # if data is being processed, append the last result
                # if self.analysis.info_by_uid:
                #   self.web_stream_dict[key] = analysis.results_by_uid[uid]
                timestamp, samples = stream.buffer[-1]
                print(stream.buffer[-1])
                # Append last sample received

                # np.any(np.isnan(arr))

                if timestamp and not np.any(np.isnan(samples)):
                    if key not in self.web_stream_dict:
                        self.web_stream_dict[key] = {}
                    
                    # For future processing, I could pull values starting from the back based on s_rate
                    self.web_stream_dict[key]["timeseries"] = samples
                    self.web_stream_dict[key]["info"] = {"nominal_srate": info.nominal_srate(),
                                                         "type": info.type(),
                                                         "channel_count": info.channel_count(),
                                                         "channel_format": info.channel_format(),
                                                         "source_id": info.source_id()
                                                        }
                    self.web_stream_dict[key]["timestamp"] = timestamp
            try:
                await websocket.send(json.dumps(self.web_stream_dict))
            except:
                print("Disconnected from", websocket)
                break
            await asyncio.sleep(0.000001)

    async def _create_websocket(self):
        async with serve(lambda w: self._stream_to_websocket(websocket=w), "localhost", self.port):
            await asyncio.Future()

    def _async_server_thread(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._create_websocket())

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._async_server_thread, daemon=True)
        self.thread.start()

    def stop(self):
        if not self.thread:
            return True

        self.running = False
        if threading.current_thread() is not self.thread:
            self.thread.join()

        self.thread = None


    
