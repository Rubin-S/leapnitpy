from django.http import HttpResponse, Http404
import logging

logger = logging.getLogger(__name__)


class CustomErrorHandlingMiddleware:
    """
    Middleware to handle any kind of error (404, server errors, etc.) and return a custom error message.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Process the request
            response = self.get_response(request)

            # Check if response status indicates an error
            if response.status_code >= 400:
                return self.handle_error(response.status_code)

            return response

        except Http404 as e:
            # Explicitly handle Http404 exceptions
            logger.warning(f"404 Not Found: {request.path}, Error: {e}")
            return self.handle_error(404)

        except Exception as e:
            # Handle any other unhandled exceptions
            logger.error(f"Unhandled Exception: {e}", exc_info=True)
            return self.handle_error(500)

    def process_exception(self, request, exception):
        """
        Catch exceptions missed by __call__ for a fallback mechanism.
        """
        if isinstance(exception, Http404):
            logger.warning(f"404 Error caught in process_exception: {exception}")
            return self.handle_error(404)

        logger.error(f"Exception caught in process_exception: {exception}", exc_info=True)
        return self.handle_error(500)

    def handle_error(self, status_code):
        """
        Generates a custom HttpResponse for error scenarios.
        """
        error_message = "Oops! Something's wrong, Let's go back?"
        return HttpResponse(
            error_message,
            status=status_code,
            content_type="text/plain"
        )
