import base64


def png_imgfile2base64_url(filepath: str) -> str:
    encoded = base64.b64encode(open(filepath, 'rb').read()).decode('ascii')
    return f'data:image/png;base64,{encoded}'
