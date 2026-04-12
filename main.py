import json
import requests
from requests.exceptions import SSLError, ConnectionError
from blessed import Terminal
import sys

def add_protocol(url):
    """自动添加协议前缀（优先https）"""
    if not url.startswith(('http://', 'https://')):
        # 检查是否以www开头，如果是则去掉以便统一处理
        if url.startswith('www.'):
            url = url[4:]
        
        # 优先使用https
        return f"https://{url}"
    
    return url

def send_post_request_with_fallback(term, url, payload):
    """发送POST请求，如果HTTPS失败则尝试HTTP"""
    original_url = url
    
    # 如果是https URL，先尝试https
    if url.startswith('https://'):
        try:
            print(term.yellow(f"尝试通过HTTPS连接: {url}"))
            response = requests.post(url, json=payload, timeout=30)
            return response
        except SSLError as e:
            print(term.red(f"HTTPS连接错误: {str(e)}"))
            print(term.yellow("尝试切换到HTTP..."))
            # 尝试HTTP
            http_url = url.replace('https://', 'http://')
            try:
                response = requests.post(http_url, json=payload, timeout=30)
                print(term.yellow(f"成功通过HTTP连接: {http_url}"))
                return response
            except Exception as http_error:
                print(term.red(f"HTTP连接也失败: {str(http_error)}"))
                return None
        except Exception as e:
            print(term.red(f"HTTPS连接错误: {str(e)}"))
            return None
    else:
        # 如果已经是http，直接尝试
        try:
            response = requests.post(url, json=payload, timeout=30)
            return response
        except Exception as e:
            print(term.red(f"HTTP连接错误: {str(e)}"))
            return None

def load_json_file(file_path):
    """从指定路径加载JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None
    except Exception:
        return None

def main():
    term = Terminal()
    
    print(term.purple("=== POST请求发送器 ==="))
    print(term.purple("此程序将向您提供的URL发送POST请求。"))
    print(term.purple("输入 'quit' 或 'exit' 退出程序\n"))
    
    while True:
        # 获取URL
        url_input = input(term.purple("请输入目标URL (输入 'quit' 或 'exit' 退出): ")).strip()
        
        if url_input.lower() in ['quit', 'exit']:
            print(term.purple("程序已退出。"))
            break
            
        if not url_input:
            print(term.red("错误: URL不能为空\n"))
            continue
        
        # 自动添加协议
        url = add_protocol(url_input)
        print(term.white(f"初始URL: {url}"))
        
        # 获取JSON文件路径
        json_file_path = input(term.purple("请输入JSON文件路径: ")).strip()
        
        if not json_file_path:
            print(term.red("错误: JSON文件路径不能为空\n"))
            continue
        
        # 加载JSON数据
        payload = load_json_file(json_file_path)
        if payload is None:
            if not load_json_file(json_file_path):  # 检查文件是否存在
                print(term.red(f"错误: 找不到文件 {json_file_path}"))
            else:
                print(term.red(f"错误: 文件 {json_file_path} 不是有效的JSON格式"))
            print()
            continue
        
        print(term.yellow(f"\n正在向 {url} 发送POST请求..."))
        print(term.white("负载数据:"), term.white(json.dumps(payload, ensure_ascii=False, indent=2)))
        
        # 发送POST请求（带fallback机制）
        response = send_post_request_with_fallback(term, url, payload)
        if response is None:
            print(term.red("所有连接尝试均已失败。"))
            print()
            continue
        
        # 输出响应信息
        print(term.green("\n=== 响应信息 ==="))
        print(term.green(f"状态码: {response.status_code}"))
        print(term.green(f"响应头: {dict(response.headers)}"))
        print(term.green("响应内容:"))
        print(term.white(response.text))  # 响应内容保持白色
        
        print(term.white("\n" + "="*50 + "\n"))

if __name__ == "__main__":
    main()