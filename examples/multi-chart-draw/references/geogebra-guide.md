# GeoGebra 语法参考

## 目录
1. [基础语法](#基础语法)
2. [函数绘图](#函数绘图)
3. [几何图形](#几何图形)
4. [圆锥曲线](#圆锥曲线)
5. [代数运算](#代数运算)
6. [统计分析](#统计分析)
7. [图表命令](#图表命令)
8. [变换命令](#变换命令)
9. [3D 命令](#3d-命令)
10. [列表命令](#列表命令)
11. [文本命令](#文本命令)
12. [常见示例](#常见示例)
13. [高级功能](#高级功能)
14. [CAS 命令](#cas-命令代数系统)
15. [完整命令索引](#完整命令索引)
16. [完整工具索引](#完整工具索引)

## 概览
GeoGebra 是一个动态数学软件，支持函数绘图、几何图形、代数运算、统计分析等功能。本 Skill 使用 GeoGebra 的命令行语法生成数学图形。

**官方文档**: https://geogebra.github.io/docs/manual/en/commands/

## 基础语法

### 命令格式
```
命令名称(参数1, 参数2, ...)
```

### 变量赋值
```
f(x) = x^2
a = 5
A = (1, 2)
```

### 注释
```
# 这是注释
```

## 函数绘图

### 基本函数
```
f(x) = x^2
g(x) = sin(x)
h(x) = e^x
k(x) = log(x)
```

### 多项式函数
```
p(x) = 3x^3 - 2x^2 + 5x - 1
q(x) = x^4 + 2x^3 - x^2 + 4
```

### 三角函数
```
sin(x)
cos(x)
tan(x)
asin(x)  # 反正弦
acos(x)  # 反余弦
atan(x)  # 反正切
```

### 指数和对数
```
e^x
2^x
10^x
log(x)   # 自然对数
log10(x) # 常用对数
log2(x)  # 以2为底的对数
```

### 分段函数
```
f(x) = If(x < 0, -x, x)
g(x) = If(x < -1, -1, x > 1, 1, x)
```

### 参数方程
```
Curve(cos(t), sin(t), t, 0, 2π)
```

## 几何图形

### 点
```
A = (1, 2)
B = (3, 4)
C = (0, 0)
```

### 线段
```
Segment(A, B)
s = Segment((0, 0), (1, 1))
```

### 直线
```
Line(A, B)
y = 2x + 3
```

### 射线
```
Ray(A, B)
```

### 圆
```
Circle(A, 3)  # 以 A 为圆心，半径为 3 的圆
Circle((0, 0), 5)
Circle((1, 1), (4, 5))  # 以两点为直径的圆
```

### 多边形
```
Polygon(A, B, C)
Polygon((0, 0), (1, 0), (1, 1), (0, 1))
Pentagon(A, B)  # 正五边形
```

### 角度
```
Angle(A, B, C)
α = Angle((1, 0), (0, 0), (0, 1))  # 90度
```

### 轨迹
```
Locus(C, A)  # 点 C 随点 A 移动的轨迹
```

## 代数运算

### 解方程
```
Solve(x^2 - 5x + 6 = 0)
Solve(2x + 3 = 7)
```

### 解不等式
```
Solve(x^2 > 4)
Solve(2x + 3 < 7)
```

### 导数
```
f(x) = x^3 - 2x^2 + x
Derivative(f)  # f'(x)
f'(2)  # f 在 x=2 处的导数
```

### 积分
```
Integral(x^2)  # ∫x²dx
Integral(sin(x), 0, π)  # 定积分
```

### 极限
```
Limit((sin(x))/x, 0)
Limit((1 + 1/x)^x, +∞)
```

## 统计分析

### 数据集
```
data = {1, 2, 3, 4, 5, 6}
```

### 统计量
```
Mean(data)    # 平均值
Median(data)  # 中位数
Mode(data)    # 众数
StdDev(data)  # 标准差
Variance(data)  # 方差
```

### 柱状图
```
BarChart(data)
```

### 箱线图
```
BoxPlot(data)
```

### 直方图
```
Histogram(data)
```

## 常见示例

### 示例 1：基本函数绘图
```
f(x) = x^2
g(x) = x^3
h(x) = sqrt(x)
```

### 示例 2：三角函数组合
```
f(x) = sin(x)
g(x) = cos(x)
h(x) = sin(x) + cos(x)
k(x) = sin(2x)
```

### 示例 3：函数图像比较
```
f(x) = x^2
g(x) = 2^x
h(x) = e^x
```

### 示例 4：几何图形
```
A = (0, 0)
B = (4, 0)
C = (2, 3)
Polygon(A, B, C)  # 三角形
Circle(A, 2)
Circle(B, 1.5)
Circle(C, 1)
```

### 示例 5：圆内接多边形
```
Circle((0, 0), 3)
Hexagon((0, 0), 3)  # 正六边形
```

### 示例 6：抛物线和切线
```
f(x) = x^2
a = 2
g(x) = Derivative(f, a)(x - a) + f(a)  # 在 x=2 处的切线
```

### 示例 7：参数方程绘制
```
Curve(cos(t), sin(t), t, 0, 2π)  # 单位圆
Curve(3cos(t), 2sin(t), t, 0, 2π)  # 椭圆
Curve(t, t^2, t, -2, 2)  # 抛物线
```

### 示例 8：函数与导数
```
f(x) = x^3 - 3x^2 + 2x
g(x) = Derivative(f)  # f'(x) = 3x^2 - 6x + 2
h(x) = Integral(g)  # ∫f'(x)dx
```

### 示例 9：分段函数
```
f(x) = If(x < 0, -1, If(x = 0, 0, 1))
g(x) = If(x < 0, x^2, x)
```

### 示例 10：统计图表
```
data = {12, 15, 18, 22, 25, 28, 30}
Mean(data)
Median(data)
StdDev(data)
BarChart(data)
```

### 示例 11：三角函数图像
```
f(x) = sin(x)
g(x) = 2sin(x)
h(x) = sin(2x)
k(x) = sin(x + π/2)
```

### 示例 12：对数函数
```
f(x) = log(x)
g(x) = log10(x)
h(x) = log2(x)
k(x) = ln(x + 1)
```

### 示例 13：指数函数
```
f(x) = e^x
g(x) = 2^x
h(x) = 0.5^x
```

### 示例 14：几何构造
```
A = (0, 0)
B = (4, 0)
C = (4, 3)
D = (0, 3)
Polygon(A, B, C, D)  # 矩形
E = Midpoint(A, C)  # 对角线中点
Circle(E, Distance(A, E)/2)  # 外接圆
```

### 示例 15：函数变换
```
f(x) = x^2
g(x) = f(x + 2)  # 向左平移
h(x) = f(x) + 3  # 向上平移
k(x) = 2*f(x)    # 纵向拉伸
m(x) = f(2x)     # 横向压缩
```

## 高级功能

### 动态点
```
A = (a, a^2)  # a 是滑动条
```

### 条件显示
```
ShowAxis(true)
ShowGrid(true)
```

### 颜色设置
```
SetColor(f, 255, 0, 0)  # 红色
SetLineThickness(f, 3)
```

### 文本标签
```
Text("原点", (0, 0))
```

## 圆锥曲线

### 椭圆
```
Ellipse(F1, F2, a)              # 焦点 F1, F2，长半轴 a
Ellipse(F1, F2, Segment)        # 焦点和线段（半长轴）
Ellipse((0,0), (4,0), 5)        # 具体示例
```

### 双曲线
```
Hyperbola(F1, F2, a)            # 焦点 F1, F2，实半轴 a
Hyperbola((−3,0), (3,0), 2)     # 具体示例
```

### 抛物线
```
Parabola(F, d)                  # 焦点 F，准线 d
Parabola((0,1), y = -1)         # 具体示例
```

### 圆锥曲线属性
```
Center(c)                       # 圆锥曲线的中心
Focus(c)                        # 获取焦点
Directrix(c)                    # 获取准线
Eccentricity(c)                 # 离心率
MajorAxis(c)                    # 长轴
MinorAxis(c)                    # 短轴
SemiMajorAxisLength(c)          # 半长轴长度
SemiMinorAxisLength(c)          # 半短轴长度
Vertex(c)                       # 顶点
Tangent(Point, Conic)           # 切线
```

## 图表命令

### 柱状图
```
BarChart({1, 2, 3, 4, 5})                    # 简单柱状图
BarChart({10, 20, 15, 25}, 0.5)              # 带宽度
BarChart({1, 2, 3}, {5, 8, 3})               # x值和y值
```

### 饼图
```
PieChart({30, 20, 50})                       # 百分比饼图
PieChart({A, B, C}, {30, 20, 50})            # 带标签
```

### 直方图
```
Histogram({0, 1, 2, 3, 4}, {2, 3, 4, 1})     # 区间和频率
Histogram(list, n)                           # 数据和组数
HistogramRight(...)                          # 右对齐直方图
```

### 箱线图
```
BoxPlot(yOffset, yScale, list)               # 基本箱线图
BoxPlot(1, 0.5, {1, 2, 3, 4, 5, 6, 7, 8})
```

### 其他图表
```
DotPlot(list)                   # 点图
LineGraph(list)                 # 折线图
StepGraph(list)                 # 阶梯图
StickGraph(list)                # 棒形图
StemPlot(list)                  # 茎叶图
FrequencyPolygon(list)          # 频率多边形
NormalQuantilePlot(list)        # 正态分位图
ResidualPlot(list, function)    # 残差图
```

## 变换命令

### 平移
```
Translate(Object, Vector)       # 按向量平移
Translate(A, (3, 2))           # 点 A 平移
Translate(polygon, Vector(B,C)) # 多边形平移
```

### 旋转
```
Rotate(Object, Angle)           # 绕原点旋转
Rotate(Object, Angle, Point)    # 绕指定点旋转
Rotate(A, 45°, B)              # 点 A 绕 B 旋转 45°
Rotate(polygon, π/4, O)         # 弧度制
```

### 反射（镜像）
```
Reflect(Object, Line)           # 关于直线反射
Reflect(Object, Point)          # 关于点反射
Reflect(A, xAxis)               # 关于 x 轴反射
Reflect(A, yAxis)               # 关于 y 轴反射
Reflect(polygon, Line(A, B))    # 多边形反射
```

### 缩放
```
Dilate(Object, Factor)          # 以原点为中心缩放
Dilate(Object, Factor, Point)   # 以指定点为中心缩放
Dilate(A, 2, O)                # 以 O 为中心放大 2 倍
```

### 拉伸和剪切
```
Stretch(Object, Vector)         # 拉伸
Shear(Object, Line, Ratio)      # 剪切
```

## 3D 命令

### 3D 点和线
```
A = (1, 2, 3)                   # 3D 点
Line(A, B)                      # 3D 直线
Segment(A, B)                   # 3D 线段
Ray(A, B)                       # 3D 射线
```

### 平面
```
Plane(A, B, C)                  # 过三点的平面
Plane(Point, Line)              # 过点和直线的平面
Plane(Line, Line)               # 过两直线的平面
PerpendicularPlane(Point, Line) # 垂直平面
```

### 3D 曲面
```
Surface(expr, u, uMin, uMax, v, vMin, vMax)  # 参数曲面
Surface(u*cos(v), u*sin(v), v, u, 0, 2, v, 0, 2π)  # 螺旋面
```

### 球体
```
Sphere(Center, Radius)          # 球心和半径
Sphere(A, 3)                    # 以 A 为圆心，半径 3
Sphere(A, B)                    # 以 AB 为直径
```

### 圆柱和圆锥
```
Cylinder(Circle, Height)        # 圆柱
Cone(Circle, Height)            # 圆锥
Cone(Point, Circle)             # 圆锥（顶点和底面）
```

### 棱柱和棱锥
```
Prism(Polygon, Height)          # 棱柱
Prism(Polygon, Point)           # 棱柱（底面和顶点）
Pyramid(Polygon, Height)        # 棱锥
Pyramid(Polygon, Point)         # 棱锥
```

### 正多面体
```
Cube(A, B)                      # 立方体
Tetrahedron(A, B)               # 正四面体
Octahedron(A, B)                # 正八面体
Dodecahedron(A, B)              # 正十二面体
Icosahedron(A, B)               # 正二十面体
```

### 3D 测量
```
Volume(solid)                   # 体积
Height(solid)                   # 高度
Distance(Point, Plane)          # 点到平面距离
```

## 列表命令

### 列表创建
```
list = {1, 2, 3, 4, 5}          # 创建列表
Sequence(k, k, 1, 10)           # 生成序列 1 到 10
Sequence(k^2, k, 1, 5)          # 平方序列 {1, 4, 9, 16, 25}
Sequence(Point, n)              # 点的列表
```

### 列表操作
```
Element(list, n)                # 获取第 n 个元素
First(list)                     # 第一个元素
First(list, n)                  # 前 n 个元素
Last(list)                      # 最后一个元素
Last(list, n)                   # 后 n 个元素
Take(list, m, n)                # 取第 m 到第 n 个元素
Append(list, element)           # 添加元素
Insert(list, element, pos)      # 插入元素
Remove(list, n)                 # 删除第 n 个元素
RemoveUndefined(list)           # 删除未定义元素
Reverse(list)                   # 反转列表
Sort(list)                      # 排序
Shuffle(list)                   # 随机打乱
Unique(list)                    # 去重
```

### 列表运算
```
Length(list)                    # 列表长度
Sum(list)                       # 求和
Product(list)                   # 求积
Max(list)                       # 最大值
Min(list)                       # 最小值
Mean(list)                      # 平均值
Median(list)                    # 中位数
```

### 列表筛选
```
KeepIf(condition, list)         # 条件筛选
CountIf(condition, list)        # 条件计数
Zip(list1, list2, expression)   # 合并列表
Sample(list, n)                 # 随机抽样
```

### 集合运算
```
Union(list1, list2)             # 并集
Intersection(list1, list2)      # 交集
```

## 文本命令

### 文本创建
```
Text("Hello World")             # 创建文本
Text("值 = ", a)                # 带变量的文本
Text(value, Point)              # 在指定位置显示文本
```

### 文本格式
```
FormulaText(f)                  # 公式文本（LaTeX）
FractionText(0.5)               # 分数文本 "1/2"
ScientificText(1234567)         # 科学计数法
SurdText(sqrt(2))               # 根号文本
TableText(matrix)               # 表格文本
VerticalText("text")            # 垂直文本
RotateText("text", angle)       # 旋转文本
```

### 文本操作
```
Length(text)                    # 文本长度
IndexOf("a", "abc")             # 查找位置
ReplaceAll(text, "old", "new")  # 替换
Split(text, separator)          # 分割
Take(text, m, n)                # 截取
```

### 编码转换
```
LetterToUnicode("A")            # 字母转 Unicode
UnicodeToLetter(65)             # Unicode 转字母
TextToUnicode("text")           # 文本转 Unicode 列表
UnicodeToText(list)             # Unicode 列表转文本
```

## CAS 命令（代数系统）

### 因式分解和展开
```
Factor(x^2 - 1)                 # 因式分解 → (x-1)(x+1)
CFactor(x^2 + 1)                # 复数因式分解
Expand((x+1)^3)                 # 展开
PartialFractions(expr)          # 部分分式
Simplify(expr)                  # 化简
Rationalize(expr)               # 有理化
```

### 解方程
```
Solve(x^2 = 4)                  # 求解 → {-2, 2}
Solve({x + y = 1, x - y = 0}, {x, y})  # 方程组
CSolve(x^2 + 1 = 0)             # 复数解
NSolve(x^3 - x - 1 = 0)         # 数值解
Solutions(x^2 = 4)              # 解集列表
```

### 微积分
```
Derivative(f)                   # 一阶导数
Derivative(f, 2)                # 二阶导数
Derivative(f, x, n)             # n 阶导数
Integral(f)                     # 不定积分
Integral(f, a, b)               # 定积分
Limit(f, a)                     # 极限
Limit(f, a, +)                  # 右极限
Limit(f, a, -)                  # 左极限
TaylorPolynomial(f, a, n)       # 泰勒多项式
```

### 数论
```
GCD(a, b)                       # 最大公约数
LCM(a, b)                       # 最小公倍数
IsPrime(n)                      # 是否质数
PrimeFactors(n)                 # 质因数分解
Divisors(n)                     # 所有因子
Mod(a, b)                       # 取模
```

## 注意事项
- 每行一个命令
- 命令区分大小写
- 希腊字母可以用 π 表示，也可用 pi
- 幂运算用 ^ 符号
- 角度可用 ° 符号或弧度
- 支持中文注释（# 开头）
- 支持所有常见数学函数
- 输出为 HTML，可在浏览器中交互查看
- **重要**: 命令语法必须正确，否则会报错"请检查输入内容"

---

## 完整命令索引

> 官方文档: https://geogebra.github.io/docs/manual/en/commands/

### 3D Commands (3D 命令)
```
Angle, Axes, Bottom, Center, Circle, CircularArc, CircularSector,
CircumcircularArc, CircumcircularSector, Circumference, Cone, Cube,
Curve, Cylinder, Distance, Dodecahedron, Ends, Function, Height,
Icosahedron, Incircle, InfiniteCone, InfiniteCylinder, InteriorAngles,
Intersect, IntersectConic, IntersectPath, Line, Midpoint, Net,
Octahedron, Perimeter, PerpendicularBisector, PerpendicularLine,
PerpendicularPlane, Plane, PlaneBisector, Point, PointIn, Polygon,
Polyline, Prism, Pyramid, Radius, Ray, Segment, Side, Sphere,
Surface, Tetrahedron, Top, Vertex, Volume
```

### Algebra Commands (代数命令)
```
AreEqual, Assume, BinomialCoefficient, CFactor, CIFactor, CSolutions,
CSolve, Coefficients, CommonDenominator, CompleteSquare, ComplexRoot,
ContinuedFraction, Degree, Denominator, Div, Division, Divisors,
DivisorsList, DivisorsSum, Eliminate, Expand, ExtendedGCD, Factor,
Factors, FromBase, GCD, GeometricMean, HarmonicMean, IFactor,
IsFactored, IsInteger, IsPrime, LCM, LeftSide, Max, Mean, Midpoint,
Min, MixedNumber, Mod, ModularExponent, NSolutions, NSolve, NextPrime,
Normalize, Numerator, Numeric, ParseToNumber, PartialFractions,
PlotSolve, Polynomial, PreviousPrime, PrimeFactors, Product,
RandomBetween, RandomPolynomial, Rationalize, RightSide, Root,
Simplify, Solutions, Solve, SolveCubic, SolveQuartic, Substitute,
Sum, ToBase, Vertex
```

### Chart Commands (图表命令)
```
BarChart, BoxPlot, ContingencyTable, DotPlot, FrequencyPolygon,
FrequencyTable, Histogram, HistogramRight, LineGraph, NormalQuantilePlot,
PieChart, ResidualPlot, StemPlot, StepGraph, StickGraph
```

### Conic Commands (圆锥曲线命令)
```
Axes, Center, Circle, Circumference, Coefficients, Conic,
ConjugateDiameter, Curvature, Directrix, Eccentricity, Ellipse,
Focus, Hyperbola, Incircle, LinearEccentricity, MajorAxis, Midpoint,
MinorAxis, OsculatingCircle, Parabola, Parameter, PathParameter,
Perimeter, Polar, Radius, Sector, SemiMajorAxisLength,
SemiMinorAxisLength, Semicircle, Tangent, Type, Vertex
```

### Discrete Math Commands (离散数学命令)
```
ConvexHull, DelaunayTriangulation, MinimumSpanningTree,
ShortestDistance, TravelingSalesman, Voronoi
```

### Functions and Calculus Commands (函数与微积分命令)
```
Asymptote, Coefficients, ComplexRoot, Cubic, Curvature, CurvatureVector,
Curve, DataFunction, Degree, Denominator, Derivative, Extremum, Factor,
Factors, Function, ImplicitCurve, ImplicitDerivative, InflectionPoint,
Integral, IntegralBetween, IntegralSymbolic, Intersect, Invert,
InverseLaplace, IsVertexForm, Iteration, IterationList, Laplace,
LeftSum, Length, Limit, LimitAbove, LimitBelow, LowerSum, Max, Min,
NDerivative, NIntegral, NInvert, NSolveODE, Normalize, Numerator,
OsculatingCircle, ParametricDerivative, ParseToFunction, PartialFractions,
PathParameter, PlotSolve, Polynomial, Product, RandomPolynomial,
RectangleSum, RemovableDiscontinuity, Root, RootList, Roots, Simplify,
SlopeField, SolveODE, Spline, Sum, Tangent, TaylorPolynomial, ToComplex,
ToExponential, ToPoint, ToPolar, TrapezoidalSum, TriangleCurve,
TrigCombine, TrigExpand, TrigSimplify, UpperSum
```

### Geometry Commands (几何命令)
```
AffineRatio, Angle, AngleBisector, Arc, Area, AreCollinear, AreConcurrent,
AreConcyclic, AreCongruent, AreEqual, AreParallel, ArePerpendicular,
Barycenter, Centroid, Circle, CircularArc, CircularSector,
CircumcircularArc, CircumcircularSector, Circumference, ClosestPoint,
ClosestPointRegion, CrossRatio, Cubic, Difference, Direction, Distance,
Envelope, Incircle, InteriorAngles, Intersect, IntersectPath, IsInRegion,
IsTangent, Length, Line, Locus, LocusEquation, Midpoint, PathParameter,
Perimeter, PerpendicularBisector, PerpendicularLine, Point, PointIn,
Polygon, Polyline, Prove, ProveDetails, Radius, RandomPointIn, Ray,
RigidPolygon, Sector, Segment, Semicircle, Slope, Tangent, TriangleCenter,
TriangleCurve, Trilinear, Union, Type, Vertex
```

### GeoGebra Commands (GeoGebra 专用命令)
```
AxisStepX, AxisStepY, CASLoaded, ConstructionStep, Corner,
DynamicCoordinates, Name, Object, SetConstructionStep, SlowPlot, ToolImage
```

### List Commands (列表命令)
```
Append, Classes, CountIf, DataFunction, Element, First, Flatten,
Frequency, IndexOf, Insert, Intersection, Join, KeepIf, Last, Max,
Mean, Min, Normalize, OrdinalRank, PointList, Product, RandomElement,
RandomPointIn, Remove, RemoveUndefined, Reverse, RootList, Sample,
SelectedElement, SelectedIndex, Sequence, Shuffle, Sort, Sum, Take,
TiedRank, Union, Unique, Zip
```

### Logic Commands (逻辑命令)
```
CountIf, If, IsDefined, IsFactored, IsInRegion, IsInteger, IsPrime,
IsTangent, IsVertexForm, KeepIf, Relation
```

### Optimization Commands (优化命令)
```
Maximize, Minimize
```

### Probability Commands (概率命令)
```
Bernoulli, BetaDist, BinomialCoefficient, BinomialDist, Cauchy,
ChiSquared, ChiSquaredTest, Erlang, Exponential, FDistribution, Gamma,
HyperGeometric, InverseBeta, InverseBinomial, InverseBinomialMinimumTrials,
InverseCauchy, InverseChiSquared, InverseExponential, InverseFDistribution,
InverseGamma, InverseHyperGeometric, InverseLogNormal, InverseLogistic,
InverseNormal, InversePascal, InversePoisson, InverseTDistribution,
InverseWeibull, InverseZipf, LogNormal, Logistic, Normal, Pascal, Poisson,
RandomBetween, RandomBinomial, RandomDiscrete, RandomNormal, RandomPointIn,
RandomPoisson, RandomPolynomial, RandomUniform, TDistribution, Triangular,
Uniform, Weibull, Zipf
```

### Scripting Commands (脚本命令)
```
AttachCopyToView, Button, CenterView, Checkbox, CopyFreeObject, Delete,
Execute, ExportImage, GetTime, HideLayer, InputBox, Pan, ParseToFunction,
ParseToNumber, PlaySound, ReadText, Rename, Repeat, RunClickScript,
RunUpdateScript, SelectObjects, SetActiveView, SetAxesRatio,
SetBackgroundColor, SetCaption, SetColor, SetConditionToShowObject,
SetConstructionStep, SetCoords, SetDecoration, SetDynamicColor, SetFilling,
SetFixed, SetImage, SetLabelMode, SetLayer, SetLevelOfDetail, SetLineOpacity,
SetLineStyle, SetLineThickness, SetPerspective, SetPointSize, SetPointStyle,
SetSeed, SetSpinSpeed, SetTooltipMode, SetTrace, SetValue, SetViewDirection,
SetVisibleInView, ShowAxes, ShowGrid, ShowLabel, ShowLayer, Slider,
StartAnimation, StartRecord, Turtle, TurtleBack, TurtleDown, TurtleForward,
TurtleLeft, TurtleRight, TurtleUp, UpdateConstruction, ZoomIn, ZoomOut
```

### Spreadsheet Commands (电子表格命令)
```
Cell, CellRange, Column, ColumnName, FillCells, FillColumn, FillRow, Row
```

### Statistics Commands (统计命令)
```
ANOVA, ChiSquaredTest, Classes, ContingencyTable, CorrelationCoefficient,
Covariance, Fit, FitExp, FitGrowth, FitImplicit, FitLine, FitLineX, FitLog,
FitLogistic, FitPoly, FitPow, FitSin, Frequency, FrequencyPolygon,
FrequencyTable, GeometricMean, HarmonicMean, MAD, Max, Mean, MeanX, MeanY,
Median, Min, Mode, Normalize, Percentile, Product, Quartile1, Quartile3,
RSquare, RootMeanSquare, SD, SDX, SDY, Sample, SampleSD, SampleSDX, SampleSDY,
SampleVariance, Shuffle, SigmaXX, SigmaXY, SigmaYY, Spearman, Sum,
SumSquaredErrors, Sxx, Sxy, Syy, TMean2Estimate, TMeanEstimate, TTest,
TTest2, TTestPaired, Variance, ZMean2Estimate, ZMean2Test, ZMeanEstimate,
ZMeanTest, ZProportion2Estimate, ZProportion2Test, ZProportionEstimate,
ZProportionTest
```

### Financial Commands (金融命令)
```
FutureValue, Payment, Periods, PresentValue, Rate
```

### Text Commands (文本命令)
```
ContingencyTable, ContinuedFraction, First, FormulaText, FractionText,
FrequencyTable, IndexOf, Last, Length, LetterToUnicode, Ordinal,
ParseToFunction, ParseToNumber, ReadText, ReplaceAll, RotateText,
ScientificText, Simplify, Split, SurdText, TableText, Take, Text,
TextToUnicode, UnicodeToLetter, UnicodeToText, VerticalText
```

### Transformation Commands (变换命令)
```
Dilate (Enlarge), Reflect, Rotate, Shear, Stretch, Translate
```

### Vector and Matrix Commands (向量与矩阵命令)
```
ApplyMatrix, CharacteristicPolynomial, Cross, CurvatureVector, Determinant,
Dimension, Direction, Dot, Eigenvalues, Eigenvectors, Element, Identity,
Invert, JordanDiagonalization, Length, LUDecomposition, MatrixRank,
MinimalPolynomial, PerpendicularVector, QRDecomposition, ReducedRowEchelonForm,
SVD, ToComplex, ToPolar, Transpose, UnitPerpendicularVector, UnitVector, Vector
```

### CAS Specific Commands (CAS 专用命令)
```
Assume, BinomialCoefficient, BinomialDist, CFactor, CIFactor, CSolutions,
CSolve, Cauchy, ChiSquared, CharacteristicPolynomial, Coefficients,
CommonDenominator, CompleteSquare, ComplexRoot, Covariance, Cross, Degree,
Delete, Denominator, Derivative, Determinant, Dimension, Div, Division,
Divisors, DivisorsList, DivisorsSum, Dot, Eigenvalues, Eigenvectors, Element,
Eliminate, Expand, Exponential, ExtendedGCD, FDistribution, Factor, Factors,
First, FitExp, FitLog, FitPoly, FitPow, FitSin, GCD, Gamma, GroebnerDegRevLex,
GroebnerLex, GroebnerLexDeg, HyperGeometric, IFactor, Identity,
ImplicitDerivative, Integral, IntegralBetween, IntegralSymbolic, Intersect,
InverseLaplace, Invert, IsPrime, JordanDiagonalization, Laplace, Last, LCM,
LeftSide, Length, Limit, LimitAbove, LimitBelow, LUDecomposition, MatrixRank,
Max, Mean, Median, Min, MinimalPolynomial, MixedNumber, Mod, ModularExponent,
NIntegral, NSolutions, NSolve, NextPrime, Normal, Numerator, Numeric,
PartialFractions, Pascal, PerpendicularVector, PlotSolve, Poisson, Polynomial,
PreviousPrime, PrimeFactors, Product, QRDecomposition, RandomBetween,
RandomBinomial, RandomElement, RandomNormal, RandomPoisson, RandomPolynomial,
RandomUniform, Rationalize, ReducedRowEchelonForm, RightSide, Root, RootList,
SD, Sample, SampleSD, SampleVariance, Sequence, Shuffle, Simplify, Solutions,
Solve, SolveCubic, SolveODE, SolveQuartic, Substitute, Sum, SVD, TDistribution,
Take, TaylorPolynomial, ToComplex, ToExponential, ToPoint, ToPolar, Transpose,
Unique, UnitPerpendicularVector, UnitVector, Variance, Weibull, Zipf
```

---

## 完整工具索引

> 官方文档: https://geogebra.github.io/docs/manual/en/tools/

### Movement Tools (移动工具)
```
Move                    # 移动对象
Move around Point       # 绕点移动
Freehand Shape          # 手绘图形
Pen                     # 画笔
```

### Point Tools (点工具)
```
Point                   # 创建点
Point on Object         # 对象上的点
Attach/Detach Point     # 附着/分离点
Intersect               # 交点
Midpoint or Center      # 中点或圆心
Complex Number          # 复数点
Extremum                # 极值点
Roots                   # 根（零点）
```

### Line Tools (直线工具)
```
Line                    # 直线（过两点）
Segment                 # 线段
Segment with Given Length   # 定长线段
Ray                     # 射线
Polyline                # 折线
Vector                  # 向量
Vector from Point       # 从点出发的向量
```

### Special Line Tools (特殊直线工具)
```
Perpendicular Line      # 垂线
Parallel Line           # 平行线
Perpendicular Bisector  # 垂直平分线
Angle Bisector          # 角平分线
Tangents                # 切线
Polar or Diameter Line  # 极线或直径
Best Fit Line           # 最佳拟合线
Locus                   # 轨迹
```

### Polygon Tools (多边形工具)
```
Polygon                 # 多边形
Regular Polygon         # 正多边形
Rigid Polygon           # 刚性多边形
Vector Polygon          # 向量多边形
```

### Circle and Arc Tools (圆和弧工具)
```
Circle with Centre through Point    # 过点的圆（圆心+点）
Circle with Centre and Radius       # 定半径圆
Compass                             # 圆规
Circle through 3 Points             # 过三点的圆
Semicircle through 2 Points         # 过两点的半圆
Circular Arc                        # 圆弧
Circumcircular Arc                  # 外接圆弧
Circular Sector                     # 扇形
Circumcircular Sector               # 外接圆扇形
```

### Conic Section Tools (圆锥曲线工具)
```
Ellipse                 # 椭圆
Hyperbola               # 双曲线
Parabola                # 抛物线
Conic through 5 Points  # 过五点的圆锥曲线
```

### Measurement Tools (测量工具)
```
Angle                   # 角度
Angle with Given Size   # 定大小的角
Distance or Length      # 距离或长度
Area                    # 面积
Slope                   # 斜率
List                    # 列表
Relation                # 关系
Function Inspector      # 函数检查器
```

### Transformation Tools (变换工具)
```
Reflect about Line      # 关于直线反射
Reflect about Point     # 关于点反射
Reflect about Circle    # 关于圆反射（反演）
Rotate around Point     # 绕点旋转
Translate by Vector     # 按向量平移
Dilate from Point       # 以点为中心缩放
```

### Special Object Tools (特殊对象工具)
```
Text                    # 文本
Image                   # 图片
Pen                     # 画笔
Freehand Shape          # 手绘图形
Function Inspector      # 函数检查器
Relation                # 关系
```

### Action Object Tools (动作对象工具)
```
Slider                  # 滑动条
Button                  # 按钮
Check Box               # 复选框
Input Box               # 输入框
Text                    # 文本
Image                   # 图片
```

### General Tools (通用工具)
```
Move Graphics View      # 移动视图
Zoom In                 # 放大
Zoom Out                # 缩小
Show/Hide Object        # 显示/隐藏对象
Show/Hide Label         # 显示/隐藏标签
Copy Visual Style       # 复制样式
Delete                  # 删除
```

### CAS Tools (CAS 工具)
```
Evaluate                # 求值
Numeric                 # 数值计算
Keep Input              # 保持输入
Factor                  # 因式分解
Expand                  # 展开
Substitute              # 替换
Solve                   # 求解
Derivative              # 求导
Integral                # 积分
```

### Spreadsheet Tools (电子表格工具)
```
Move                    # 移动
One Variable Analysis   # 单变量分析
Two Variable Regression Analysis  # 双变量回归分析
Multiple Variable Analysis        # 多变量分析
Create List             # 创建列表
Create List of Points   # 创建点列表
Create Matrix           # 创建矩阵
Create Table            # 创建表格
Create Polyline         # 创建折线
Sum                     # 求和
Mean                    # 平均值
Count                   # 计数
Max                     # 最大值
Min                     # 最小值
```

### 3D Graphics Tools (3D 图形工具)
```
# 移动工具
Move (3D)               # 3D 移动
Rotate 3D Graphics View # 旋转 3D 视图

# 点工具
Point (3D)              # 3D 点
Point on Object (3D)    # 对象上的点
Intersect (3D)          # 交点
Midpoint or Center (3D) # 中点或圆心
Attach/Detach Point     # 附着/分离点

# 直线工具
Line (3D)               # 3D 直线
Segment (3D)            # 3D 线段
Ray (3D)                # 3D 射线
Vector (3D)             # 3D 向量
Perpendicular Line (3D) # 3D 垂线

# 多边形工具
Polygon (3D)            # 3D 多边形

# 圆和弧工具
Circle with Axis through Point      # 过点的圆（轴+点）
Circle with Centre, Radius and Direction  # 定圆心、半径和方向的圆
Circle through 3 Points (3D)        # 过三点的圆
Circular Arc (3D)                   # 圆弧
Circumcircular Arc (3D)             # 外接圆弧
Circular Sector (3D)                # 扇形
Circumcircular Sector (3D)          # 外接圆扇形

# 交集工具
Intersect Two Surfaces              # 两曲面交线
Intersection Curve                  # 交线

# 平面工具
Plane through 3 Points              # 过三点的平面
Plane                               # 平面
Perpendicular Plane                 # 垂直平面

# 立体几何工具
Pyramid                 # 棱锥
Prism                   # 棱柱
Cone                    # 圆锥
Cylinder                # 圆柱
Sphere with Centre through Point    # 球（圆心+点）
Sphere with Centre and Radius       # 定半径球
Extrude to Pyramid or Cone          # 拉伸为棱锥或圆锥
Extrude to Prism or Cylinder        # 拉伸为棱柱或圆柱
Net                     # 展开图
Cube                    # 立方体
Tetrahedron             # 正四面体
Octahedron              # 正八面体
Dodecahedron            # 正十二面体
Icosahedron             # 正二十面体

# 测量工具 (3D)
Angle (3D)              # 3D 角度
Distance or Length (3D) # 3D 距离或长度
Area (3D)               # 3D 面积
Volume                  # 体积

# 变换工具 (3D)
Reflect about Plane     # 关于平面反射
Rotate around Line      # 绕直线旋转
Translate by Vector (3D)# 按向量平移
Dilate from Point (3D)  # 以点为中心缩放

# 通用工具 (3D)
Rotate 3D Graphics View # 旋转视图
Move Graphics View (3D) # 移动视图
Zoom In (3D)            # 放大
Zoom Out (3D)           # 缩小
Show/Hide Object (3D)   # 显示/隐藏对象
Show/Hide Label (3D)    # 显示/隐藏标签
Copy Visual Style (3D)  # 复制样式
Delete (3D)             # 删除
View in front of        # 正视图
```
