import base64
import requests
from linebot.v3.messaging import PushMessageRequest, TextMessage, ImageMessage
from typing import Optional

from utils.factory import setup_logger

logger = setup_logger(__name__)


class Notifier:
    def __init__(self, project_name: str, messaging_api=None):
        self.project_name = project_name
        self.messaging_api = messaging_api
        self.logger = setup_logger(__name__)

    def _log_success(self, method: str):
        self.logger.info(
            f"{method} sent successfully.", extra={"project": self.project_name}
        )

    def _log_failure(self, method: str, error: Exception):
        self.logger.error(
            f"Failed to send notification via {method}: {str(error)}",
            extra={"project": self.project_name},
        )

    def send_line(
        self, group_id: str, text_message: str, image_url: Optional[str] = None
    ):
        try:
            messages = [TextMessage(text=text_message)]
            if image_url:
                messages.append(
                    ImageMessage(
                        original_content_url=image_url,
                        preview_image_url=image_url,
                    )
                )
            request = PushMessageRequest(to=group_id, messages=messages)
            self.messaging_api.push_message(request)
            self._log_success("send_line")
        except Exception as e:
            self._log_failure("send_line", e)

    def send_ntfy(
        self, ntfy_topic: str, text_message: str, image_url: Optional[str] = None
    ):
        ntfy_url = f"https://thstplsu7001.nttp3.ths.com.tw/{ntfy_topic}"
        headers = {
            "Title": f"=?utf-8?b?{base64.b64encode(text_message.encode()).decode()}?=",
            "Tags": "warning",
        }
        if image_url:
            headers["Attach"] = image_url

        try:
            response = requests.post(
                ntfy_url, headers=headers, verify=False, timeout=10
            )
            response.raise_for_status()
            self._log_success("send_ntfy")
        except requests.exceptions.RequestException as e:
            self._log_failure("send_ntfy", e)
