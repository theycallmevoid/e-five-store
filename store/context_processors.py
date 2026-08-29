from .models import TrackingPixelSettings


def tracking_pixels(request):
    return {"tracking_pixels": TrackingPixelSettings.current()}
