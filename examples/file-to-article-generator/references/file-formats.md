# 文件格式规范

## 目录
1. [输入文件格式](#输入文件格式)
2. [输出格式规范](#输出格式规范)

## 输入文件格式

### 支持的文件类型

| 文件类型 | 扩展名 | 文本提取能力 | 图片提取能力 |
|---------|-------|------------|------------|
| PDF | `.pdf` | ✅ 支持 | ✅ 支持（提取图片位置和描述） |
| Word | `.docx`, `.doc` | ✅ 支持（仅 `.docx`） | ✅ 支持（检测图片位置） |
| 图片 | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp` | ❌ 不支持（仅标记为图片） | ✅ 支持（获取图片元数据） |
| 其他 | - | ❌ 不支持 | ❌ 不支持 |

### PDF文件规范

**支持版本**：PDF 1.0 - 2.0

**文本提取**：
- 提取所有页面的文本内容
- 保留基本段落结构
- 标记分页信息（`--- 第N页 ---`）

**图片提取与保存**：
- 使用PyMuPDF提取PDF中的所有图片对象
- 图片保存到输出目录：`./images/`
- 图片命名格式：`image_001.png`, `image_002.png` 等
- 记录图片所在页面和本地路径
- 输出图片描述，格式：`PDF第N页的第M张图片`

**元数据提取**：
- 标题（Title）
- 作者（Author）
- 主题（Subject）
- 页数（Page Count）

**注意事项**：
- 扫描版PDF（纯图片）无法提取文本，需要OCR（暂不支持）
- 加密PDF需要密码才能解析（暂不支持）
- 复杂布局的PDF可能影响文本提取质量

### Word文件规范

**支持版本**：
- ✅ 完全支持：`.docx`（Office 2007及以后）
- ❌ 不支持：`.doc`（旧版二进制格式）

**文本提取**：
- 提取所有段落文本
- 保留基本段落顺序
- 标记表格内容（`[表格X 行Y 列Z]: 内容`）

**图片提取与保存**：
- 检测并提取Word文档中的所有图片
- 图片保存到输出目录：`./images/`
- 图片命名格式：`image_001.png`, `image_002.png` 等
- 记录图片位置和本地路径
- 输出图片描述，格式：`Word文档中的第N张图片`

**元数据提取**：
- 标题（Title）
- 作者（Author）
- 主题（Subject）
- 段落数（Paragraph Count）

**注意事项**：
- 复杂格式（如多级列表、嵌套表格）可能影响文本质量
- 图片无法直接提取，仅记录位置信息

### 图片文件规范

**支持格式**：
- JPEG：`.jpg`, `.jpeg`
- PNG：`.png`
- GIF：`.gif`
- BMP：`.bmp`
- WebP：`.webp`

**图片保存**：
- 图片直接复制到输出目录：`./images/`
- 命名格式：`image_001.{original_format}`
- 获取并返回图片的本地路径

**图片信息提取**：
- 格式（Format）
- 尺寸（Size）：宽x高
- 颜色模式（Mode）：如RGB、L等
- 描述：自动生成描述，格式：`{宽}x{高} {格式}图片`

**注意事项**：
- 不支持OCR文字识别
- 图片文件会被保存到输出目录，可直接用于Markdown引用

## 输出格式规范

### parse_file.py 输出格式

**标准输出（JSON格式）**：

```json
{
  "file_type": "pdf|docx|image",
  "text_content": "提取的文本内容，可能包含分页标记",
  "images": [
    {
      "index": 0,
      "description": "图片描述信息",
      "local_path": "./images/image_001.png",
      "page": 1,
      "paragraph": 3,
      "format": "png",
      "size": [800, 600]
    }
  ],
  "metadata": {
    "title": "文件标题",
    "author": "作者",
    "subject": "主题",
    "page_count": 10,
    "paragraph_count": 50,
    "format": "pdf|docx|jpg|png",
    "size": [800, 600]
  }
}
```

**错误输出**：

```json
{
  "error": "错误描述信息"
}
```

**字段说明**：

| 字段 | 类型 | 必需 | 说明 |
|-----|------|-----|------|
| file_type | string | ✅ | 文件类型：`pdf`, `docx`, `image` |
| text_content | string | ✅ | 提取的文本内容 |
| images | array | ✅ | 图片信息列表，可为空 |
| images[].index | integer | ✅ | 图片索引（从0开始） |
| images[].description | string | ✅ | 图片描述 |
| images[].local_path | string | ✅ | 图片的本地路径（相对路径，如 `./images/image_001.png`） |
| images[].page | integer | 否 | 图片所在页码（PDF专用） |
| images[].paragraph | integer | 否 | 图片所在段落（Word专用） |
| images[].format | string | 否 | 图片格式（如 `png`, `jpg`） |
| images[].size | array | 否 | 图片尺寸 [宽, 高]（图片文件专用） |
| metadata | object | ✅ | 文件元数据 |
| metadata.title | string | 否 | 文件标题 |
| metadata.author | string | 否 | 文件作者 |
| metadata.subject | string | 否 | 文件主题 |
| metadata.page_count | integer | 否 | 页数（PDF专用） |
| metadata.paragraph_count | integer | 否 | 段落数（Word专用） |
| metadata.format | string | 否 | 图片格式（图片专用） |
| metadata.size | array | 否 | 图片尺寸 [宽, 高]（图片专用） |

### 最终输出格式（参考 output-template.md）

最终输出包含以下部分：

1. **原文摘要**：简述原文文件的核心内容
2. **生成的文章**：完整的文章内容（使用Markdown语法引用图片）
3. **图片清单**：所有图片的索引、本地路径、描述
4. **质量评分报告**：各维度得分、总分、评级、改进建议
5. **文件下载说明**：输出目录结构和使用说明

详细格式见 [assets/output-template.md](../assets/output-template.md)

## 使用建议

### 选择合适的文件格式

| 场景 | 推荐格式 | 原因 |
|-----|---------|------|
| 正式文档 | PDF | 格式稳定，布局保持好 |
| 可编辑文档 | DOCX | 文本提取质量高，易于编辑 |
| 包含丰富图片的文档 | DOCX | 图片位置检测更准确 |
| 纯图片内容 | JPG/PNG | 支持度高，压缩比好 |
| 需要透明背景 | PNG | 支持透明通道 |

### 提高解析质量的建议

**PDF文件**：
- 避免使用扫描版PDF（文字变成图片）
- 避免复杂的布局和多栏排版
- 确保PDF未加密

**Word文件**：
- 优先使用 `.docx` 格式（而非旧版 `.doc`）
- 避免过度的格式和嵌套结构
- 图片建议添加描述性文字

**图片文件**：
- 选择合适的分辨率（过高影响处理速度，过低影响质量）
- 文字清晰的图片便于后续人工添加说明

### 文件路径规范

- 使用相对路径（如 `./document.pdf`）
- 避免使用绝对路径
- 文件名使用英文或数字，避免特殊字符
- 路径中不要包含空格（如果无法避免，请用引号包裹）
