"""Offline OCR of a PNG with macOS Vision (no network, no credits). ocr(path, crop=(x0,y0,x1,y1)) -> [(text, (x,y))]."""
import sys
import Quartz, Vision
from Foundation import NSURL


def ocr(path, crop=None):
    url = NSURL.fileURLWithPath_(path)
    src = Quartz.CGImageSourceCreateWithURL(url, None)
    img = Quartz.CGImageSourceCreateImageAtIndex(src, 0, None)
    W, H = Quartz.CGImageGetWidth(img), Quartz.CGImageGetHeight(img)
    ox = oy = 0
    if crop:
        img = Quartz.CGImageCreateWithImageInRect(img, Quartz.CGRectMake(crop[0], crop[1], crop[2] - crop[0], crop[3] - crop[1]))
        ox, oy = crop[0], crop[1]; W, H = crop[2] - crop[0], crop[3] - crop[1]
    req = Vision.VNRecognizeTextRequest.alloc().init()
    req.setRecognitionLevel_(0); req.setUsesLanguageCorrection_(False)
    h = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(img, None)
    h.performRequests_error_([req], None)
    out = []
    for r in req.results() or []:
        c = r.topCandidates_(1)[0]; bb = r.boundingBox()
        out.append((str(c.string()), (int(ox + (bb.origin.x + bb.size.width / 2) * W), int(oy + (1 - bb.origin.y - bb.size.height / 2) * H))))
    return out


if __name__ == '__main__':
    for t, p in ocr(sys.argv[1]):
        print(p, t)
