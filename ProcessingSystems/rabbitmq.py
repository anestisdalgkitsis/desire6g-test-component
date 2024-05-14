# ProcessingSystems/rabbitmq.py

import asyncio
import os
import yaml
import logging
from aio_pika import connect, IncomingMessage, ExchangeType, Message
from .config import rabbitmq_host, input_topic, output_topic

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

async def process_message(message: IncomingMessage, message_counter):
    try:
        parsed_yaml = yaml.safe_load(message.body)
        clear_screen()
        logger.info(f"Processing message {message_counter}...")
        logger.info("Received and processing YAML data:")
        logger.info(parsed_yaml)

        modified_message = f"Processed: {message.body.decode()}"

        logger.info(f"Message {message_counter} processing complete.")
        
        # Manually acknowledge the message
        await message.ack()

        return modified_message
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        
        # Optionally reject the message in case of an error
        await message.reject(requeue=False)
        
        return None

async def consume_messages():
    try:
        # Connect to RabbitMQ
        connection = await connect(f"amqp://{rabbitmq_host}/")
        channel = await connection.channel()

        # Declare queues and get the default exchange
        input_queue = await channel.declare_queue(input_topic)
        output_queue = await channel.declare_queue(output_topic)
        default_exchange = channel.default_exchange

        message_counter = 0  # Initialize message counter here

        async def on_message(message: IncomingMessage):
            nonlocal message_counter  # Use nonlocal to modify the outer variable
            message_counter += 1
            modified_message = await process_message(message, message_counter)
            if modified_message:
                await default_exchange.publish(
                    Message(modified_message.encode()),
                    routing_key=output_topic  # Provide the routing_key here
                )
                logger.info(f"Processed message {message_counter}: {message.body.decode()}")

        await input_queue.consume(on_message)
        logger.info("Waiting for messages to process. To exit, press CTRL+C")

        return connection
    except Exception as e:
        logger.error(f"Error in consuming messages: {str(e)}")
        raise  # Reraise the exception to propagate it up the call stack
