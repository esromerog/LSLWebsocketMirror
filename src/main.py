from acquisition import Discovery, LSLMirror
import time

def main():
    discovery = Discovery(
        discard_timestamps=True,
        correct_timestamps=False
    )
    streams=[]

    while len(streams) == 0:
        input("Press any key to start LSL discovery")
        discovery.start()
        time.sleep(3)
        streams = list(discovery.streams_by_uid.keys())
        if len(streams) == 0:
            print("No streams found")
        else:
            print("Connected to: \n",streams)
        
    
    mirror = LSLMirror(discovery=discovery)
    input("Press any key to start websocket transmission")
    mirror.start()
    x = input("")

if __name__ == '__main__':
    main()