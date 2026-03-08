# -*- coding: utf-8 -*-
"""
Sentive 后端服务

提供句子搜索和随机获取的API接口，同时提供静态文件服务
作者：TREA_AI助手、云栖
最后修改时间：2026-03-07
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import random
import os


# 创建Flask应用实例，配置静态文件目录
app = Flask(__name__, static_folder='.', static_url_path='')
# 启用CORS跨域支持，允许前端访问
CORS(app)


@app.route('/')
def index():
    """
    提供主页index.html
    
    请求方法: GET
    参数: 无
    
    Returns:
        Response: index.html文件内容
    """
    return send_from_directory('.', 'index.html')


def load_online_presets():
    """
    加载在线背景预设（米哈游主题）
    
    Returns:
        list: 在线预设列表
    """
    return [
        {
            "id": "genshin-1",
            "name": "原神-蒙德",
            "url": "https://bkimg.cdn.bcebos.com/pic/5ab5c9ea15ce36d3d539339181a52d87e950352a1b41",
            "style": {
                "backgroundSize": "cover",
                "backgroundPosition": "center",
                "backgroundAttachment": "fixed"
            }
        },
        {
            "id": "genshin-2",
            "name": "原神-璃月",
            "url": "https://img.hongyoubizhi.com/picture/pages/regular/2022/08/31/14/101462757_p0_master1200.jpg?x-oss-process=image/resize,m_fill,w_10000",
            "style": {
                "backgroundSize": "cover",
                "backgroundPosition": "center",
                "backgroundAttachment": "fixed"
            }
        },
        {
            "id": "genshin-3",
            "name": "原神-稻妻",
            "url": "https://i0.hdslb.com/bfs/archive/639fb48fce96e2d6fd73bba4e79758eb70fbeb8d.jpg",
            "style": {
                "backgroundSize": "cover",
                "backgroundPosition": "center",
                "backgroundAttachment": "fixed"
            }
        },
        {
            "id": "honkai-1",
            "name": "崩坏-星穹铁道",
            "url": "https://i2.hdslb.com/bfs/archive/d434ac2a124528cbf5fcc3948e3f2a92342faed9.jpg",
            "style": {
                "backgroundSize": "cover",
                "backgroundPosition": "center",
                "backgroundAttachment": "fixed"
            }
        },
        {
            "id": "honkai-2",
            "name": "崩坏-星穹铁道2",
            "url": "https://i0.hdslb.com/bfs/archive/a1f4659e9fb3cd381dc330e3dc1ef321093eaa6b.jpg",
            "style": {
                "backgroundSize": "cover",
                "backgroundPosition": "center",
                "backgroundAttachment": "fixed"
            }
        }
    ]


def scan_local_images():
    """
    自动扫描img文件夹中的图片文件
    
    支持的格式: .jpg, .jpeg, .png, .gif, .webp
    
    Returns:
        list: 本地图片预设列表，每个预设包含id、name、url、style
    """
    img_folder = 'img'
    supported_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.JPG', '.JPEG', '.PNG', '.GIF', '.WEBP')
    local_presets = []
    
    # 检查img文件夹是否存在
    if not os.path.exists(img_folder):
        return local_presets
    
    # 遍历img文件夹中的所有文件
    for filename in sorted(os.listdir(img_folder)):
        # 检查文件扩展名是否支持
        if filename.endswith(supported_extensions):
            # 生成预设ID（移除扩展名，替换空格和括号为连字符）
            file_id = os.path.splitext(filename)[0]
            preset_id = f"local-{file_id.replace(' ', '-').replace('(', '-').replace(')', '')}"
            
            # 创建预设对象
            preset = {
                "id": preset_id,
                "name": f"本地图片 {file_id}",
                "url": f"img/{filename}",
                "style": {
                    "backgroundSize": "cover",
                    "backgroundPosition": "center",
                    "backgroundAttachment": "fixed"
                }
            }
            local_presets.append(preset)
    
    return local_presets


@app.route('/api/bg-presets', methods=['GET'])
def get_bg_presets():
    """
    获取所有背景预设（在线预设 + 本地图片）
    
    自动扫描img文件夹，动态生成本地图片预设
    
    请求方法: GET
    参数: 无
    
    Returns:
        dict: 预设配置对象
            {
                "presets": list,  # 所有预设列表
                "default": str,   # 默认预设ID
                "count": int      # 预设总数
            }
    
    Example:
        GET /api/bg-presets
        
        Response:
        {
            "presets": [
                {"id": "genshin-1", "name": "原神-蒙德", ...},
                {"id": "local-IMG_0948", "name": "本地图片 IMG_0948", ...}
            ],
            "default": "genshin-1",
            "count": 73
        }
    """
    # 加载在线预设
    online_presets = load_online_presets()
    
    # 扫描本地图片
    local_presets = scan_local_images()
    
    # 合并预设列表（在线预设在前，本地预设在后）
    all_presets = online_presets + local_presets
    
    return jsonify({
        "presets": all_presets,
        "default": "genshin-1",
        "count": len(all_presets)
    })


def load_sentences():
    """
    从JSON文件加载句子数据
    
    Returns:
        list: 句子对象列表，每个对象包含id、content、author、category字段
    
    Raises:
        FileNotFoundError: 当sentences.json文件不存在时
        json.JSONDecodeError: 当JSON格式错误时
    """
    with open("sentences.json", "r", encoding="utf-8") as f:
        return json.load(f)["sentences"]


@app.route("/api/random", methods=["GET"])
def random_sentence():
    """
    随机获取一条句子
    
    请求方法: GET
    参数: 无
    
    Returns:
        dict: 包含随机句子的响应
            {
                "sentence": {
                    "id": int,
                    "content": str,
                    "author": str,
                    "category": str
                }
            }
    
    Raises:
        500: 当加载句子数据失败时
    """
    sentences = load_sentences()
    # 使用random.choice随机选择一条句子
    sentence = random.choice(sentences)
    return jsonify({"sentence": sentence})


@app.route("/api/search", methods=["GET"])
def search():
    """
    根据关键词搜索句子
    
    请求方法: GET
    参数:
        kw (str): 搜索关键词，可选参数
    
    Returns:
        dict: 搜索结果响应
            {
                "results": [
                    {
                        "id": int,
                        "content": str,
                        "author": str,
                        "category": str
                    }
                ],
                "count": int  # 匹配结果数量
            }
    
    Raises:
        500: 当加载句子数据失败时
    """
    # 获取搜索关键词，默认为空字符串
    kw = request.args.get("kw", "").lower()
    sentences = load_sentences()
    
    # 在content、author、category三个字段中进行模糊搜索
    # 使用lower()确保搜索不区分大小写
    arr = [s for s in sentences if kw in s["content"].lower() 
           or kw in s["author"].lower() 
           or kw in s["category"].lower()]
    
    # 返回搜索结果和匹配数量
    return jsonify({"results": arr, "count": len(arr)})


if __name__ == "__main__":
    """
    启动Flask生产服务器
    
    配置:
        host: 0.0.0.0 (允许外部访问)
        port: 5000
        debug: False (生产模式，关闭调试)
    """
    app.run(host="0.0.0.0", port=5000, debug=False)
