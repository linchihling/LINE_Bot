import traceback
from linebot.v3.messaging import (
    ReplyMessageRequest,
    TextMessage,
    ImageMessage,
    StickerMessage,
    ShowLoadingAnimationRequest,
    ButtonsTemplate,
    TemplateMessage,
    MessageAction,
    FlexCarousel,
    FlexMessage,
    FlexBubble,
    FlexBox,
    FlexButton,
)
from datetime import datetime, timedelta
import pytz
import os

from utils.fetch_url import fetch_folder_links, fetch_image_names, fetch_last_5_images
from utils.member_status import get_member_status, load_members, save_members
from logger import setup_logger 

logger = setup_logger("ty_bot", "logs/ty_bot.log")
members = load_members()

machine_dic = {
        "(軋一)":"rl1",
        "(軋二)":"rl2"
    }
def choice_mechine(message, token):
    primary_button = FlexButton(
        style='primary',
        action=MessageAction(label="軋一", text=f"(軋一){message[1:]}")
    )
    secondary_button = FlexButton(
        style='secondary',
        action=MessageAction(label="軋二", text=f"(軋二){message[1:]}")
    )

    bubble = FlexBubble(
        body=FlexBox(
            layout='vertical',
            spacing='md',
            contents=[primary_button, secondary_button]
        )
    )

    return ReplyMessageRequest(reply_token=token, messages=[FlexMessage(alt_text="機器選擇", contents=bubble)])

def get_image(machine_name, event):
    message = event.message.text
    token = event.reply_token
    
    tz = pytz.timezone('Asia/Taipei')
    now = datetime.now(tz)
    one_hour_ago = now - timedelta(hours=1)
    time_range = [one_hour_ago.strftime('%Y%m%d_%H'), now.strftime('%Y%m%d_%H')]
    
    machine = machine_dic.get(machine_name)
    url = os.path.join("https://linebot.tunghosteel.com:5003/" , machine)

    latest_5_images = fetch_last_5_images(machine)
    logger.info(f"{machine_name} successfully fetched the latest 5 images: {latest_5_images}")
    now_hour = latest_5_images[0].split('/')[0]
    if now_hour not in time_range:
        reply_message = [TextMessage(text="一小時內無影像")]
        logger.info(f"{machine_name} doesn't have any images from the past hour")

    elif message == machine_name + "最新影像":
        latest_image = latest_5_images[0]
        img_url = os.path.join(url, latest_image)
        # latest_image = "20241023_10/2024-10-23_10_01_21_63_900_D25.png"
        reply_message = [ImageMessage(original_content_url=img_url, preview_image_url=img_url)]
        logger.info(f"{machine_name} reply latest image: {latest_image}")
        
    elif message == machine_name + "最新影像五張":
        reply_message = [ImageMessage(original_content_url= os.path.join(url, img), preview_image_url= os.path.join(url, img)) for img in latest_5_images]
        logger.info(f"{machine_name} reply latest 5 images: {latest_5_images}")
    
    return ReplyMessageRequest(reply_token=token, messages=reply_message)

def create_date_menu(message, token):
    if message.startswith("(軋一)"):
        url = "https://linebot.tunghosteel.com:5003/rl1/"
        name = "!(軋一)影像:"
    elif message.startswith("(軋二)"):
        url = "https://linebot.tunghosteel.com:5003/rl2/"
        name = "!(軋二)影像:"

    folder_links = fetch_folder_links(url)[1:]
    folder_links = [link.split('_')[0] for link in folder_links]
    folder_links_date = sorted(list(set(folder_links)))

    def create_button(label, action):
        return FlexButton(
            style='link',
            height='sm',
            action=action
        )

    bubbles = []
    for i in range(0, len(folder_links_date), 10):
        buttons = []
        for link in folder_links_date[i:i+10]:
            buttons.append(create_button(str(link), MessageAction(label=f"{link}", text=name + link)))

        bubble = FlexBubble(
            footer=FlexBox(
                layout='vertical',
                spacing='sm',
                contents=buttons,
                flex=0
            )
        )
        bubbles.append(bubble)

    carousel = FlexCarousel(contents=bubbles)

    return ReplyMessageRequest(reply_token=token, messages=[FlexMessage(alt_text="Flex Message", contents=carousel)])

def create_time_menu(message, token):
    if message.startswith("!(軋一)"):
        url = "https://linebot.tunghosteel.com:5003/rl1/"
        name = "!(軋一)搜尋:"
    elif message.startswith("!(軋二)"):
        url = "https://linebot.tunghosteel.com:5003/rl2/"
        name = "!(軋二)搜尋:"

    folder_links = fetch_folder_links(url)[1:]
    date = message.split(':')[1]
    folder_links = [link.split('/')[0] for link in folder_links if link.startswith(date)]

    def create_button(label, action):
        return FlexButton(
            style='link',
            height='sm',
            action=action
        )

    bubbles = []
    for i in range(0, len(folder_links), 10):
        buttons = []
        for link in folder_links[i:i+10]:
            buttons.append(create_button(str(link), MessageAction(label=f"{link}", text=name + link)))

        bubble = FlexBubble(
            footer=FlexBox(
                layout='vertical',
                spacing='sm',
                contents=buttons,
                flex=0
            )
        )
        bubbles.append(bubble)

    carousel = FlexCarousel(contents=bubbles)

    return ReplyMessageRequest(reply_token=token, messages=[FlexMessage(alt_text="Flex Message", contents=carousel)])

