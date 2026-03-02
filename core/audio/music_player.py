"""
Background music and sound effects.
Uses pygame.mixer. If pygame isn't installed, audio silently does nothing.
"""

try:
    import pygame.mixer as _mixer

    _mixer.init()
    _AUDIO_AVAILABLE = True
except Exception:
    _AUDIO_AVAILABLE = False

_current_track = None  # Track what's playing so we don't restart the same song


def play_music(path: str, volume: float = 0.5) -> None:
    """
    Play a music file on loop. Swaps cleanly if something else is already playing.
    path: relative path to the file, e.g. "assets/audio/music/kimaer.mp3"
    volume: 0.0 to 1.0
    """
    global _current_track
    if not _AUDIO_AVAILABLE:
        return
    if path == _current_track:
        return  # Already playing, don't restart it
    try:
        _mixer.music.load(path)
        _mixer.music.set_volume(volume)
        _mixer.music.play(loops=-1)  # -1 = loop forever
        _current_track = path
    except Exception:
        pass  # Bad path or unsupported format - just skip it


def stop_music() -> None:
    """Stop background music."""
    global _current_track
    if not _AUDIO_AVAILABLE:
        return
    _mixer.music.stop()
    _current_track = None


def play_sfx(path: str, volume: float = 0.8) -> None:
    """
    Play a one-shot sound effect. Stacks over music fine.
    path: relative path to the file, e.g. "assets/audio/sfx/sword_hit.mp3"
    volume: 0.0 to 1.0
    """
    if not _AUDIO_AVAILABLE:
        return
    try:
        sfx = _mixer.Sound(path)
        sfx.set_volume(volume)
        sfx.play()
    except Exception:
        pass
