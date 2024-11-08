class DurationTooLongError(Exception):
    """Raised when the duration of the voice/video_note is over 600 seconds"""
    pass