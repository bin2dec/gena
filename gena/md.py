"""Markdown extensions."""

from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.util import etree
from slugify import slugify

from gena.settings import settings


__all__ = (
    'PostLinkInlineProcessor',
    'SettingsExtension',
    'SlugExtension',
)


class PostLinkInlineProcessor(InlineProcessor):
    """The processor for PostLinkExtension."""

    def handleMatch(self, m, data):
        a = etree.Element('a')
        a.text = m.group(2)
        a.set('href', f'{settings.BLOG_POSTS_URL}/{slugify(m.group(2))}')

        return a, m.start(0), m.end(0)


class PostLinkExtension(Extension):
    """Replace all [[ TITLE ]] with blog post links.

    For example, "[[ Gateway Ridge ]]" could be replaced with
    "<a href="https://example.com/posts/gateway-ridge">Gateway Ridge</a>".
    """

    def extendMarkdown(self, md):
        md.inlinePatterns.register(PostLinkInlineProcessor(r'(\[\[\s*(.+?)\s*\]\])'), 'gena_post_links', 200)


class SettingsInlineProcessor(InlineProcessor):
    """The processor for SettingsExtension."""

    def handleMatch(self, m, data):
        return settings.get(m.group(2), ''), m.start(0), m.end(0)


class SettingsExtension(Extension):
    """Replace all ::KEY:: with appropriate values from the settings dictionary."""

    def extendMarkdown(self, md):
        md.inlinePatterns.register(SettingsInlineProcessor(r'(::\s*([A-Z0-9_]+?)\s*::)'), 'gena_settings', 200)


class SlugInlineProcessor(InlineProcessor):
    """The processor for SlugsExtension."""

    def handleMatch(self, m, data):
        return slugify(m.group(2)), m.start(0), m.end(0)


class SlugExtension(Extension):
    """Slugify all ((STRING))."""

    def extendMarkdown(self, md):
        md.inlinePatterns.register(SlugInlineProcessor(r'(\(\(\s*(.+?)\s*\)\))'), 'gena_slugs', 210)
