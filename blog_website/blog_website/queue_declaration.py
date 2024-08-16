import pika
import logging

def declare_queues():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        # Declare a queue with a specific name
        channel.queue_declare(queue='blog_queue', durable=True)

        connection.close()
        print("Queue declared successfully.")
    except pika.exceptions.AMQPConnectionError as e:
        logging.error(f"Failed to connect to RabbitMQ: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    declare_queues()
