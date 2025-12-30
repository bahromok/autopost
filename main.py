import asyncio
import logging
import os
import time
from datetime import datetime, timedelta
import getpass
from urllib.parse import urljoin

import feedparser
import requests
import translators as ts
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import (
    FloodWaitError,
    SessionPasswordNeededError,
    PhotoInvalidError,
    WebpageCurlFailedError,
    MediaCaptionTooLongError,
)

import settings

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- Helper Functions ---
def load_posted_links():
    """Loads the set of already posted links from the file."""
    try:
        with open(settings.POSTED_LINKS_FILE, "r") as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()


def save_posted_links(links_set):
    """Saves the set of posted links to the file."""
    with open(settings.POSTED_LINKS_FILE, "w") as f:
        for link in sorted(list(links_set)):
            f.write(link + "\n")


def contains_keywords(text, keywords):
    """Checks if the text contains any of the specified keywords."""
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)


def translate_text(
    text, target_lang="uz", source_lang="en", translator_backend="google"
):
    """Translates text using the 'translators' library."""
    if not text or not settings.ENABLE_TRANSLATION:
        return text
    try:
        logging.info(f"Attempting translation with backend: {translator_backend}")
        translated = ts.translate_text(
            text,
            translator=translator_backend,
            from_language=source_lang,
            to_language=target_lang,
        )
        logging.info(
            f"Translated to {target_lang} using {translator_backend}: {translated[:50]}..."
        )
        return translated
    except Exception as e:
        logging.error(
            f"Translation failed with backend {translator_backend}: {e}. Returning original text."
        )
        return text


def extract_image_url(entry, article_url):
    """Tries to find a suitable image URL from the RSS feed or article page."""
    if not settings.ENABLE_IMAGE_FETCHING:
        return None

    # 1. Check RSS feed for standard media tags
    for key in ["media_content", "media_thumbnail", "enclosures"]:
        if key in entry:
            for item in entry[key]:
                if "url" in item and "image" in item.get("medium", ""):
                    url = item["url"]
                    logging.info(f"Found image in RSS {key}: {url}")
                    return url
                if "href" in item and "image" in item.get("type", ""):
                    url = item["href"]
                    logging.info(f"Found image in RSS {key}: {url}")
                    return url

    # 2. If not in RSS, fetch the article page and look for an Open Graph image
    if article_url:
        logging.info(
            f"No image in RSS feed, attempting to fetch from page: {article_url}"
        )
        try:
            response = requests.get(
                article_url,
                headers=settings.REQUEST_HEADERS,
                timeout=settings.REQUEST_TIMEOUT,
                allow_redirects=True,
            )
            response.raise_for_status()

            content_type = response.headers.get("content-type", "").lower()
            if "html" not in content_type:
                logging.warning(
                    f"Content type is not HTML ({content_type}), skipping image parse for {article_url}"
                )
                return None

            soup = BeautifulSoup(response.text, "lxml")
            og_image_tag = soup.find("meta", property="og:image")

            if og_image_tag and og_image_tag.get("content"):
                image_url = og_image_tag["content"]
                if image_url.startswith("/"):
                    image_url = urljoin(article_url, image_url)
                logging.info(f"Found og:image on page: {image_url}")
                return image_url
            else:
                logging.info(f"No og:image tag found on page: {article_url}")

        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch article page {article_url}: {e}")
        except Exception as e:
            logging.error(f"Error parsing page {article_url} for image: {e}")

    return None


def format_base_message(entry):
    """Formats the core English message parts from an RSS entry."""
    title = entry.get("title", "No Title")
    link = entry.get("link", "#")
    summary = entry.get("summary", "")

    if "<" in summary:
        summary_soup = BeautifulSoup(summary, "html.parser")
        summary = summary_soup.get_text(separator=" ", strip=True)
    if len(summary) > 300:
        summary = summary[:300].rsplit(" ", 1)[0] + "..."

    return title, summary, link


def create_final_message(
    post_title,
    post_summary,
    en_post_title,
    en_post_summary,
    rupost_title,
    rupost_summary,
    article_link,
):
    """Constructs the final message text with translations and hashtags."""
    hashtags = set()
    combined_text_uz = (post_title + " " + post_summary).lower()
    if "sun'iy intellekt" in combined_text_uz or "si " in combined_text_uz:
        hashtags.add("#SuniyIntellekt")
    if "innovat" in combined_text_uz:
        hashtags.add("#Innovatsiya")
    if "kelajak" in combined_text_uz:
        hashtags.add("#Kelajak")
    if not hashtags:
        hashtags.add("#Yangilik")

    hashtag_string = " ".join(sorted(list(hashtags)))

    return (
        f"🇺🇿:\n<b>{post_title}</b>\n\n"
        f"{post_summary}\n\n"
        "======================================\n\n"
        f"🇺🇸:\n<b>{en_post_title}</b>\n\n"
        f"<i>{en_post_summary}</i>\n\n"
        "======================================\n\n"
        f"🇷🇺:\n<b>{rupost_title}</b>\n\n"
        f"<i>{rupost_summary}</i>\n\n"
        f"<a href='{article_link}'>Batafsil o'qish</a>\n\n"
        f"{hashtag_string}\n"
        f"📰 PressLeaf - https://t.me/pressleaf. "
    )


