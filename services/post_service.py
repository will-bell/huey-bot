from rq import Queue

from worker import conn

post_queue = Queue('post', connection=conn)
