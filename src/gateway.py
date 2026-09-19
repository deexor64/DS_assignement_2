import grpc
from spyne import Application, ComplexModel, Iterable, ServiceBase, Unicode, rpc
from spyne.error import Fault
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

from hazard import hazard_pb2, hazard_pb2_grpc


class HazardModel(ComplexModel):
    hazard_id = Unicode
    status = Unicode
    message = Unicode


class HazardGatewayService(ServiceBase):
    @rpc(Unicode, Unicode, Unicode, _returns=HazardModel)
    def ReportHazard(ctx, title, description, region):
        try:
            with grpc.insecure_channel("localhost:50051") as channel:
                stub = hazard_pb2_grpc.HazardServiceStub(channel)
                response = stub.ReportHazard(
                    hazard_pb2.ReportRequest(
                        title=title, description=description, region=region
                    )
                )
                return HazardModel(
                    hazard_id=response.hazard_id,
                    status=response.status,
                    message=response.message,
                )
        except grpc.RpcError as e:
            # Maps gRPC INVALID_ARGUMENT to a SOAP client fault
            raise Fault(faultcode="Client", faultstring=e.details())

    @rpc(Unicode, _returns=HazardModel)
    def GetHazardStatus(ctx, hazard_id):
        try:
            with grpc.insecure_channel("localhost:50051") as channel:
                stub = hazard_pb2_grpc.HazardServiceStub(channel)
                response = stub.GetHazardStatus(
                    hazard_pb2.StatusRequest(hazard_id=hazard_id)
                )
                return HazardModel(
                    hazard_id=response.hazard_id,
                    status=response.status,
                    message=response.message,
                )
        except grpc.RpcError as e:
            # Maps gRPC NOT_FOUND / INVALID_ARGUMENT to a SOAP client fault
            raise Fault(faultcode="Client", faultstring=e.details())

    @rpc(Unicode, _returns=Iterable(HazardModel))
    def ListHazards(ctx, region):
        try:
            with grpc.insecure_channel("localhost:50051") as channel:
                stub = hazard_pb2_grpc.HazardServiceStub(channel)
                response = stub.ListHazards(hazard_pb2.ListRequest(region=region))
                # Yield handles Spyne's requirement for Iterable returns (lists)
                for h in response.hazards:
                    yield HazardModel(
                        hazard_id=h.hazard_id, status=h.status, message=h.message
                    )
        except grpc.RpcError as e:
            raise Fault(faultcode="Client", faultstring=e.details())


application = Application(
    [HazardGatewayService],
    tns="hazard.gateway",
    in_protocol=Soap11(validator="lxml"),
    out_protocol=Soap11(),
)
wsgi_app = WsgiApplication(application)

if __name__ == "__main__":
    from wsgiref.simple_server import make_server

    print("SOAP Gateway running on http://localhost:8000 ...")
    server = make_server("0.0.0.0", 8000, wsgi_app)
    server.serve_forever()