async def post_article(client, target_entity, entry, posted_links):
    """Processes a single article: formats, translates, and posts it."""
    link = entry.get("link")
    title = entry.get("title")

    if not link or not title or link in posted_links:
        return False

    published_dt = None
    if entry.get("published_parsed"):
        try:
            published_dt = datetime.fromtimestamp(
                time.mktime(entry.get("published_parsed"))
            )
        except Exception:
            pass

    cutoff_time = datetime.now() - timedelta(hours=settings.MAX_ARTICLE_AGE_HOURS)
    if published_dt and published_dt < cutoff_time:
        return False

    summary_en = entry.get("summary", "")
    if not (
        contains_keywords(title, settings.KEYWORDS)
        or contains_keywords(summary_en, settings.KEYWORDS)
    ):
        return False

    logging.info(f"Found relevant article: {title} ({link})")

    en_title, en_summary, article_link = format_base_message(entry)

    post_title = translate_text(en_title, target_lang="uz", translator_backend="bing")
    post_summary = translate_text(
        en_summary, target_lang="uz", translator_backend="bing"
    )
    rupost_title = translate_text(en_title, target_lang="ru", translator_backend="bing")
    rupost_summary = translate_text(
        en_summary, target_lang="ru", translator_backend="bing"
    )

    final_message = create_final_message(
        post_title,
        post_summary,
        en_title,
        en_summary,
        rupost_title,
        rupost_summary,
        article_link,
    )

    image_to_post = extract_image_url(entry, article_link)

    try:
        if image_to_post:
            await client.send_file(
                entity=target_entity,
                file=image_to_post,
                caption=final_message,
                parse_mode="html",
                link_preview=True,
            )
        else:
            await client.send_message(
                entity=target_entity,
                message=final_message,
                parse_mode="html",
                link_preview=True,
            )
        logging.info(f"Successfully posted to {settings.CHANNEL_USERNAME}: {en_title}")
        return True

    except (PhotoInvalidError, WebpageCurlFailedError) as img_err:
        logging.warning(
            f"Failed to send with image {image_to_post}: {img_err}. Attempting text-only post."
        )
        try:
            await client.send_message(
                target_entity, final_message, parse_mode="html", link_preview=True
            )
            logging.info(f"Successfully posted text-only fallback for {en_title}")
            return True
        except Exception as fallback_err:
            logging.error(
                f"Failed to send text-only fallback for {link}: {fallback_err}"
            )
    except MediaCaptionTooLongError:
        logging.warning(
            f"Caption too long for {link}. Trying to shorten and resend text-only."
        )
        # Implement shortening logic if necessary
    except FloodWaitError as fwe:
        logging.warning(f"Flood wait error: sleeping for {fwe.seconds} seconds.")
        await asyncio.sleep(fwe.seconds + 5)
    except Exception as e:
        logging.error(f"Generic error sending message for {link}: {e}")

    return False


async def fetch_and_post_news(client):
    """Fetches news from RSS feeds and posts new articles."""
    posted_links = load_posted_links()
    new_links_posted_count = 0

    try:
        target_entity = await client.get_entity(settings.CHANNEL_USERNAME)
    except Exception as e:
        logging.error(f"Failed to get entity '{settings.CHANNEL_USERNAME}': {e}")
        return

    logging.info(f"Checking {len(settings.RSS_FEEDS)} RSS feeds...")
    for feed_url in settings.RSS_FEEDS:
        try:
            logging.info(f"Parsing feed: {feed_url}")
            feed = feedparser.parse(feed_url)
            if feed.bozo:
                logging.warning(
                    f"Feed potentially malformed: {feed_url} - Reason: {feed.bozo_exception}"
                )

            for entry in feed.entries:
                if await post_article(client, target_entity, entry, posted_links):
                    posted_links.add(entry.get("link"))
                    new_links_posted_count += 1
                    save_posted_links(posted_links)
                    await asyncio.sleep(15)

        except Exception as e:
            logging.error(f"Failed to process feed {feed_url}: {e}")

    logging.info(f"Feed check complete. Posted {new_links_posted_count} new articles.")


async def main():
    """Main function to connect to Telegram and start the news posting loop."""
    load_dotenv()
    try:
        api_id = int(os.getenv("API_ID"))
        api_hash = os.getenv("API_HASH")
        phone_number = os.getenv("PHONE_NUMBER")
    except (TypeError, ValueError):
        logging.error(
            "Could not load credentials from environment variables. Please check your .env file."
        )
        return

    client = TelegramClient("noxrex_session", api_id, api_hash)

    logging.info("Connecting to Telegram...")
    await client.connect()

    if not await client.is_user_authorized():
        logging.info("First run: Authorization required.")
        await client.send_code_request(phone_number)
        code = input("Enter the code you received: ")
        try:
            await client.sign_in(phone_number, code)
        except SessionPasswordNeededError:
            password = getpass.getpass("Enter your Telegram password (2FA): ")
            await client.sign_in(password=password)
        except Exception as e:
            logging.error(f"Failed to sign in: {e}")
            await client.disconnect()
            return

    logging.info("Authorization successful.")

    while True:
        await fetch_and_post_news(client)
        logging.info(
            f"Scheduler finished. Waiting for {settings.CHECK_INTERVAL_SECONDS / 60:.0f} minutes."
        )
        await asyncio.sleep(settings.CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())
