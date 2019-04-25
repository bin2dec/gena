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


POST_LINK_RE = r'(\[\[\s*(?P<title>.+?)\s*(?:#\s*(?P<anchor>.+?)\s*)?\]\])'

SETTINGS_RE = r'(::\s*([A-Z0-9_]+?)\s*::)'

SLUG_RE = r'(\(\(\s*(.+?)\s*\)\))'


class PostLinkInlineProcessor(InlineProcessor):
    """The processor for PostLinkExtension."""

    def handleMatch(self, m, data):
        title = m.group('title')
        anchor = m.group('anchor')

        href = f'{settings.BLOG_POSTS_URL}/{slugify(title)}'
        if anchor:
            href += f'/#{anchor}'

        a = etree.Element('a')
        a.text = title
        a.set('href', href)

        return a, m.start(0), m.end(0)


class PostLinkExtension(Extension):
    """Replace all [[ TITLE ]] with blog post links.

    For example, "[[ Gateway Ridge ]]" could be replaced with
    "<a href="https://example.com/posts/gateway-ridge">Gateway Ridge</a>".
    """

    def extendMarkdown(self, md):
        md.inlinePatterns.register(PostLinkInlineProcessor(POST_LINK_RE), 'gena_post_links', 200)


class SettingsInlineProcessor(InlineProcessor):
    """The processor for SettingsExtension."""

    def handleMatch(self, m, data):
        return settings.get(m.group(2), ''), m.start(0), m.end(0)


class SettingsExtension(Extension):
    """Replace all ::KEY:: with appropriate values from the settings dictionary."""

    def extendMarkdown(self, md):
        md.inlinePatterns.register(SettingsInlineProcessor(SETTINGS_RE), 'gena_settings', 200)


class SlugInlineProcessor(InlineProcessor):
    """The processor for SlugsExtension."""

    def handleMatch(self, m, data):
        return slugify(m.group(2)), m.start(0), m.end(0)


class SlugExtension(Extension):
    """Slugify all ((STRING))."""

    def extendMarkdown(self, md):
        md.inlinePatterns.register(SlugInlineProcessor(SLUG_RE), 'gena_slugs', 210)
