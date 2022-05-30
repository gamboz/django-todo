"""
Django settings for django-todo + martor. Snippets.
"""

INSTALLED_APPS = [
    # ...
    'django.contrib.sites',
    'todo',
    'martor',
]


TEMPLATES = [
    {
        # ...
        'DIRS': [BASE_DIR / 'templates', ],
        'APP_DIRS': True,
        # ...
    },
]


# The absolute path to the directory where collectstatic will collect
# static files for deployment.
STATIC_ROOT = BASE_DIR / 'collected_static'


# Use mailcatcher for emails
# https://docs.djangoproject.com/en/1.11/topics/email/
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_USE_TLS = False

SITE_ID = 1

LOGIN_REDIRECT_URL = "/"
# LOGIN_URL
# Default: '/accounts/login/'
#
# The URL or named URL pattern where requests are redirected for login
# when using the login_required() decorator, LoginRequiredMixin, or
# AccessMixin.


# Restrict access to ALL todo lists/views to `is_staff` users.
#
# If False or unset, all users can see all views (but more granular
# permissions are still enforced within views, such as requiring staff
# for adding and deleting lists).
TODO_STAFF_ONLY = False




# Choices are: "semantic", "bootstrap"
MARTOR_THEME = 'bootstrap'

# Global martor settings
# Input: string boolean, `true/false`
MARTOR_ENABLE_CONFIGS = {
    'emoji': 'true',        # to enable/disable emoji icons.
    'imgur': 'true',        # to enable/disable imgur/custom uploader.
    'mention': 'false',     # to enable/disable mention
    'jquery': 'true',       # to include/revoke jquery (require for admin default django)
    'living': 'false',      # to enable/disable live updates in preview
    'spellcheck': 'false',  # to enable/disable spellcheck in form textareas
    'hljs': 'true',         # to enable/disable hljs highlighting in preview
}

# To show the toolbar buttons
MARTOR_TOOLBAR_BUTTONS = [
    'bold', 'italic', 'horizontal', 'heading', 'pre-code',
    'blockquote', 'unordered-list', 'ordered-list',
    'link', 'image-link', 'image-upload', 'emoji',
    'direct-mention', 'toggle-maximize', 'help'
]

# To setup the martor editor with title label or not (default is False)
MARTOR_ENABLE_LABEL = False

# Imgur API Keys
MARTOR_IMGUR_CLIENT_ID = 'your-client-id'
MARTOR_IMGUR_API_KEY   = 'your-api-key'

# Markdownify
MARTOR_MARKDOWNIFY_FUNCTION = 'martor.utils.markdownify' # default
MARTOR_MARKDOWNIFY_URL = '/martor/markdownify/' # default

# Markdown extensions (default)
MARTOR_MARKDOWN_EXTENSIONS = [
    'markdown.extensions.extra',
    'markdown.extensions.nl2br',
    'markdown.extensions.smarty',
    'markdown.extensions.fenced_code',

    # Custom markdown extensions.
    'martor.extensions.urlize',
    'martor.extensions.del_ins',      # ~~strikethrough~~ and ++underscores++
    'martor.extensions.mention',      # to parse markdown mention
    'martor.extensions.emoji',        # to parse markdown emoji
    'martor.extensions.mdx_video',    # to parse embed/iframe video
    'martor.extensions.escape_html',  # to handle the XSS vulnerabilities
]

# Markdown Extensions Configs
MARTOR_MARKDOWN_EXTENSION_CONFIGS = {}

# Markdown urls
MARTOR_UPLOAD_URL = '/martor/uploader/' # default
MARTOR_SEARCH_USERS_URL = '/martor/search-user/' # default

# Markdown Extensions
# MARTOR_MARKDOWN_BASE_EMOJI_URL = 'https://www.webfx.com/tools/emoji-cheat-sheet/graphics/emojis/'     # from webfx
MARTOR_MARKDOWN_BASE_EMOJI_URL = 'https://github.githubassets.com/images/icons/emoji/'                  # default from github
MARTOR_MARKDOWN_BASE_MENTION_URL = 'https://python.web.id/author/'                                      # please change this to your domain

# # If you need to use your own themed "bootstrap" or "semantic ui" dependency
# # replace the values with the file in your static files dir
# MARTOR_ALTERNATIVE_JS_FILE_THEME = "semantic-themed/semantic.min.js"   # default None
# MARTOR_ALTERNATIVE_CSS_FILE_THEME = "semantic-themed/semantic.min.css" # default None
# MARTOR_ALTERNATIVE_JQUERY_JS_FILE = "jquery/dist/jquery.min.js"        # default None

# URL schemes that are allowed within links
ALLOWED_URL_SCHEMES = [
    "file", "ftp", "ftps", "http", "https", "irc", "mailto",
    "sftp", "ssh", "tel", "telnet", "tftp", "vnc", "xmpp",
]



# TODO: understand this piece:
CSRF_COOKIE_HTTPONLY = False