def create_imgs_menu(message, token, client_id):

    search_date = message.split(":")[-1]
    
    if message.startswith("!(軋一)"):
        url = "https://linebot.tunghosteel.com:5003/rl1/"
        name = "(軋一)時間:"
    elif message.startswith("!(軋二)"):
        url = "https://linebot.tunghosteel.com:5003/rl2/"
        name = "(軋二)時間:"

    directory_url = url + search_date + '/' 
    logger.info(f"Client ID: {client_id}, (搜尋)Directory URL: {directory_url}")
    img_names = fetch_image_names(directory_url)[1:]                                         
    images_list = list({filename.split('_')[2] + '_' + filename.split('_')[2]: filename for filename in img_names}.values())                  # latest img every minutes

    def create_button(label, action):
        return FlexButton(
            style='link',
            height='sm',
            action=action
        )

    bubbles = []
    for i in range(0, len(images_list), 10):
        buttons = []
        for link in images_list[i:i+10]:
            buttons.append(create_button(str(link), MessageAction(label=f"{'_'.join(link.split('_')[1:4])}", text=name + link)))

        bubble = FlexBubble(
            footer=FlexBox(
                layout='vertical',
                spacing='sm',
                contents=buttons,
                flex=0
            )
        )
        bubbles.append(bubble)

    carousel = FlexCarousel(contents=bubbles)

    return ReplyMessageRequest(reply_token=token, messages=[FlexMessage(alt_text="Flex Message", contents=carousel)])

def show_img(message, token, client_id):
    if message.startswith("(軋一)"):
        url = "https://linebot.tunghosteel.com:5003/rl1/"
    elif message.startswith("(軋二)"):
        url = "https://linebot.tunghosteel.com:5003/rl2/"

    specify_url = url + message.split(":")[-1]
    logger.info(f"User: {client_id}, Directory URL: {specify_url}")
    image_message = [ImageMessage(original_content_url=specify_url, preview_image_url=specify_url)]

    return ReplyMessageRequest(reply_token=token, messages=image_message)

def handle_text_message(event, messaging_api):
    message = event.message.text
    token = event.reply_token
    # group_id = event.source.group_id
    client_id = event.source.user_id
    
    # loading animation
    show_loading_animation_request = ShowLoadingAnimationRequest(
        chat_id=client_id, loadingSeconds=5
    )
    messaging_api.show_loading_animation(show_loading_animation_request)
    # if get_member_status(messaging_api, event, logger):
    if message:
        # members = load_members()
        # member = members[client_id]
        try:
            if message == "!" or message == "！":
                function_menu = ReplyMessageRequest(
                    reply_token=token,
                    messages=[
                        TemplateMessage(
                            alt_text="ButtonsTemplate",
                            template=ButtonsTemplate(
                                thumbnail_image_url="https://doqvf81n9htmm.cloudfront.net/data/crop_article/118966/shutterstock_1122707477.jpg_1140x855.jpg",
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
                messaging_api.reply_message(function_menu)
            elif (
                message == "!最新影像"
                or message == "!最新影像五張"
                or message == "!自訂時間影像"
            ):
                mechine_menu = choice_mechine(message, token)
                try:
                    messaging_api.reply_message(mechine_menu)
                except Exception as e:
                    print(f'Error: {str(e)}')
            elif message.startswith("(軋一)自訂") or message.startswith("(軋二)自訂"):
                date_menu = create_date_menu(message, token)
                messaging_api.reply_message(date_menu)
            elif message.startswith("!(軋一)影像:") or message.startswith("!(軋二)影像:"):
                time_menu = create_time_menu(message, token)
                messaging_api.reply_message(time_menu)
            elif message.startswith("!(軋一)搜尋:") or message.startswith("!(軋二)搜尋:"):
                imgs_menu = create_imgs_menu(message, token, client_id)
                messaging_api.reply_message(imgs_menu)
            elif message.startswith("(軋一)最新") :
                img = get_image("(軋一)", event)
                messaging_api.reply_message(img)
            elif message.startswith("(軋二)最新") :
                img = get_image("(軋二)", event)
                messaging_api.reply_message(img)
            elif message.startswith("(軋一)時間") or message.startswith("(軋二)時間"):
                png = show_img(message, token, client_id)
                messaging_api.reply_message(png)
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error: {str(e)}")
            messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=token,
                    messages=[TextMessage(text="Unable to process your request")],
                )
            )
    # else:
    #     messaging_api.reply_message(
    #         ReplyMessageRequest(
    #             reply_token=token,
    #             messages=[TextMessage(text="You are not a member, please contact the developer.")],
    #         )
    #     )
    #     logger.info(f"User: {client_id}, message: {message}")

def handle_follow(event, messaging_api):
    user_id = event.source.user_id
    sticker_message = StickerMessage(package_id="6370", sticker_id="11088021")
    messaging_api.push_message(
        user_id, messages=[TextMessage(text="輸入!開啟功能選單"), sticker_message]
    )
    logger.info(f"New follower: {user_id}")

