# ProcessingSystems/config.py

import os

# RabbitMQ connection parameters
rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
input_topic = os.getenv("INPUT_TOPIC", "input_topic")
output_topic = os.getenv("OUTPUT_TOPIC", "output_topic")

# Kafka connection parameters
kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
