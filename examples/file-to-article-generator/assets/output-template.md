# 文章生成结果

---

## 原文摘要

**文件信息**：
- 文件类型：{FILE_TYPE}
- 标题：{FILE_TITLE}
- 作者：{FILE_AUTHOR}
- 总页数/段落数：{PAGE_OR_PARA_COUNT}

**内容概览**：
{CONTENT_SUMMARY}

---

## 生成的文章

**文章类型**：{ARTICLE_TYPE}

**文章标题**：{ARTICLE_TITLE}

---

{ARTICLE_BODY}

---

## 文章质量评估

> ⚠️ **重要说明**：以下评估结果必须包含在文章的最后，作为文章质量的重要参考。

### 评估角色
{EVALUATION_ROLE}

### 1. 标题点击欲望判定 (Max: 50 points)

**标题点击欲望评分：** {TITLE_SCORE} / 50

**是否会点击：** [{WILL_CLICK}]

**一句话原因：**
{CLICK_REASON}

**标题改写：**
{TITLE_REWRITE_SUGGESTIONS}

### 2. 全文阅读价值判定 (Max: 50 points)

**全文阅读价值评分：** {CONTENT_SCORE} / 50

**收获价值总结：**
{VALUE_SUMMARY}

**对我直接有用的点：**
{USEFUL_POINTS}

**内容缺憾：**
{CONTENT_GAPS}

### 3. 总分与简评

**总分：** {TOTAL_SCORE} / 100

**一句话简评：**
{BRIEF_COMMENT}

---

## 图片清单

| 索引 | 本地路径 | 描述 |
|-----|---------|------|
{IMAGES_TABLE_ROWS}

---

## 文件下载

**输出目录结构**：
```
output/
├── article.md          # Markdown格式的文章内容（包含评估报告）
└── images/             # 图片文件目录
    ├── image_001.png
    ├── image_002.png
    └── ...
```

**使用说明**：
1. 文章已保存为Markdown格式文件，可直接用Markdown编辑器打开
2. 图片保存在 `images/` 目录，与文章使用相对路径关联
3. 可下载整个 `output/` 目录，包含文章和所有图片
4. 文章中的图片使用标准Markdown语法引用，支持大部分Markdown渲染器
5. **文章评估报告已附加在文章内容的最后**

---

*本内容由文件解析与文章生成器自动生成*
