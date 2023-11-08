import os
from concurrent import futures

import grpc
import user_service.user_service_pb2_grpc as user_pb2_grpc
from dotenv import load_dotenv

from user_info_service import UssrSservice

load_dotenv()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(UssrSservice(), server)
    server.add_insecure_port(f'[::]:{os.getenv("USER_SERVICE_PORT")}')
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
