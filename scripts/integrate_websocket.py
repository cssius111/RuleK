#!/usr/bin/env python3
"""
将WebSocket功能集成到FastAPI应用
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def integrate_websocket():
    """集成WebSocket到app.py"""
    
    app_file = project_root / "web" / "backend" / "app.py"
    
    if not app_file.exists():
        print(f"❌ 找不到 {app_file}")
        return False
        
    # 读取现有app.py
    content = app_file.read_text()
    
    # 检查是否已经集成
    if "websocket_endpoint" in content or "@app.websocket" in content:
        print("✅ WebSocket已经集成")
        return True
        
    # 找到导入部分的结束位置
    import_end = content.find("\n\napp = FastAPI")
    if import_end == -1:
        import_end = content.find("\napp = FastAPI")
        
    # 添加WebSocket导入
    websocket_imports = """
# WebSocket支持
from fastapi import WebSocket, WebSocketDisconnect, Query
from services.streaming_service import websocket_endpoint, streaming_service
"""
    
    # 找到路由定义部分
    route_section = content.find("@app.get")
    if route_section == -1:
        route_section = content.find("@app.post")
        
    # 添加WebSocket路由
    websocket_route = '''

# WebSocket端点
@app.websocket("/ws")
async def websocket_route(websocket: WebSocket, client_id: str = Query(...)):
    """WebSocket连接端点"""
    await websocket_endpoint(websocket, client_id)


# 流式AI响应端点
@app.post("/api/ai/stream/{game_id}")
async def stream_ai_response(game_id: str, request: dict):
    """触发AI流式响应"""
    prompt = request.get("prompt", "")
    
    # 生成AI响应并流式发送
    async def generate():
        # 这里应该调用实际的AI服务
        response = "这是一个测试的流式响应。每个字都会逐个发送到客户端。"
        for char in response:
            yield char
            
    await streaming_service.send_stream(game_id, generate())
    
    return {"status": "streaming", "game_id": game_id}
'''
    
    # 组装新内容
    if import_end > 0:
        new_content = (
            content[:import_end] + 
            websocket_imports + 
            content[import_end:route_section] + 
            websocket_route + 
            content[route_section:]
        )
    else:
        # 如果找不到合适位置，在文件末尾添加
        new_content = content + websocket_route
        
    # 写回文件
    app_file.write_text(new_content)
    print(f"✅ WebSocket已集成到 {app_file}")
    
    # 创建一个示例HTML测试页面
    test_html = project_root / "web" / "backend" / "static" / "websocket_test.html"
    test_html.parent.mkdir(parents=True, exist_ok=True)
    
    test_html.write_text('''<!DOCTYPE html>
<html>
<head>
    <title>WebSocket测试</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        #messages { border: 1px solid #ccc; height: 300px; overflow-y: auto; padding: 10px; margin: 10px 0; }
        .message { margin: 5px 0; padding: 5px; background: #f0f0f0; }
        .sent { background: #e0f0ff; }
        .received { background: #f0ffe0; }
        button { margin: 5px; padding: 5px 10px; }
    </style>
</head>
<body>
    <h1>WebSocket测试页面</h1>
    <div>
        <button onclick="connect()">连接</button>
        <button onclick="disconnect()">断开</button>
        <button onclick="sendTest()">发送测试</button>
        <button onclick="requestStream()">请求流式数据</button>
    </div>
    <div id="messages"></div>
    
    <script>
        let ws = null;
        const clientId = 'test_' + Date.now();
        
        function log(message, type = 'received') {
            const div = document.createElement('div');
            div.className = 'message ' + type;
            div.textContent = new Date().toLocaleTimeString() + ' - ' + message;
            document.getElementById('messages').appendChild(div);
            document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
        }
        
        function connect() {
            if (ws) {
                log('已经连接', 'sent');
                return;
            }
            
            ws = new WebSocket(`ws://localhost:8000/ws?client_id=${clientId}`);
            
            ws.onopen = () => {
                log('WebSocket连接成功', 'sent');
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'ping') {
                    ws.send(JSON.stringify({type: 'pong', data: {}}));
                    log('心跳: ping -> pong');
                } else if (data.type === 'stream_chunk') {
                    log(`流式数据 #${data.data.chunk_id}: ${data.data.content}`);
                } else {
                    log(`收到: ${JSON.stringify(data)}`);
                }
            };
            
            ws.onclose = () => {
                log('WebSocket连接关闭', 'sent');
                ws = null;
            };
            
            ws.onerror = (error) => {
                log('WebSocket错误: ' + error, 'sent');
            };
        }
        
        function disconnect() {
            if (ws) {
                ws.close();
                ws = null;
                log('主动断开连接', 'sent');
            }
        }
        
        function sendTest() {
            if (!ws) {
                log('未连接', 'sent');
                return;
            }
            
            const message = {type: 'test', data: {message: 'Hello from client!'}};
            ws.send(JSON.stringify(message));
            log('发送: ' + JSON.stringify(message), 'sent');
        }
        
        function requestStream() {
            if (!ws) {
                log('未连接', 'sent');
                return;
            }
            
            // 通过HTTP请求触发流式响应
            fetch(`/api/ai/stream/${clientId}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({prompt: 'Generate story'})
            })
            .then(response => response.json())
            .then(data => log('请求流式响应: ' + JSON.stringify(data), 'sent'));
        }
        
        // 自动连接
        window.onload = () => {
            log('页面加载完成，点击"连接"按钮开始测试');
        };
    </script>
</body>
</html>
''')
    
    print(f"✅ 测试页面已创建: {test_html}")
    print("\n📝 使用说明：")
    print("1. 启动服务器: python web/backend/app.py")
    print("2. 访问测试页面: http://localhost:8000/static/websocket_test.html")
    print("3. 点击'连接'按钮测试WebSocket功能")
    
    return True


if __name__ == "__main__":
    if integrate_websocket():
        print("\n✅ WebSocket集成完成！")
    else:
        print("\n❌ WebSocket集成失败")
