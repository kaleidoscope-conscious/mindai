from prometheus_client import start_http_server, Gauge, Counter

class CognitiveMetrics:
    def __init__(self):
        self.cognitive_cycles = Counter(
            'conscious_cognitive_cycles_total',
            'Total number of cognitive cycles'
        )
        
        self.memory_usage = Gauge(
            'conscious_memory_usage_bytes',
            'Current memory usage'
        )
        
        self.ethical_decisions = Counter(
            'conscious_ethical_decisions_total',
            'Ethical decisions made',
            ['decision_type']
        )

    def start_monitoring(self, port=9090):
        start_http_server(port)

# Initialize metrics collector
metrics = CognitiveMetrics()
