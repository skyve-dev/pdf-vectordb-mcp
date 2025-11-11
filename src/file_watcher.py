"""
File watcher module for monitoring PDF folder changes
"""
import logging
import time
from pathlib import Path
from typing import Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from .config import Config

logger = logging.getLogger(__name__)

class PDFFileHandler(FileSystemEventHandler):
    """Handler for PDF file system events"""

    def __init__(self, on_created: Callable, on_modified: Callable, on_deleted: Callable):
        """
        Initialize PDF file handler

        Args:
            on_created: Callback for file creation events
            on_modified: Callback for file modification events
            on_deleted: Callback for file deletion events
        """
        super().__init__()
        self.on_created_callback = on_created
        self.on_modified_callback = on_modified
        self.on_deleted_callback = on_deleted
        self.pending_events = {}  # For debouncing
        self.debounce_delay = 2  # seconds

    def _is_pdf(self, path: str) -> bool:
        """Check if the file is a PDF"""
        return path.lower().endswith('.pdf')

    def _debounce_event(self, event: FileSystemEvent) -> bool:
        """
        Debounce file events to avoid processing during file writes

        Args:
            event: File system event

        Returns:
            True if event should be processed, False if debounced
        """
        current_time = time.time()
        file_path = event.src_path

        # Check if we've seen this file recently
        if file_path in self.pending_events:
            last_time = self.pending_events[file_path]
            if current_time - last_time < self.debounce_delay:
                # Update the timestamp but don't process yet
                self.pending_events[file_path] = current_time
                return False

        # Update timestamp and process
        self.pending_events[file_path] = current_time
        return True

    def on_created(self, event: FileSystemEvent):
        """Handle file creation event"""
        if not event.is_directory and self._is_pdf(event.src_path):
            if self._debounce_event(event):
                logger.info(f"PDF created: {event.src_path}")
                try:
                    self.on_created_callback(Path(event.src_path))
                except Exception as e:
                    logger.error(f"Error handling created file {event.src_path}: {e}")

    def on_modified(self, event: FileSystemEvent):
        """Handle file modification event"""
        if not event.is_directory and self._is_pdf(event.src_path):
            if self._debounce_event(event):
                logger.info(f"PDF modified: {event.src_path}")
                try:
                    self.on_modified_callback(Path(event.src_path))
                except Exception as e:
                    logger.error(f"Error handling modified file {event.src_path}: {e}")

    def on_deleted(self, event: FileSystemEvent):
        """Handle file deletion event"""
        if not event.is_directory and self._is_pdf(event.src_path):
            logger.info(f"PDF deleted: {event.src_path}")
            try:
                self.on_deleted_callback(Path(event.src_path))
            except Exception as e:
                logger.error(f"Error handling deleted file {event.src_path}: {e}")

class PDFWatcher:
    """Watches a directory for PDF file changes"""

    def __init__(self, watch_directory: Path = None):
        """
        Initialize PDF watcher

        Args:
            watch_directory: Directory to watch (defaults to Config.PDF_FOLDER)
        """
        self.watch_directory = watch_directory or Config.PDF_FOLDER
        self.observer = None
        self.event_handler = None

        logger.info(f"Initialized PDFWatcher for directory: {self.watch_directory}")

    def start(self, on_created: Callable, on_modified: Callable, on_deleted: Callable):
        """
        Start watching the directory

        Args:
            on_created: Callback function for when a PDF is created
            on_modified: Callback function for when a PDF is modified
            on_deleted: Callback function for when a PDF is deleted
        """
        self.event_handler = PDFFileHandler(
            on_created=on_created,
            on_modified=on_modified,
            on_deleted=on_deleted
        )

        self.observer = Observer()
        self.observer.schedule(
            self.event_handler,
            str(self.watch_directory),
            recursive=False
        )
        self.observer.start()

        logger.info(f"Started watching directory: {self.watch_directory}")

    def stop(self):
        """Stop watching the directory"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("Stopped file watcher")

    def is_running(self) -> bool:
        """Check if the watcher is currently running"""
        return self.observer is not None and self.observer.is_alive()
