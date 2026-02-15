import asyncio
from io import BytesIO
from pathlib import Path

from task._models.custom_content import Attachment, CustomContent
from task._utils.constants import API_KEY, DIAL_URL, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role


async def _put_image() -> Attachment:
    file_name = 'dialx-banner.png'
    project_root = Path(__file__).parent.parent.parent
    image_path = project_root / file_name
    mime_type_png = 'image/png'
    # TODO:
    #  1. Create DialBucketClient
    #  2. Open image file
    #  3. Use BytesIO to load bytes of image
    #  4. Upload file with client
    #  5. Return Attachment object with title (file name), url and type (mime type)
    async with DialBucketClient(api_key=API_KEY, base_url=DIAL_URL) as client:
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()
        file_info = await client.put_file(file_name, mime_type_png, BytesIO(image_bytes))

    print("file_info content:", file_info)
    return Attachment(
        title=file_info["name"],
        url=file_info["url"],
        type=file_info["contentType"]
    )


async def start() -> None:
    # TODO:
    #  1. Create DialModelClient
    #  2. Upload image (use `_put_image` method )
    #  3. Print attachment to see result
    #  4. Call chat completion via client with list containing one Message:
    #    - role: Role.USER
    #    - content: "What do you see on this picture?"
    #    - custom_content: CustomContent(attachments=[attachment])
    #  ---------------------------------------------------------------------------------------------------------------
    #  Note: This approach uploads the image to DIAL bucket and references it via attachment. The key benefit of this
    #        approach that we can use Models from different vendors (OpenAI, Google, Anthropic). The DIAL Core
    #        adapts this attachment to Message content in appropriate format for Model.
    #  TRY THIS APPROACH WITH DIFFERENT MODELS!
    #  Optional: Try upload 2+ pictures for analysis
    client = DialModelClient(
        endpoint=DIAL_CHAT_COMPLETIONS_ENDPOINT,
        deployment_name="gpt-4o",
        api_key=API_KEY
    )
    attachment = await _put_image()
    print("attachment content:", attachment)
    messages = [
        Message(
            role=Role.USER,
            content="What do you see on this picture?",
            custom_content=CustomContent(attachments=[attachment])
        )
    ]
    response = client.get_completion(messages=messages)
    print(f"\nAI Response: {response.content}")


if __name__ == "__main__":
    asyncio.run(start())
