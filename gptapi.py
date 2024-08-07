import aiohttp
import asyncio
import os
import json
import datetime

class GPTAPIConversation:
    def __init__(self, api_key, api_url, model, system_prompt="", enable_logging=False):
        self.api_key = api_key
        self.session = aiohttp.ClientSession()  # 创建一个aiohttp会话
        self.url = api_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.messages = []
        self.model = model
        self.system_prompt = system_prompt
        self.enable_logging = enable_logging

    def log_message(self, message):
        if self.enable_logging:
            timestamp = datetime.datetime.now().isoformat()
            log_entry = f"{timestamp} - {message}"
            file_path = os.path.join(os.getcwd(), "message.log")
            with open(file_path, 'a+', encoding='utf-8') as f:
                f.write(f"{log_entry}\n")

    def add_system_prompt(self):
        if not self.messages or (self.messages and self.messages[0]["role"] != "system"):
            self.messages.insert(0, {
                "role": "system",
                "content": self.system_prompt
            })

    async def call_gpt(self, prompt):
        self.add_system_prompt()
        self.log_message(f"系统提示词：{self.system_prompt}")
        self.messages.append({
            "role": "user",
            "content": prompt
        })
        data = {
            "messages": self.messages,
            "model": self.model,
            "temperature": 0.5,
            "presence_penalty": 2
        }
        self.log_message("发送给gpt的提示: " + prompt)

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.url, headers=self.headers, json=data) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return await self.handle_response(result)
            except aiohttp.ClientResponseError as errh:
                print("Http Error:", errh)
                print("Status code:", response.status)
            except aiohttp.ContentTypeError as e:
                print("JSON decode error:", e)

    async def handle_response(self, result):
        if 'choices' in result and result['choices']:
            content = ""
            for choice in result['choices']:
                if 'message' in choice:
                    content = choice['message']['content']
                    self.log_message(f"gpt:{content}")
                    self.messages.append({
                        "role": "assistant",
                        "content": content
                    })
            return content

    def save_conversation(self):
        file_path = os.path.join(os.getcwd(), 'conversation.json')
        self.log_message(f"保存对话文件,文件路径:{file_path},保存数据:{self.messages}")

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.messages, f, ensure_ascii=False, indent=4)

    async def close(self):
        await self.session.close()  # 关闭会话