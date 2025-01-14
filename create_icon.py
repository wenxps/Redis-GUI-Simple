from PIL import Image, ImageDraw
import os

def create_redis_icon():
    # 创建一个64x64的图像，使用RGBA模式（支持透明度）
    size = 64
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # 设置Redis标志性的红色
    redis_red = "#D82C20"
    
    # 绘制一个圆形作为背景
    padding = 4
    draw.ellipse([padding, padding, size-padding, size-padding], fill=redis_red)
    
    # 保存图标
    if not os.path.exists('resources'):
        os.makedirs('resources')
    
    # 保存为PNG
    image.save('resources/icon.png')
    
    print("图标已创建：resources/icon.png")

if __name__ == "__main__":
    create_redis_icon() 