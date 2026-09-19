import grpc
import hazard_pb2
import hazard_pb2_grpc
from spyne import Application, ComplexModel, ServiceBase, Unicode, rpc
from spyne.error import Fault
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication


class HazardModel(ComplexModel):
    hazard_id = Unicode
    status = Unicode
    message = Unicode


class HazardGatewayService(ServiceBase):
    @rpc(Unicode, Unicode, Unicode, _returns=HazardModel)
    def ReportHazard(ctx, title, description, region):
        try:
            with grpc.insecure_channel("grpc-server:50051") as channel:
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
            raise Fault(faultcode="Client", faultstring=e.details())

    # Additional operations (GetHazardStatus, ListHazards) follow the same try/except translation pattern.


application = Application(
    [HazardGatewayService],
    tns="hazard.gateway",
    in_protocol=Soap11(validator="lxml"),
    out_protocol=Soap11(),
)
wsgi_app = WsgiApplication(application)

if __name__ == "__main__":
    from wsgiref.simple_server import make_server

    server = make_server("0.0.0.0", 8000, wsgi_app)
    server.serve_forever()
