import threading

lock:             threading.Lock = threading.Lock()
thumbnailsServed: int            = 0
bytesServed:      int            = 0
processingTime:   float          = 0.0
requestsServed:   int            = 0
