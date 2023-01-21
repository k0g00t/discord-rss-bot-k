from bs4 import BeautifulSoup
from reader import Entry, Feed, Reader, TagNotFoundError

from discord_rss_bot.markdown import convert_html_to_md
from discord_rss_bot.settings import get_reader


def get_images_from_entry(entry: Entry):
    """Get images from a entry.

    Args:
        entry: The entry to get the images from.

    Returns:
        Returns a list of images.
    """

    def return_image(found_images):
        soup: BeautifulSoup = BeautifulSoup(found_images, "html.parser")
        images = soup.find_all("img")
        for image in images:
            image_src = image["src"] or ""
            image_alt: str = "Link to image"
            if image.get("alt"):
                image_alt = image.get("alt")
            return [(image_src, image_alt)]

    images = []
    # Get the images from the summary with beautiful soup
    if entry.summary:
        images = return_image(entry.summary)

    # Get the images from the content with beautiful soup
    if entry.content:
        images = return_image(entry.content[0].value)

    # No images found
    return images


def try_to_replace(custom_message: str, template: str, replace_with: str) -> str:
    """Try to replace a tag in custom_message.

    Args:
        custom_message: The custom_message to replace tags in.
        feed: The feed to get the tags from.
        entry: The entry to get the tags from.
        tag: The tag to replace.

    Returns:
        Returns the custom_message with the tag replaced.
    """
    try:
        return custom_message.replace(template, replace_with)
    except TypeError:
        return custom_message


def replace_tags(feed: Feed, entry: Entry) -> str:
    """Replace tags in custom_message.

    Args:
        feed: The feed to get the tags from.
        entry: The entry to get the tags from.

    Returns:
        Returns the custom_message with the tags replaced.
    """
    custom_reader: Reader = get_reader()
    custom_message: str = get_custom_message(feed=feed, custom_reader=custom_reader)

    summary = ""
    content = ""
    if entry.summary:
        summary: str = entry.summary
        summary = convert_html_to_md(summary)

    if entry.content:
        for content_item in entry.content:
            content: str = content_item.value
            content = convert_html_to_md(content)

    if images := get_images_from_entry(entry=entry):
        first_image: str = images[0][0]
    else:
        first_image = ""

    list_of_replacements = [
        {"{{feed_author}}": feed.author},
        {"{{feed_added}}": feed.added},
        {"{{feed_last_exception}}": feed.last_exception},
        {"{{feed_last_updated}}": feed.last_updated},
        {"{{feed_link}}": feed.link},
        {"{{feed_subtitle}}": feed.subtitle},
        {"{{feed_title}}": feed.title},
        {"{{feed_updated}}": feed.updated},
        {"{{feed_updates_enabled}}": str(feed.updates_enabled)},
        {"{{feed_url}}": feed.url},
        {"{{feed_user_title}}": feed.user_title},
        {"{{feed_version}}": feed.version},
        {"{{entry_added}}": entry.added},
        {"{{entry_author}}": entry.author},
        {"{{entry_content}}": content},
        {"{{entry_content_raw}}": entry.content[0].value if entry.content else ""},
        {"{{entry_id}}": entry.id},
        {"{{entry_important}}": str(entry.important)},
        {"{{entry_link}}": entry.link},
        {"{{entry_published}}": entry.published},
        {"{{entry_read}}": str(entry.read)},
        {"{{entry_read_modified}}": entry.read_modified},
        {"{{entry_summary}}": summary},
        {"{{entry_summary_raw}}": entry.summary or ""},
        {"{{entry_title}}": entry.title},
        {"{{entry_updated}}": entry.updated},
        {"{{image_1}}": first_image},
    ]

    for replacement in list_of_replacements:
        for template, replace_with in replacement.items():
            custom_message = try_to_replace(custom_message, template, replace_with)

    return custom_message.replace("\\n", "\n")


def get_custom_message(custom_reader: Reader, feed: Feed) -> str:
    """Get custom_message tag from feed.

    Args:
        custom_reader: What Reader to use.
        feed: The feed to get the tag from.

    Returns:
        Returns the contents from the custom_message tag.
    """
    try:
        custom_message: str = str(custom_reader.get_tag(feed, "custom_message"))
    except TagNotFoundError:
        custom_message = ""
    except ValueError:
        custom_message = ""

    return custom_message
