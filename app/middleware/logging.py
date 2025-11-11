import time
import logging
import json
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from uuid import uuid4

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

logger = logging.getLogger(__name__)

class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """
    Monitoring endpoints excluded from logging to reduce disk writes.
    
    These endpoints are frequently polled by health check systems and
    don't need to be logged for normal operations.
    """
    EXCLUDED_PATHS = {
        '/api/v1/monitoring/health',
        '/api/v1/monitoring/ready',
        '/api/v1/monitoring/metrics',
    }

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid4())
        request.state.request_id = request_id

        start_time = time.time()
        
        # Skip logging for monitoring endpoints
        should_log = request.url.path not in self.EXCLUDED_PATHS

        log_data = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else None,
        }

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # Only log if not an excluded endpoint
            if should_log:
                log_data.update({
                    "status_code": response.status_code,
                    "process_time": f"{process_time:.3f}s",
                    "success": response.status_code < 400
                })
                logger.info(json.dumps(log_data))

            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.3f}"

            return response

        except Exception as e:
            process_time = time.time() - start_time
            
            # Only log errors if not an excluded endpoint
            if should_log:
                log_data.update({
                    "status_code": 500,
                    "process_time": f"{process_time:.3f}s",
                    "error": str(e),
                    "success": False
                })
                logger.error(json.dumps(log_data))
            raise
