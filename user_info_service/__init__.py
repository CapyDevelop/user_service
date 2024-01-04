import logging
import os

import auth_service.authservice_pb2 as auth_pb2
import auth_service.authservice_pb2_grpc as auth_pb2_grpc
import db_service.db_handler_pb2 as db_pb2
import db_service.db_handler_pb2_grpc as db_pb2_grpc
import grpc
import school_service.school_service_pb2 as school_pb2
import school_service.school_service_pb2_grpc as school_pb2_grpc
import user_service.user_service_pb2 as user_pb2
import user_service.user_service_pb2_grpc as user_pb2_grpc
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - '
                           '%(levelname)s - %(message)s')

auth_service_channel = grpc.insecure_channel(
    f"{os.getenv('AUTH_SERVICE_HOST')}:{os.getenv('AUTH_SERVICE_PORT')}"
)
auth_service_stub = auth_pb2_grpc.AuthServiceStub(auth_service_channel)

school_service_channel = grpc.insecure_channel(
    f"{os.getenv('SCHOOL_SERVICE_HOST')}:{os.getenv('SCHOOL_SERVICE_PORT')}"
)
school_service_stub = school_pb2_grpc.SchoolServiceStub(school_service_channel)

db_service_channel = grpc.insecure_channel(
    f"{os.getenv('DB_SERVICE_HOST')}:{os.getenv('DB_SERVICE_PORT')}"
)
db_service_stub = db_pb2_grpc.DBServiceStub(db_service_channel)


class UssrSservice(user_pb2_grpc.UserServiceServicer):
    def get_rp(self, request, context):
        logging.info("[ Get rp ] - Get rp request. ----- START -----")
        logging.info("[ Get rp ] - request to auth_service")
        auth_info_request = auth_pb2.TokenRequest(uuid=request.capy_uuid)
        auth_info_response = auth_service_stub.get_token_by_uuid(auth_info_request)
        logging.info("[ Get rp ] - response from auth_service")
        if auth_info_response.status == 13:
            logging.info("[ Get rp ] - Error response from auth_service. Token Expired ----- END -----")
            return user_pb2.GetRpResponse(
                status=13
            )
        if auth_info_response.status != 0:
            logging.info("[ Get rp ] - Error response from auth_service. TOKEN OK ----- END -----")
            return user_pb2.GetRpResponse(
                status=1
            )
        logging.info("[ Get rp ] - request to school_service")
        school_info_request = school_pb2.GetRpRequest(
            access_token=auth_info_response.access_token
        )
        school_info_response = school_service_stub.get_rp_info(school_info_request)
        logging.info("[ Get rp ] - response from school_service")
        return user_pb2.GetRpResponse(
            coins=school_info_response.coins,
            prp=school_info_response.prp,
            crp=school_info_response.crp,
            level=school_info_response.level,
            first_name=school_info_response.first_name,
            last_name=school_info_response.last_name,
            login=school_info_response.login,
            status=0,
            description="Success"
        )

    def set_avatar(self, request, context):
        avatar = request.avatar
        uuid = request.uuid
        req = db_pb2.SetAvatarRequest(capy_uuid=uuid, avatar=avatar)
        res = db_service_stub.set_avatar(req)
        return user_pb2.SetAvatarResponse(status=res.status, description=res.description)

    def get_avatar(self, request, context):
        uuid = request.capy_uuid
        req = db_pb2.GetAvatarRequest(uuid=uuid)
        res = db_service_stub.get_avatar(req)
        return user_pb2.GetAvatarResponse(status=res.status, description=res.description, avatar=res.avatar)

    def get_peer_info(self, request, context):
        uuid = request.request_uuid
        nickname = request.nickname
        req = db_pb2.GetPeerInfoRequest(request_uuid=uuid, nickname=nickname)
        res = db_service_stub.get_peer_info(req)
        return user_pb2.GetPeerInfoResponse(
            status=res.status,
            description=res.description,
            avatar=res.avatar,
            first_name=res.first_name,
            last_name=res.last_name,
            login=res.login
        )

    def get_friend_stats(self, request, context):
        uuid = request.capy_uuid
        req = db_pb2.GetFriendStatsRequest(uuid=uuid)
        res = db_service_stub.get_friend_stats(req)
        return user_pb2.GetFriendStatsResponse(
            status=res.status,
            description=res.description,
            friends=res.friends,
            subscribers=res.subscribers,
        )

    def search_user(self, request, context):
        uuid = request.capy_uuid
        nickname = request.nickname
        req = db_pb2.SearchUserRequest(uuid=uuid, nickname=nickname)
        res = db_service_stub.search_user(req)
        return user_pb2.SearchUserResponse(
            status=res.status,
            description=res.description,
            friends=[user_pb2.SearchedUser(login=i.login, avatar=i.avatar) for i in res.friends],
            on_platform=[user_pb2.SearchedUser(login=i.login, avatar=i.avatar) for i in res.on_platform],
            out_platform=[user_pb2.SearchedUser(login=i.login, avatar=i.avatar) for i in res.out_platform],
        )

    def add_friend(self, request, context):
        uuid = request.capy_uuid
        login = request.nickname
        req = db_pb2.AddFriendRequest(uuid=uuid, login=login)
        res = db_service_stub.add_friend(req)
        return user_pb2.AddFriendResponse(status=res.status, description=res.description)
