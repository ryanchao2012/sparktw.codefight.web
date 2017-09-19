from channels import route_class
from combat.consumers import EvaluateConsumer

channel_routing = [
    route_class(EvaluateConsumer, path='^/evaluate/$')
]
