import traceback
import pytz
import os
from datetime import datetime, timedelta

from linebot.v3.messaging import (
    ReplyMessageRequest,
    TextMessage,
    ImageMessage,
    ShowLoadingAnimationRequest,
    ButtonsTemplate,
    TemplateMessage,
    MessageAction,
    FlexCarousel,
    FlexMessage,
    FlexBubble,
    FlexBox,
    FlexButton,
    StickerMessage,
)

from utils.fetch_url import fetch_folder_links, fetch_image_names, fetch_last_5_images
from utils.factory import setup_logger, load_config


class TyScrapBotHandler:
    def __init__(self, messaging_api):
        self.messaging_api = messaging_api
        self.config = load_config()
        self.machine_config = self.config["MACHINES"]
        self.logger = setup_logger(__name__)

    def _get_machine_info(self, message):
        for key, value in self.machine_config.items():
            if message.startswith(f"({key})"):
                return key, value
        return None, None

    def _send_reply(self, reply_token, messages, event_message=None):
        try:
            self.messaging_api.reply_message(
                ReplyMessageRequest(reply_token=reply_token, messages=messages)
            )
            return event_message or "OK"
        except Exception as e:
            return f"Error sending message: {str(e)}"

    def _choice_machine(self, message, reply_token):
        buttons = [
            FlexButton(
                style="primary" if idx == 0 else "secondary",
                action=MessageAction(label=label, text=f"({label}){message[1:]}"),
            )
            for idx, label in enumerate(self.machine_config.keys())
        ]
        bubble = FlexBubble(
            body=FlexBox(layout="vertical", spacing="md", contents=buttons)
        )
        return ReplyMessageRequest(
            reply_token=reply_token,
            messages=[FlexMessage(alt_text="機器選擇", contents=bubble)],
        )

    def _create_date_menu(self, message, reply_token):
        key, info = self._get_machine_info(message)
        if not info:
            return

        url, name = info["url"], info["name_image"]
        folder_links = [link.split("_")[0] for link in fetch_folder_links(url)[1:]]
        folder_links_date = sorted(set(folder_links))

        bubbles = []
        for i in range(0, len(folder_links_date), 10):
            buttons = [
                FlexButton(
                    style="link",
                    height="sm",
                    action=MessageAction(label=link, text=name + link),
                )
                for link in folder_links_date[i : i + 10]   # noqa E203
            ]
            bubbles.append(
                FlexBubble(
                    footer=FlexBox(
                        layout="vertical", spacing="sm", contents=buttons, flex=0
                    )
                )
            )

        return ReplyMessageRequest(
            reply_token=reply_token,
            messages=[
                FlexMessage(
                    alt_text="日期選擇", contents=FlexCarousel(contents=bubbles)
                )
            ],
        )

    def _create_time_menu(self, message, reply_token):
        for key, info in self.machine_config.items():
            if message.startswith(f"!({key})"):
                url, name = info["url"], info["name_search"]
                break
        else:
            return

        date = message.split(":")[1]
        folder_links = [
            link.split("/")[0]
            for link in fetch_folder_links(url)[1:]
            if link.startswith(date)
        ]

        bubbles = []
        for i in range(0, len(folder_links), 10):
            buttons = [
                FlexButton(
                    style="link",
                    height="sm",
                    action=MessageAction(label=link, text=name + link),
                )
                for link in folder_links[i : i + 10]  # noqa E203
            ]
            bubbles.append(
                FlexBubble(
                    footer=FlexBox(
                        layout="vertical", spacing="sm", contents=buttons, flex=0
                    )
                )
            )

        return ReplyMessageRequest(
            reply_token=reply_token,
            messages=[
                FlexMessage(
                    alt_text="時間選擇", contents=FlexCarousel(contents=bubbles)
                )
            ],
        )

    def _create_imgs_menu(self, message, reply_token, client_id):
        search_date = message.split(":")[-1]
        for key, info in self.machine_config.items():
            if message.startswith(f"!({key})"):
                url, name = info["url"], info["name_time"]
                break
        else:
            return

        directory_url = os.path.join(url, search_date + "/")
        img_names = fetch_image_names(directory_url)[1:]
        images_list = list({f.split("_")[2]: f for f in img_names}.values())

        bubbles = []
        for i in range(0, len(images_list), 10):
            buttons = [
                FlexButton(
                    style="link",
                    height="sm",
                    action=MessageAction(
                        label="_".join(link.split("_")[1:4]), text=name + link
                    ),
                )
                for link in images_list[i : i + 10]  # noqa E203
            ]
            bubbles.append(
                FlexBubble(
                    footer=FlexBox(
                        layout="vertical", spacing="sm", contents=buttons, flex=0
                    )
                )
            )

        return ReplyMessageRequest(
            reply_token=reply_token,
            messages=[
                FlexMessage(
                    alt_text="影像清單", contents=FlexCarousel(contents=bubbles)
                )
            ],
        )

    def _reply_new_image(self, event):
        message = event.message.text
        reply_token = event.reply_token
        tz = pytz.timezone("Asia/Taipei")
        now = datetime.now(tz)
        time_range = [
            (now - timedelta(hours=1)).strftime("%Y%m%d_%H"),
            now.strftime("%Y%m%d_%H"),
        ]

        key = message[0:4].strip("()")
        info = self.machine_config.get(key)
        if not info:
            return

        url, machine = info["url"], info["machine"]
        latest_5_images = fetch_last_5_images(machine)
        now_hour = latest_5_images[0].split("/")[0]

        if now_hour not in time_range:
            return self._send_reply(reply_token, [TextMessage(text="一小時內無影像")])
        elif "最新影像五張" in message:
            reply_message = [
                ImageMessage(
                    original_content_url=os.path.join(url, img),
                    preview_image_url=os.path.join(url, img),
                )
                for img in latest_5_images
            ]
        else:
            latest_image = latest_5_images[0]
            img_url = os.path.join(url, latest_image)
            reply_message = [
                ImageMessage(original_content_url=img_url, preview_image_url=img_url)
            ]

        return self._send_reply(reply_token, reply_message)

    def _reply_image(self, message, reply_token, client_id):
        date_time_name = message.split(":")[-1]
        date_time_part = date_time_name.split("_")
        date_time = f"{date_time_part[0].replace('-', '')}_{date_time_part[1]}"

        for key, info in self.machine_config.items():
            if message.startswith(f"({key})"):
                url = info["url"]
                break
        else:
            return

        img_url = os.path.join(url, date_time, date_time_name)
        reply_message = [
            ImageMessage(original_content_url=img_url, preview_image_url=img_url)
        ]
        return self._send_reply(reply_token, reply_message)

    def handle_text(self, event):
        message = event.message.text
        reply_token = event.reply_token
        client_id = event.source.user_id

        if hasattr(event.source, "group_id"):
            self.logger.info(
                f"Group({event.source.group_id}): {message}",
                extra={"project": "ty_scrap"},
            )
        else:
            self.logger.info(
                f"User({client_id}): {message}", extra={"project": "ty_scrap"}
            )

        self.messaging_api.show_loading_animation(
            ShowLoadingAnimationRequest(chat_id=client_id, loadingSeconds=5)
        )

        try:
            if message in ["!", "！"]:
                return self._send_reply(
                    reply_token,
                    [
                        TemplateMessage(
                            alt_text="功能選單",
                            template=ButtonsTemplate(
                                thumbnail_image_url="https://doqvf81n9htmm.cloudfront.net/data/crop_article/118966/shutterstock_1122707477.jpg_1140x855.jpg",  # noqa E501
                                title="鋼筋影像",
                                text="功能選單",
                                actions=[
                                    MessageAction(label="最新影像", text="!最新影像"),
                                    MessageAction(
                                        label="最新影像五張", text="!最新影像五張"
                                    ),
                                    MessageAction(
                                        label="自訂時間區間", text="!自訂時間影像"
                                    ),
                                ],
                            ),
                        )
                    ],
                )
            elif message in ["!最新影像", "!最新影像五張", "!自訂時間影像"]:
                return self._send_reply(
                    reply_token,
                    [self._choice_machine(message, reply_token).messages[0]],
                )
            elif any(message.startswith(f"({key})自訂") for key in self.machine_config):
                return self._send_reply(
                    reply_token,
                    [self._create_date_menu(message, reply_token).messages[0]],
                )
            elif any(
                message.startswith(f"!({key})影像:") for key in self.machine_config
            ):
                return self._send_reply(
                    reply_token,
                    [self._create_time_menu(message, reply_token).messages[0]],
                )
            elif any(
                message.startswith(f"!({key})搜尋:") for key in self.machine_config
            ):
                return self._send_reply(
                    reply_token,
                    [
                        self._create_imgs_menu(
                            message, reply_token, client_id
                        ).messages[0]
                    ],
                )
            elif any(message.startswith(f"({key})最新") for key in self.machine_config):
                return self._reply_new_image(event)
            elif any(message.startswith(f"({key})時間") for key in self.machine_config):
                return self._reply_image(message, reply_token, client_id)
        except Exception:
            traceback.print_exc()
            return self._send_reply(
                reply_token, [TextMessage(text="Unable to process your request")]
            )

    def handle_follow(self, event):
        user_id = event.source.user_id
        self.messaging_api.push_message(
            user_id,
            messages=[
                TextMessage(text="功能選單觀看即時影像"),
                StickerMessage(package_id="6370", sticker_id="11088021"),
            ],
        )
        self.logger.info(f"New follower: {user_id}", extra={"project": "ty_scrap"})
