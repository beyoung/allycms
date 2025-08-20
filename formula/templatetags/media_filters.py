from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def is_image(file_type):
    """检查文件类型是否为图片"""
    image_types = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp']
    return file_type.lower() in image_types

@register.filter
@stringfilter
def is_video(file_type):
    """检查文件类型是否为视频"""
    video_types = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv']
    return file_type.lower() in video_types

@register.filter
@stringfilter
def is_audio(file_type):
    """检查文件类型是否为音频"""
    audio_types = ['.mp3', '.wav', '.ogg', '.aac', '.flac', '.wma']
    return file_type.lower() in audio_types

@register.filter
@stringfilter
def get_media_icon(file_type):
    """获取媒体文件的图标类名"""
    if is_image(file_type):
        return 'fas fa-image'
    elif is_video(file_type):
        return 'fas fa-video'
    elif is_audio(file_type):
        return 'fas fa-music'
    else:
        return 'fas fa-file'

