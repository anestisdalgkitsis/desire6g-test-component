# processor.py

import asyncio
from ProcessingSystems.rabbitmq import consume_messages

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    connection = loop.run_until_complete(consume_messages())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Processor interrupted, closing connection...")
    finally:
        loop.run_until_complete(connection.close())
