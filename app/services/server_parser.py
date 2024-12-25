import re
import json
from typing import Dict, List, Tuple

class ServerInfoParser:
    """
    服务器信息解析器
    """
    @staticmethod
    def parse_server_info(content: str) -> Tuple[Dict[str, str], Dict[str, any]]:
        """
        解析服务器信息
        返回：(必要信息, 额外信息)
        """
        # 清理文本
        content = content.strip()
        # 统一冒号格式和空格
        content = content.replace('：', ':').replace('  ', ' ')
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        # 初始化结果
        required_info = {
            "server_ips": [],
            "server_port": "",
            "server_username": "",
            "server_password": ""
        }
        extra_info = {}
        
        # IP 地址正则
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        
        # 解析每一行
        for line in lines:
            # 打印每行内容，用于调试
            print(f"处理行: {line}")
            
            # 尝试匹配 IP
            ip_matches = re.findall(ip_pattern, line)
            if ip_matches:
                required_info["server_ips"].extend(ip_matches)
                continue
            
            # 分割键值对
            if ':' in line:
                key, value = [x.strip() for x in line.split(':', 1)]
                key = key.lower()
                
                # 匹配端口
                if '端口' in key:
                    port = re.search(r'\d+', value)
                    if port:
                        required_info["server_port"] = port.group()
                
                # 匹配用户名
                elif any(x in key for x in ['账号', '帐号', 'user']):
                    required_info["server_username"] = value
                
                # 匹配密码
                elif '密码' in key:
                    required_info["server_password"] = value
                
                # 其他信息作为额外信息保存
                else:
                    extra_info[key] = value
            else:
                # 配置信息
                if any(x in line.lower() for x in ['gb', 'cpu', 'ddr', 'ssd', 'system', '系统']):
                    extra_info[f"config_{len(extra_info)}"] = line
        
        # 调试输出
        print("解析结果：", {
            "required_info": required_info,
            "extra_info": extra_info
        })
        
        # 转换 IP 列表为 JSON 字符串
        required_info["server_ips"] = json.dumps(required_info["server_ips"])
        
        return required_info, extra_info 