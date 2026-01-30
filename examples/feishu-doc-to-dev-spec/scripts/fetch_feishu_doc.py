#!/usr/bin/env python3
"""
飞书云文档读取脚本

读取飞书云文档的完整内容，包括文本、表格、图片、代码块等。
支持新版文档(docx)、旧版文档(docs)和知识库文档(wiki)。

输入参数（JSON 格式，通过 stdin 传入）：
{
    "doc_urls": ["https://xxx.feishu.cn/docx/xxxxx"],
    "app_id": "飞书应用ID（可选）",
    "app_secret": "飞书应用密钥（可选）"
}

输出（JSON 格式）：
{
    "success": true,
    "documents": [
        {
            "url": "原始链接",
            "title": "文档标题",
            "content": "Markdown 格式的文档内容",
            "images": ["下载的图片路径列表"]
        }
    ],
    "merged_content": "合并后的完整内容"
}
"""

import json
import os
import re
import sys
import base64
import hashlib
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx


class FeishuDocReader:
    """飞书云文档读取器"""

    # API 基础地址
    BASE_URL = "https://open.feishu.cn/open-apis"

    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self._tenant_token: str | None = None
        self._client = httpx.Client(timeout=30.0)
        self.output_dir = Path("./output")
        self.images_dir = self.output_dir / "images"
        self.images_dir.mkdir(parents=True, exist_ok=True)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._client.close()

    def _get_tenant_token(self) -> str:
        """获取 tenant_access_token"""
        if self._tenant_token:
            return self._tenant_token

        url = f"{self.BASE_URL}/auth/v3/tenant_access_token/internal"
        response = self._client.post(
            url,
            json={
                "app_id": self.app_id,
                "app_secret": self.app_secret,
            },
        )
        response.raise_for_status()
        data = response.json()

        if data.get("code") != 0:
            raise Exception(f"获取 tenant_access_token 失败: {data.get('msg')}")

        self._tenant_token = data["tenant_access_token"]
        return self._tenant_token

    def _request(self, method: str, path: str, **kwargs) -> dict:
        """发送 API 请求"""
        token = self._get_tenant_token()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"

        url = f"{self.BASE_URL}{path}"
        response = self._client.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()

    def _download_image(self, file_token: str) -> str | None:
        """下载图片并返回本地路径"""
        try:
            token = self._get_tenant_token()
            url = f"{self.BASE_URL}/drive/v1/medias/{file_token}/download"

            response = self._client.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
                follow_redirects=True,
            )
            response.raise_for_status()

            # 根据 content-type 确定扩展名
            content_type = response.headers.get("content-type", "")
            ext = ".png"
            if "jpeg" in content_type or "jpg" in content_type:
                ext = ".jpg"
            elif "gif" in content_type:
                ext = ".gif"
            elif "webp" in content_type:
                ext = ".webp"

            # 使用 file_token 的哈希作为文件名
            filename = hashlib.md5(file_token.encode()).hexdigest()[:12] + ext
            local_path = self.images_dir / filename

            local_path.write_bytes(response.content)
            return f"./images/{filename}"
        except Exception as e:
            print(f"下载图片失败 ({file_token}): {e}", file=sys.stderr)
            return None

    def parse_doc_url(self, url: str) -> tuple[str, str]:
        """
        解析飞书文档 URL，返回 (doc_type, doc_token)

        支持的 URL 格式：
        - https://xxx.feishu.cn/docx/xxxxx - 新版文档
        - https://xxx.feishu.cn/docs/xxxxx - 旧版文档
        - https://xxx.feishu.cn/wiki/xxxxx - 知识库
        """
        parsed = urlparse(url)
        path_parts = parsed.path.strip("/").split("/")

        if len(path_parts) < 2:
            raise ValueError(f"无法解析文档链接: {url}")

        doc_type = path_parts[0]  # docx, docs, wiki
        doc_token = path_parts[1].split("?")[0]  # 去除查询参数

        return doc_type, doc_token

    def get_docx_content(self, document_id: str) -> dict:
        """获取新版文档(docx)内容"""
        # 获取文档元信息
        meta_response = self._request("GET", f"/docx/v1/documents/{document_id}")
        if meta_response.get("code") != 0:
            raise Exception(f"获取文档元信息失败: {meta_response.get('msg')}")

        title = meta_response.get("data", {}).get("document", {}).get("title", "未命名文档")

        # 获取文档块内容
        blocks_response = self._request(
            "GET",
            f"/docx/v1/documents/{document_id}/blocks",
            params={"page_size": 500},
        )
        if blocks_response.get("code") != 0:
            raise Exception(f"获取文档内容失败: {blocks_response.get('msg')}")

        blocks = blocks_response.get("data", {}).get("items", [])

        # 递归获取所有块（处理分页）
        page_token = blocks_response.get("data", {}).get("page_token")
        while page_token:
            next_response = self._request(
                "GET",
                f"/docx/v1/documents/{document_id}/blocks",
                params={"page_size": 500, "page_token": page_token},
            )
            if next_response.get("code") == 0:
                blocks.extend(next_response.get("data", {}).get("items", []))
                page_token = next_response.get("data", {}).get("page_token")
            else:
                break

        return {"title": title, "blocks": blocks}

    def get_wiki_content(self, wiki_token: str) -> dict:
        """获取知识库文档内容"""
        # 先获取知识库节点信息，找到实际的文档 ID
        response = self._request("GET", f"/wiki/v2/spaces/get_node", params={"token": wiki_token})
        if response.get("code") != 0:
            raise Exception(f"获取知识库节点失败: {response.get('msg')}")

        node = response.get("data", {}).get("node", {})
        obj_token = node.get("obj_token")
        obj_type = node.get("obj_type")

        if obj_type == "docx":
            return self.get_docx_content(obj_token)
        else:
            raise Exception(f"不支持的知识库文档类型: {obj_type}")

    def blocks_to_markdown(self, blocks: list[dict]) -> tuple[str, list[str]]:
        """将文档块转换为 Markdown 格式"""
        lines = []
        images = []
        block_map = {b.get("block_id"): b for b in blocks}

        def process_text_elements(elements: list[dict]) -> str:
            """处理文本元素"""
            result = []
            for elem in elements:
                text_run = elem.get("text_run", {})
                content = text_run.get("content", "")
                style = text_run.get("text_element_style", {})

                # 处理样式
                if style.get("bold"):
                    content = f"**{content}**"
                if style.get("italic"):
                    content = f"*{content}*"
                if style.get("strikethrough"):
                    content = f"~~{content}~~"
                if style.get("inline_code"):
                    content = f"`{content}`"
                if style.get("link", {}).get("url"):
                    url = style["link"]["url"]
                    content = f"[{content}]({url})"

                result.append(content)
            return "".join(result)

        def process_block(block: dict, indent: int = 0) -> list[str]:
            """递归处理文档块"""
            block_type = block.get("block_type")
            block_lines = []
            prefix = "  " * indent

            if block_type == 1:  # Page
                pass  # 页面块，跳过

            elif block_type == 2:  # Text
                text = block.get("text", {})
                elements = text.get("elements", [])
                content = process_text_elements(elements)
                if content.strip():
                    block_lines.append(f"{prefix}{content}")

            elif block_type == 3:  # Heading1
                text = block.get("heading1", {})
                elements = text.get("elements", [])
                content = process_text_elements(elements)
                block_lines.append(f"\n# {content}\n")

            elif block_type == 4:  # Heading2
                text = block.get("heading2", {})
                elements = text.get("elements", [])
                content = process_text_elements(elements)
                block_lines.append(f"\n## {content}\n")

            elif block_type == 5:  # Heading3
                text = block.get("heading3", {})
                elements = text.get("elements", [])
                content = process_text_elements(elements)
                block_lines.append(f"\n### {content}\n")

            elif block_type == 6:  # Heading4
                text = block.get("heading4", {})
                elements = text.get("elements", [])
                content = process_text_elements(elements)
                block_lines.append(f"\n#### {content}\n")

            elif block_type == 7:  # Heading5
                text = block.get("heading5", {})
                elements = text.get("elements", [])
                content = process_text_elements(elements)
                block_lines.append(f"\n##### {content}\n")

            elif block_type == 8:  # Heading6
                text = block.get("heading6", {})
                elements = text.get("elements", [])
                content = process_text_elements(elements)
                block_lines.append(f"\n###### {content}\n")

            elif block_type == 9:  # Heading7
                text = block.get("heading7", {})
                elements = text.get("elements", [])
                content = process_text_elements(elements)
                block_lines.append(f"\n####### {content}\n")

            elif block_type == 10:  # Heading8
                text = block.get("heading8", {})
                elements = text.get("elements", [])
                content = process_text_elements(elements)
                block_lines.append(f"\n######## {content}\n")

            elif block_type == 11:  # Heading9
                text = block.get("heading9", {})
                elements = text.get("elements", [])
                content = process_text_elements(elements)
                block_lines.append(f"\n######### {content}\n")

            elif block_type == 12:  # Bullet (无序列表)
                text = block.get("bullet", {})
                elements = text.get("elements", [])
                content = process_text_elements(elements)
                block_lines.append(f"{prefix}- {content}")

            elif block_type == 13:  # Ordered (有序列表)
                text = block.get("ordered", {})
                elements = text.get("elements", [])
                content = process_text_elements(elements)
                block_lines.append(f"{prefix}1. {content}")

            elif block_type == 14:  # Code
                code_block = block.get("code", {})
                elements = code_block.get("elements", [])
                content = process_text_elements(elements)
                language = code_block.get("style", {}).get("language", "")
                # 映射语言代码到名称
                lang_map = {
                    1: "plaintext", 2: "abap", 3: "ada", 4: "apache", 5: "apex",
                    6: "assembly", 7: "bash", 8: "csharp", 9: "cpp", 10: "c",
                    11: "cobol", 12: "css", 13: "coffeescript", 14: "d", 15: "dart",
                    16: "delphi", 17: "django", 18: "dockerfile", 19: "erlang", 20: "fortran",
                    21: "foxpro", 22: "go", 23: "groovy", 24: "html", 25: "http",
                    26: "haskell", 27: "json", 28: "java", 29: "javascript", 30: "julia",
                    31: "kotlin", 32: "latex", 33: "lisp", 34: "logo", 35: "lua",
                    36: "matlab", 37: "makefile", 38: "markdown", 39: "nginx", 40: "objectivec",
                    41: "openedge", 42: "php", 43: "perl", 44: "postscript", 45: "powershell",
                    46: "prolog", 47: "protobuf", 48: "python", 49: "r", 50: "rpg",
                    51: "ruby", 52: "rust", 53: "sas", 54: "scss", 55: "sql",
                    56: "scala", 57: "scheme", 58: "scratch", 59: "shell", 60: "swift",
                    61: "thrift", 62: "typescript", 63: "vbnet", 64: "vbscript", 65: "visual_basic",
                    66: "xml", 67: "yaml", 68: "cmake", 69: "diff", 70: "gherkin",
                    71: "graphql", 72: "opengl", 73: "solidity", 74: "toml",
                }
                lang_name = lang_map.get(language, "")
                block_lines.append(f"\n```{lang_name}\n{content}\n```\n")

            elif block_type == 15:  # Quote (引用)
                text = block.get("quote", {})
                elements = text.get("elements", [])
                content = process_text_elements(elements)
                block_lines.append(f"{prefix}> {content}")

            elif block_type == 17:  # TodoList (待办事项)
                todo = block.get("todo", {})
                elements = todo.get("elements", [])
                content = process_text_elements(elements)
                done = todo.get("style", {}).get("done", False)
                checkbox = "[x]" if done else "[ ]"
                block_lines.append(f"{prefix}- {checkbox} {content}")

            elif block_type == 18:  # Divider (分割线)
                block_lines.append(f"\n---\n")

            elif block_type == 19:  # Image (图片)
                image = block.get("image", {})
                file_token = image.get("token", "")
                if file_token:
                    local_path = self._download_image(file_token)
                    if local_path:
                        images.append(local_path)
                        block_lines.append(f"\n![image]({local_path})\n")
                    else:
                        block_lines.append(f"\n[图片加载失败: {file_token}]\n")

            elif block_type == 20:  # Table (表格)
                table = block.get("table", {})
                property_info = table.get("property", {})
                row_size = property_info.get("row_size", 0)
                column_size = property_info.get("column_size", 0)

                # 获取合并单元格信息
                merge_info = table.get("merge_info", [])

                # 构建表格内容
                table_lines = []
                children = block.get("children", [])

                if children and row_size > 0 and column_size > 0:
                    rows = []
                    for i in range(row_size):
                        row = []
                        for j in range(column_size):
                            cell_idx = i * column_size + j
                            if cell_idx < len(children):
                                cell_block_id = children[cell_idx]
                                cell_block = block_map.get(cell_block_id, {})
                                # 处理单元格内容
                                cell_content = self._process_table_cell(cell_block, block_map)
                                row.append(cell_content)
                            else:
                                row.append("")
                        rows.append(row)

                    # 生成 Markdown 表格
                    if rows:
                        # 表头
                        header = "| " + " | ".join(rows[0]) + " |"
                        separator = "| " + " | ".join(["---"] * column_size) + " |"
                        table_lines.append(header)
                        table_lines.append(separator)
                        # 表体
                        for row in rows[1:]:
                            row_line = "| " + " | ".join(row) + " |"
                            table_lines.append(row_line)

                if table_lines:
                    block_lines.append("\n" + "\n".join(table_lines) + "\n")

            elif block_type == 21:  # TableCell (表格单元格) - 在表格处理中单独处理
                pass

            elif block_type == 22:  # QuoteContainer (引用容器)
                children = block.get("children", [])
                for child_id in children:
                    child_block = block_map.get(child_id)
                    if child_block:
                        block_lines.extend(process_block(child_block, indent))

            elif block_type == 23:  # Task (任务)
                task = block.get("task", {})
                task_id = task.get("task_id", "")
                block_lines.append(f"{prefix}[任务: {task_id}]")

            elif block_type == 24:  # OKR
                block_lines.append(f"{prefix}[OKR 组件]")

            elif block_type == 25:  # OKRObjective
                block_lines.append(f"{prefix}[OKR 目标]")

            elif block_type == 26:  # OKRKeyResult
                block_lines.append(f"{prefix}[OKR 关键结果]")

            elif block_type == 27:  # OKRProgress
                block_lines.append(f"{prefix}[OKR 进度]")

            elif block_type == 28:  # AddOns (第三方应用块)
                block_lines.append(f"{prefix}[第三方应用组件]")

            elif block_type == 29:  # JiraIssue
                block_lines.append(f"{prefix}[Jira Issue]")

            elif block_type == 30:  # WikiCatalog (知识库目录)
                block_lines.append(f"{prefix}[知识库目录]")

            elif block_type == 31:  # Board (画板)
                block_lines.append(f"{prefix}[画板]")

            elif block_type == 32:  # Callout (高亮块)
                callout = block.get("callout", {})
                children = block.get("children", [])
                emoji = callout.get("emoji_id", "📌")
                block_lines.append(f"\n> {emoji} **高亮块**")
                for child_id in children:
                    child_block = block_map.get(child_id)
                    if child_block:
                        child_lines = process_block(child_block, indent + 1)
                        for line in child_lines:
                            block_lines.append(f"> {line}")

            elif block_type == 999:  # Undefined
                block_lines.append(f"{prefix}[未知块类型]")

            # 处理子块
            children = block.get("children", [])
            if children and block_type not in [20, 22, 32]:  # 表格、引用容器、高亮块的子块已处理
                for child_id in children:
                    child_block = block_map.get(child_id)
                    if child_block:
                        block_lines.extend(process_block(child_block, indent + 1))

            return block_lines

        # 处理所有顶级块
        for block in blocks:
            parent_id = block.get("parent_id")
            # 只处理顶级块（parent_id 为空或等于文档 ID）
            if not parent_id or parent_id == blocks[0].get("block_id"):
                lines.extend(process_block(block))

        return "\n".join(lines), images

    def _process_table_cell(self, cell_block: dict, block_map: dict) -> str:
        """处理表格单元格内容"""
        block_type = cell_block.get("block_type")

        if block_type == 21:  # TableCell
            children = cell_block.get("children", [])
            contents = []
            for child_id in children:
                child_block = block_map.get(child_id, {})
                child_type = child_block.get("block_type")

                if child_type == 2:  # Text
                    text = child_block.get("text", {})
                    elements = text.get("elements", [])
                    content = self._process_text_elements_simple(elements)
                    contents.append(content)

            return " ".join(contents).replace("|", "\\|").replace("\n", " ")

        return ""

    def _process_text_elements_simple(self, elements: list[dict]) -> str:
        """简单处理文本元素（用于表格单元格）"""
        result = []
        for elem in elements:
            text_run = elem.get("text_run", {})
            content = text_run.get("content", "")
            result.append(content)
        return "".join(result)

    def read_document(self, url: str) -> dict:
        """读取文档并返回内容"""
        doc_type, doc_token = self.parse_doc_url(url)

        if doc_type == "docx":
            doc_data = self.get_docx_content(doc_token)
        elif doc_type == "wiki":
            doc_data = self.get_wiki_content(doc_token)
        elif doc_type == "docs":
            # 旧版文档 API 已废弃，尝试作为 docx 处理
            doc_data = self.get_docx_content(doc_token)
        else:
            raise ValueError(f"不支持的文档类型: {doc_type}")

        title = doc_data.get("title", "未命名文档")
        blocks = doc_data.get("blocks", [])

        content, images = self.blocks_to_markdown(blocks)

        return {
            "url": url,
            "title": title,
            "content": content,
            "images": images,
        }

    def read_documents(self, urls: list[str]) -> dict:
        """读取多个文档并合并内容"""
        documents = []
        all_images = []
        merged_parts = []

        for i, url in enumerate(urls):
            try:
                print(f"读取文档 {i + 1}/{len(urls)}: {url}", file=sys.stderr)
                doc = self.read_document(url)
                documents.append(doc)
                all_images.extend(doc.get("images", []))

                # 添加到合并内容
                merged_parts.append(f"# {doc['title']}\n")
                merged_parts.append(doc["content"])
                if i < len(urls) - 1:
                    merged_parts.append("\n\n---\n\n")  # 文档分隔线

            except Exception as e:
                print(f"读取文档失败 ({url}): {e}", file=sys.stderr)
                documents.append({
                    "url": url,
                    "title": "读取失败",
                    "content": f"错误: {str(e)}",
                    "images": [],
                    "error": str(e),
                })

        return {
            "success": True,
            "documents": documents,
            "merged_content": "".join(merged_parts),
            "total_images": len(all_images),
        }


def main():
    """主函数"""
    # 从 stdin 读取输入
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({
            "success": False,
            "error": f"JSON 解析错误: {str(e)}",
        }))
        sys.exit(1)

    # 获取参数
    doc_urls = input_data.get("doc_urls", [])
    if isinstance(doc_urls, str):
        doc_urls = [doc_urls]

    if not doc_urls:
        print(json.dumps({
            "success": False,
            "error": "未提供文档链接 (doc_urls)",
        }))
        sys.exit(1)

    # 获取飞书凭证
    app_id = input_data.get("app_id") or os.environ.get("FEISHU_APP_ID")
    app_secret = input_data.get("app_secret") or os.environ.get("FEISHU_APP_SECRET")

    if not app_id or not app_secret:
        print(json.dumps({
            "success": False,
            "error": "缺少飞书应用凭证，请设置 FEISHU_APP_ID 和 FEISHU_APP_SECRET 环境变量",
        }))
        sys.exit(1)

    # 读取文档
    try:
        with FeishuDocReader(app_id, app_secret) as reader:
            result = reader.read_documents(doc_urls)
            print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e),
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()
