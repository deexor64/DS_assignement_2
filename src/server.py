import uuid
from concurrent import futures

import grpc

from hazard import hazard_pb2, hazard_pb2_grpc


class HazardService(hazard_pb2_grpc.HazardServiceServicer):
    def __init__(self):
        # In-memory database to store hazards
        self.db = {}

    def ReportHazard(self, request, context):
        # Input Validation
        if not request.title or not request.region:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Validation Error: Title and Region are required")
            return hazard_pb2.HazardResponse()

        h_id = str(uuid.uuid4())
        self.db[h_id] = {
            "title": request.title,
            "region": request.region,
            "status": "Reported",
        }
        return hazard_pb2.HazardResponse(
            hazard_id=h_id, status="Reported", message="Successfully reported"
        )

    def GetHazardStatus(self, request, context):
        # Input Validation
        if not request.hazard_id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Validation Error: Hazard ID is required")
            return hazard_pb2.HazardResponse()

        if request.hazard_id not in self.db:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Not Found: Hazard ID does not exist")
            return hazard_pb2.HazardResponse()

        record = self.db[request.hazard_id]
        return hazard_pb2.HazardResponse(
            hazard_id=request.hazard_id,
            status=record["status"],
            message="Fetched status successfully",
        )

    def ListHazards(self, request, context):
        # Input Validation
        if not request.region:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Validation Error: Region is required to list hazards")
            return hazard_pb2.ListResponse()

        results = []
        for h_id, record in self.db.items():
            if record["region"] == request.region:
                results.append(
                    hazard_pb2.HazardResponse(
                        hazard_id=h_id, status=record["status"], message="Fetched"
                    )
                )
        return hazard_pb2.ListResponse(hazards=results)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    hazard_pb2_grpc.add_HazardServiceServicer_to_server(HazardService(), server)
    server.add_insecure_port("[::]:50051")
    print("gRPC Backend running on port 50051...")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
