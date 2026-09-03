from piem.version import get_version_info
from django.conf import settings
from django.templatetags.static import static

def version_context(request):
    public_url = settings.PUBLIC_SITE_URL
    return {
        "version_info": get_version_info(),
        "PIEM_VERSION": get_version_info()["version"],
        "PIEM_RELEASE_NAME": get_version_info()["release_name"],
        "PIEM_OG_IMAGE": f"{public_url}{static('core/og.png')}" if public_url else "",
    }
