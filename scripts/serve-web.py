#!/usr/bin/env python3
"""ONE TRAIL · 前端静态服务（SPA 回退到 index.html）
用法: python3 scripts/serve-web.py [端口]   默认 8082
"""
import http.server
import os
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8082
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'dist')


class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def send_head(self):
        # 静态资源不存在时回退到 index.html（前端路由），真文件正常返回
        path = self.translate_path(self.path)
        if not os.path.exists(path) and '.' not in os.path.basename(self.path):
            self.path = '/index.html'
        return super().send_head()

    def end_headers(self):
        # HTML 不缓存，静态资源（带 hash 文件名）长缓存
        if self.path.endswith(('.js', '.css', '.png', '.jpg', '.svg', '.woff2')):
            self.send_header('Cache-Control', 'public, max-age=604800, immutable')
        else:
            self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

    def log_message(self, fmt, *args):
        pass  # 静默日志


if __name__ == '__main__':
    if not os.path.isdir(ROOT):
        sys.exit(f'[serve-web] 未找到 {ROOT}，请先 cd frontend && npm run build')
    with http.server.ThreadingHTTPServer(('0.0.0.0', PORT), SPAHandler) as srv:
        print(f'[serve-web] 服务 {ROOT} → http://0.0.0.0:{PORT}')
        srv.serve_forever()
