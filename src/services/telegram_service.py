"""Telegram client service."""

import getpass
from typing import Optional
from telethon import TelegramClient
from telethon.errors import (
    FloodWaitError,
    SessionPasswordNeededError,
    PhotoInvalidError,
    WebpageCurlFailedError,
    MediaCaptionTooLongError,
)
from telethon.tl.types import Message
from loguru import logger
import asyncio

from src.config.settings import settings


class TelegramService:
    """Service for Telegram operations."""
    
    def __init__(self):
        """Initialize Telegram client."""
        self.client = TelegramClient(
            "telegram_session",
            settings.api_id,
            settings.api_hash,
        )
        self.channel_entity = None
    
    async def connect(self):
        """Connect to Telegram and authenticate."""
        logger.info("Connecting to Telegram...")
        await self.client.connect()
        
        if not await self.client.is_user_authorized():
            logger.info("First run: Authorization required")
            await self.client.send_code_request(settings.phone_number)
            
            code = input("Enter the code you received: ")
            
            try:
                await self.client.sign_in(settings.phone_number, code)
            except SessionPasswordNeededError:
                password = getpass.getpass("Enter your Telegram password (2FA): ")
                await self.client.sign_in(password=password)
            except Exception as e:
                logger.error(f"Failed to sign in: {e}")
                await self.disconnect()
                raise
        
        logger.success("Telegram authorization successful")
        
        # Get channel entity
        try:
            self.channel_entity = await self.client.get_entity(settings.channel_username)
            logger.success(f"Connected to channel: {settings.channel_username}")
        except Exception as e:
            logger.error(f"Failed to get channel entity '{settings.channel_username}': {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Telegram."""
        if self.client.is_connected():
            await self.client.disconnect()
            logger.info("Disconnected from Telegram")
    
    async def send_message(
        self,
        message: str,
        image_url: Optional[str] = None,
        retry_count: int = 3,
    ) -> Optional[Message]:
        """
        Send a message to the channel.
        
        Args:
            message: Message text (HTML formatted)
            image_url: Optional image URL
            retry_count: Number of retry attempts
        
        Returns:
            Sent message or None if failed
        """
        if not self.channel_entity:
            logger.error("Channel entity not initialized")
            return None
        
        for attempt in range(retry_count):
            try:
                # Try sending with image
                if image_url:
                    logger.info(f"Sending message with image: {image_url}")
                    sent_message = await self.client.send_file(
                        entity=self.channel_entity,
                        file=image_url,
                        caption=message,
                        parse_mode="html",
                        link_preview=True,
                    )
                    logger.success("Message with image sent successfully")
                    return sent_message
                
                # Send text-only
                else:
                    logger.info("Sending text-only message")
                    sent_message = await self.client.send_message(
                        entity=self.channel_entity,
                        message=message,
                        parse_mode="html",
                        link_preview=True,
                    )
                    logger.success("Text message sent successfully")
                    return sent_message
                
            except (PhotoInvalidError, WebpageCurlFailedError) as img_err:
                logger.warning(
                    f"Failed to send with image {image_url}: {img_err}. "
                    "Attempting text-only fallback."
                )
                # Retry without image
                try:
                    sent_message = await self.client.send_message(
                        entity=self.channel_entity,
                        message=message,
                        parse_mode="html",
                        link_preview=True,
                    )
                    logger.success("Text-only fallback sent successfully")
                    return sent_message
                except Exception as fallback_err:
                    logger.error(f"Text-only fallback failed: {fallback_err}")
                    if attempt < retry_count - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    return None
            
            except MediaCaptionTooLongError:
                logger.warning("Caption too long for image. Falling back to text-only mode.")
                # Fallback to text only (4096 limit instead of 1024)
                try:
                    sent_message = await self.client.send_message(
                        entity=self.channel_entity,
                        message=message,
                        parse_mode="html",
                        link_preview=True,
                    )
                    logger.success("Text-only fallback sent successfully (caption too long)")
                    return sent_message
                except Exception as fallback_err:
                    logger.error(f"Text-only fallback failed: {fallback_err}")
                    return None
            
            except FloodWaitError as fwe:
                wait_time = fwe.seconds
                logger.warning(f"Flood wait error: sleeping for {wait_time} seconds")
                await asyncio.sleep(wait_time + 5)
                continue
            
            except Exception as e:
                logger.error(f"Error sending message (attempt {attempt + 1}/{retry_count}): {e}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                return None
        
        logger.error("Failed to send message after all retry attempts")
        return None
    
    async def get_channel_info(self):
        """Get information about the channel."""
        if not self.channel_entity:
            logger.error("Channel entity not initialized")
            return None
        
        try:
            full_channel = await self.client.get_entity(self.channel_entity)
            logger.info(f"Channel: {full_channel.title}")
            logger.info(f"Username: @{full_channel.username}")
            return full_channel
        except Exception as e:
            logger.error(f"Failed to get channel info: {e}")
            return None
