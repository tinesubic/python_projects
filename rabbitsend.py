#!/usr/bin/env python
import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters(host='roadrunner.solvesall.com'))
channel = connection.channel()

channel.queue_declare(queue='value_change', durable=True)

data = {'message_type': 'value_change', 'timestamp': 12345678, 'client_id': '12AAAAA', 'content': {'MY_VALUE': '333'}}

channel.basic_publish(exchange='',
                      routing_key='value_change',
                      body=json.dumps(data))
print(" [x] Sent", json.dumps(data))
connection.close()
