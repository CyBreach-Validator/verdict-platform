import logging
import os
import threading
import time
from concurrent import futures

import grpc

try:
    from contracts import cybreach_service_pb2, cybreach_service_pb2_grpc
except ImportError:  # pragma: no cover - generated stubs are created during build
    cybreach_service_pb2 = None
    cybreach_service_pb2_grpc = None

logger = logging.getLogger(__name__)


class VerdictPublisherServiceServicer:
    def PublishVerdict(self, request, context):
        if cybreach_service_pb2 is None:
            context.abort(grpc.StatusCode.UNIMPLEMENTED, "gRPC stubs not generated")
        return cybreach_service_pb2.PublishVerdictResponse(
            verdict_id=request.verdict_id or request.action_id,
            status="accepted",
            accepted=True,
            error_detail="",
        )

    def HealthCheck(self, request, context):
        if cybreach_service_pb2 is None:
            context.abort(grpc.StatusCode.UNIMPLEMENTED, "gRPC stubs not generated")
        return cybreach_service_pb2.HealthResponse(
            status="ok",
            service="delta-verdict-publisher",
            timestamp=int(time.time()),
            version="1.0",
        )


def serve(host: str = "0.0.0.0", port: int = 50055):
    if cybreach_service_pb2 is None or cybreach_service_pb2_grpc is None:
        logger.warning(
            "Delta gRPC server not started because proto stubs are not generated. "
            "Run: python -m grpc_tools.protoc -Icontracts --python_out=. --grpc_python_out=. contracts/cybreach_service.proto"
        )
        return

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    cybreach_service_pb2_grpc.add_VerdictPublisherServiceServicer_to_server(
        VerdictPublisherServiceServicer(),
        server,
    )
    server.add_insecure_port(f"{host}:{port}")
    server.start()
    logger.info("[Delta gRPC] VerdictPublisherService listening on %s:%s", host, port)
    server.wait_for_termination()
