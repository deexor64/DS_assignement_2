import uuid
from concurrent import futures

import grpc
import hazard_pb2
import hazard_pb2_grpc


class HazardService(hazard_pb2_grpc.HazardServiceServicer):
    def __init__(self):
        self.db = {}

    def ReportHazard(self, request, context):
        if not request.title or not request.region:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Title and Region are required")
            return hazard_pb2.HazardResponse()

        h_id = str(uuid.uuid4())
        self.db[h_id] = {
            "title": request.title,
            "region": request.region,
            "status": "Reported",
        }
        return hazard_pb2.HazardResponse(
            hazard_id=h_id, status="Reported", message="Successfully logged"
        )

    def GetHazardStatus(self, request, context):
        if request.hazard_id not in self.db:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Hazard ID not found")
            return hazard_pb2.HazardResponse()

        record = self.db[request.hazard_id]
        return hazard_pb2.HazardResponse(
            hazard_id=request.hazard_id, status=record["status"], message="Fetched"
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    hazard_pb2_grpc.add_HazardServiceServicer_to_server(HazardService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
