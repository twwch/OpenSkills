# DrawIO XML 格式参考

## 目录
1. [XML 结构](#xml-结构)
2. [基础元素](#基础元素)
3. [连接器](#连接器)
4. [样式配置](#样式配置)
5. [常见示例](#常见示例)

## 概览
DrawIO 使用 XML 格式描述图表。本格式支持复杂的网络拓扑、系统架构图等专业绘图场景。

## XML 结构

### 基础模板
```xml
<mxfile host="app.diagrams.net" modified="2024-01-01T00:00:00.000Z" agent="Skill" version="22.0.0">
  <diagram name="Page-1" id="diagram-1">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="850" pageHeight="1100" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- 在这里添加图形和连接器 -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## 基础元素

### 矩形节点
```xml
<mxCell id="2" value="矩形节点" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
  <mxGeometry x="160" y="80" width="120" height="60" as="geometry" />
</mxCell>
```

### 圆角矩形
```xml
<mxCell id="3" value="圆角矩形" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
  <mxGeometry x="160" y="200" width="120" height="60" as="geometry" />
</mxCell>
```

### 圆形节点
```xml
<mxCell id="4" value="圆形" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
  <mxGeometry x="320" y="80" width="120" height="80" as="geometry" />
</mxCell>
```

### 菱形节点
```xml
<mxCell id="5" value="菱形" style="rhombus;whiteSpace=wrap;html=1;" vertex="1" parent="1">
  <mxGeometry x="320" y="200" width="120" height="120" as="geometry" />
</mxCell>
```

### 泳道/容器
```xml
<mxCell id="6" value="泳道" style="swimlane;fontStyle=1;align=center;verticalAlign=top;childLayout=stackLayout;horizontal=1;startSize=26;horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=1;marginBottom=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
  <mxGeometry x="80" y="360" width="320" height="160" as="geometry" />
</mxCell>
```

## 连接器

### 直线连接
```xml
<mxCell id="7" value="" style="endArrow=classic;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="2" target="3">
  <mxGeometry width="50" height="50" relative="1" as="geometry" />
</mxCell>
```

### 带标签的连接
```xml
<mxCell id="8" value="流程" style="endArrow=classic;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="3" target="4">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

### 虚线连接
```xml
<mxCell id="9" value="" style="endArrow=classic;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;dashed=1;" edge="1" parent="1" source="4" target="5">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

## 样式配置

### 颜色和填充
```xml
<!-- 蓝色背景，白色文字 -->
<mxCell id="10" value="蓝色节点" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#333333;" vertex="1" parent="1">
  <mxGeometry x="480" y="80" width="120" height="60" as="geometry" />
</mxCell>

<!-- 绿色背景 -->
<mxCell id="11" value="绿色节点" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontColor=#333333;" vertex="1" parent="1">
  <mxGeometry x="480" y="200" width="120" height="60" as="geometry" />
</mxCell>

<!-- 红色背景 -->
<mxCell id="12" value="红色节点" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontColor=#333333;" vertex="1" parent="1">
  <mxGeometry x="480" y="320" width="120" height="60" as="geometry" />
</mxCell>
```

### 阴影和渐变
```xml
<!-- 带阴影 -->
<mxCell id="13" value="阴影节点" style="rounded=1;whiteSpace=wrap;html=1;shadow=1;" vertex="1" parent="1">
  <mxGeometry x="640" y="80" width="120" height="60" as="geometry" />
</mxCell>

<!-- 渐变填充 -->
<mxCell id="14" value="渐变节点" style="rounded=1;whiteSpace=wrap;html=1;gradientColor=#7ea6e0;" vertex="1" parent="1">
  <mxGeometry x="640" y="200" width="120" height="60" as="geometry" />
</mxCell>
```

## 常见示例

### 示例 1：系统架构图
```xml
<mxfile host="app.diagrams.net" modified="2024-01-01T00:00:00.000Z" agent="Skill" version="22.0.0">
  <diagram name="System Architecture" id="diagram-1">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="850" pageHeight="1100" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        
        <!-- 前端层 -->
        <mxCell id="frontend" value="前端层" style="swimlane;fontStyle=1;align=center;verticalAlign=top;childLayout=stackLayout;horizontal=1;startSize=26;horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=1;marginBottom=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="40" y="40" width="280" height="120" as="geometry" />
        </mxCell>
        <mxCell id="web" value="Web 应用" style="text;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;spacingLeft=4;spacingRight=4;overflow=hidden;rotatable=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;whiteSpace=wrap;html=1;" vertex="1" parent="frontend">
          <mxGeometry y="26" width="280" height="26" as="geometry" />
        </mxCell>
        <mxCell id="mobile" value="移动应用" style="text;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;spacingLeft=4;spacingRight=4;overflow=hidden;rotatable=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;whiteSpace=wrap;html=1;" vertex="1" parent="frontend">
          <mxGeometry y="52" width="280" height="26" as="geometry" />
        </mxCell>
        
        <!-- 后端层 -->
        <mxCell id="backend" value="后端层" style="swimlane;fontStyle=1;align=center;verticalAlign=top;childLayout=stackLayout;horizontal=1;startSize=26;horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=1;marginBottom=0;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
          <mxGeometry x="40" y="200" width="280" height="120" as="geometry" />
        </mxCell>
        <mxCell id="api" value="API 网关" style="text;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;spacingLeft=4;spacingRight=4;overflow=hidden;rotatable=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;whiteSpace=wrap;html=1;" vertex="1" parent="backend">
          <mxGeometry y="26" width="280" height="26" as="geometry" />
        </mxCell>
        <mxCell id="service" value="业务服务" style="text;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;spacingLeft=4;spacingRight=4;overflow=hidden;rotatable=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;whiteSpace=wrap;html=1;" vertex="1" parent="backend">
          <mxGeometry y="52" width="280" height="26" as="geometry" />
        </mxCell>
        
        <!-- 数据层 -->
        <mxCell id="database" value="数据库" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="1">
          <mxGeometry x="120" y="360" width="120" height="80" as="geometry" />
        </mxCell>
        
        <!-- 连接 -->
        <mxCell id="conn1" value="" style="endArrow=classic;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="frontend" target="backend">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="conn2" value="" style="endArrow=classic;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="backend" target="database">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

### 示例 2：流程图
```xml
<mxfile host="app.diagrams.net" modified="2024-01-01T00:00:00.000Z" agent="Skill" version="22.0.0">
  <diagram name="Flowchart" id="diagram-1">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="850" pageHeight="1100" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        
        <!-- 开始节点 -->
        <mxCell id="start" value="开始" style="ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
          <mxGeometry x="200" y="40" width="120" height="60" as="geometry" />
        </mxCell>
        
        <!-- 处理节点 -->
        <mxCell id="process1" value="检查条件" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="200" y="140" width="120" height="60" as="geometry" />
        </mxCell>
        
        <!-- 判断节点 -->
        <mxCell id="decision" value="条件满足?" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="1">
          <mxGeometry x="180" y="240" width="160" height="100" as="geometry" />
        </mxCell>
        
        <!-- 分支 A -->
        <mxCell id="branchA" value="执行 A" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="80" y="380" width="120" height="60" as="geometry" />
        </mxCell>
        
        <!-- 分支 B -->
        <mxCell id="branchB" value="执行 B" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="1">
          <mxGeometry x="320" y="380" width="120" height="60" as="geometry" />
        </mxCell>
        
        <!-- 结束节点 -->
        <mxCell id="end" value="结束" style="ellipse;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="1">
          <mxGeometry x="200" y="480" width="120" height="60" as="geometry" />
        </mxCell>
        
        <!-- 连接 -->
        <mxCell id="c1" value="" style="endArrow=classic;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="start" target="process1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="c2" value="" style="endArrow=classic;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="process1" target="decision">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="c3" value="是" style="endArrow=classic;html=1;exitX=0;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="decision" target="branchA">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="c4" value="否" style="endArrow=classic;html=1;exitX=1;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="decision" target="branchB">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="c5" value="" style="endArrow=classic;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="branchA" target="end">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="c6" value="" style="endArrow=classic;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=1;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="branchB" target="end">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## 常用样式参考

### 颜色方案
- 蓝色：`fillColor=#dae8fc;strokeColor=#6c8ebf;`
- 绿色：`fillColor=#d5e8d4;strokeColor=#82b366;`
- 红色：`fillColor=#f8cecc;strokeColor=#b85450;`
- 黄色：`fillColor=#fff2cc;strokeColor=#d6b656;`
- 紫色：`fillColor=#e1d5e7;strokeColor=#9673a6;`
- 橙色：`fillColor=#ffe6cc;strokeColor=#d79b00;`

### 连接点位置
- 中心：`exitX=0.5;exitY=0.5;`
- 上：`exitX=0.5;exitY=0;`
- 下：`exitX=0.5;exitY=1;`
- 左：`exitX=0;exitY=0.5;`
- 右：`exitX=1;exitY=0.5;`

## 注意事项
- XML 格式必须正确，注意标签闭合
- 每个节点必须有唯一的 `id`
- 连接器通过 `source` 和 `target` 引用节点 ID
- 支持中文，建议使用 UTF-8 编码
- 复杂图表建议使用 DrawIO 编辑器手动创建
