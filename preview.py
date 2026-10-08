# 미리보기용 단일 파일(preview.html): 이미지·썸네일을 파일 안에 넣어 외부 이미지가 막힌 곳에서도 보이게 한다
import os, base64
D = os.path.dirname(os.path.abspath(__file__))
os.environ['PREVIEW'] = '1'
src = open(os.path.join(D, 'build.py'), encoding='utf-8').read()
src = src.replace("def img(name): return 'assets/' + name",
                  "def img(name): return 'data:image/jpeg;base64,' + base64.b64encode(open(os.path.join(D, 'assets', name), 'rb').read()).decode()")
src = src.replace("os.path.join(D, 'index.html')", "os.path.join(D, 'preview.html')")
exec(compile(src, 'build.py', 'exec'), {'__file__': os.path.join(D, 'build.py'), '__name__': '__main__'})
