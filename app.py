import streamlit as st
import dashscope
from dashscope import Generation
import os

# ===================== 配置 =====================
# 优先从 Streamlit Secrets 读取，其次环境变量
try:
    dashscope.api_key = st.secrets["DASHSCOPE_API_KEY"]
except Exception:
    dashscope.api_key = os.getenv("DASHSCOPE_API_KEY", "")

# ===================== Prompt 模板 =====================

PROMPT_ORAL_SCRIPT = """你是一个专业的二手房短视频文案策划师，擅长撰写吸引人的房源讲解口播稿。

## 你的风格特点：
- 说人话，不要中介腔，像朋友推荐好房子一样自然
- 开头3秒必须有钩子（要么抛问题，要么给结论，要么制造冲突）
- 突出核心卖点，最多讲3个（多了记不住）
- 适当提缺点（增加可信度，但要把缺点转化为优势或弱化处理）
- 结尾有互动引导（扣1、评论区留言、点击主页等）

## 房源信息：
- 小区名称：{community}
- 城市/区域：{city}{district}
- 户型：{layout}
- 面积：{area}㎡
- 楼层：{floor}层/共{total_floor}层
- 朝向：{orientation}
- 装修情况：{decoration}
- 挂牌价格：{price}万（单价约{unit_price}元/㎡）
- 房龄：{age}年
- 核心卖点：{highlights}
- 不足之处：{drawbacks}
- 特殊信息：{extra}

## 请生成以下三版口播稿：

### 版本A：30秒短视频（约100-120字）
要求：节奏快、信息密度高、适合抖音/快手

### 版本B：60秒中视频（约220-260字）
要求：有故事感、适合小红书/视频号

### 版本C：3分钟详细讲解（约600-700字）
要求：适合深度介绍，涵盖户型解析、周边配套、适合人群分析

每版都要包含：
1. 开头钩子（前3秒）
2. 核心内容
3. 互动结尾"""

PROMPT_TITLES = """你是一个短视频运营专家，擅长写高点击率的房源视频标题。

## 标题写作原则：
- 有数字（面积、价格、楼层）
- 有情绪词（急售、捡漏、后悔、真香、劝退）
- 有冲突/悬念
- 长度：15-25字
- 包含地域关键词

## 房源基本信息：
- 小区：{community}
- 区域：{city}{district}
- 户型：{layout}
- 面积：{area}㎡
- 价格：{price}万
- 核心卖点：{highlights}
- 特殊标签：{extra}

## 请生成5个标题，分别采用以下策略：
1. 价格冲击型（突出性价比/捡漏感）
2. 悬念好奇型（引发点击欲望）
3. 痛点共鸣型（戳中买房人的纠结点）
4. 数据对比型（用数字制造冲突）
5. 身份代入型（让特定人群觉得"说的就是我"）

每个标题后面附一句话说明为什么这么写。"""

PROMPT_MULTI_PLATFORM = """你是一个多平台内容运营专家。请根据以下房源信息，分别生成三个平台的发布文案。

## 房源信息：
- 小区：{community}
- 城市区域：{city}{district}
- 户型面积：{layout} {area}㎡
- 价格：{price}万
- 核心卖点：{highlights}
- 不足之处：{drawbacks}

## 请输出：

### 抖音版（视频描述）
- 长度：50-100字
- 风格：口语化、有梗、带emoji
- 必须包含：3-5个话题标签（#太原买房 #二手房 等）
- 互动引导：引导评论

### 小红书版（笔记正文）
- 长度：200-400字
- 风格：分段清晰、有干货感、多用emoji分隔
- 结构：【开头吸引】+【房源亮点1/2/3】+【适合人群】+【总结建议】
- 必须包含：话题标签+关键词

### 视频号版（视频描述）
- 长度：80-150字
- 风格：相对正式、可信感强
- 互动引导：引导私信或添加微信"""

PROMPT_COMMENTS = """你是一个房产短视频账号的运营助手。请针对以下房源，生成常见评论的回复话术。

## 房源信息：
- 小区：{community}
- 价格：{price}万
- 户型：{layout} {area}㎡
- 核心卖点：{highlights}

## 回复原则：
- 语气亲和、专业但不端着
- 引导私信/进一步沟通
- 对于质疑，幽默化解不对抗
- 适当制造稀缺感

## 请针对以下10种评论类型各生成2条回复：
1. 问价格的："这套多少钱？"
2. 问位置的："这是哪个小区？"
3. 嫌贵的："太贵了"
4. 问贷款的："首付多少？月供多少？"
5. 质疑的："中介就会忽悠"
6. 表达兴趣的："想看看"
7. 问学区的："对口哪个学校？"
8. 比较的："隔壁小区更便宜"
9. 凑热闹的："住不起"
10. 问缺点的："有什么问题没说的吧"
"""


# ===================== 调用大模型 =====================
def call_llm(prompt: str) -> str:
    """调用通义千问生成内容"""
    try:
        response = Generation.call(
            model="qwen-plus",
            prompt=prompt,
            result_format="message",
        )
        if response.status_code == 200:
            return response.output.choices[0].message.content
        else:
            return f"❌ 调用失败：{response.code} - {response.message}"
    except Exception as e:
        return f"❌ 出错了：{str(e)}"


# ===================== 页面 UI =====================
def main():
    st.set_page_config(
        page_title="🏠 房产AI内容助手",
        page_icon="🏠",
        layout="wide"
    )

    st.title("🏠 房产 AI 内容助手")
    st.caption("输入房源信息，一键生成口播文案 / 视频标题 / 多平台文案 / 评论区话术")

    # ---- 侧边栏 ----
    with st.sidebar:
        st.header("⚙️ 设置")
        # 如果后台已经配好 Key，不再让用户填
        if not dashscope.api_key:
            api_key_input = st.text_input(
                "通义千问 API Key",
                type="password",
                help="在 https://dashscope.console.aliyun.com/ 获取"
            )
            if api_key_input:
                dashscope.api_key = api_key_input
        else:
            st.success("✅ API 已就绪")

        st.divider()
        st.markdown("### 📖 使用说明")
        st.markdown("""
        1. 在右侧填写房源信息
        2. 选择要生成的内容类型
        3. 点击"生成"按钮
        4. 复制结果直接使用
        """)

    # ---- 主区域：房源信息输入 ----
    st.header("📝 房源信息")

    col1, col2, col3 = st.columns(3)

    with col1:
        city = st.text_input("城市", value="太原", help="如：太原")
        district = st.text_input("区域", value="", placeholder="如：小店区/万柏林区")
        community = st.text_input("小区名称 *", value="", placeholder="如：滨河润府")
        layout = st.text_input("户型 *", value="", placeholder="如：三室两厅两卫")

    with col2:
        area = st.number_input("面积（㎡）*", min_value=20.0, max_value=500.0, value=100.0, step=1.0)
        price = st.number_input("挂牌价（万）*", min_value=10.0, max_value=5000.0, value=200.0, step=1.0)
        floor = st.number_input("楼层", min_value=1, max_value=99, value=10)
        total_floor = st.number_input("总楼层", min_value=1, max_value=99, value=18)

    with col3:
        orientation = st.selectbox("朝向", ["南", "南北通透", "东南", "西南", "东", "西", "北"])
        decoration = st.selectbox("装修情况", ["毛坯", "简装", "精装", "豪装"])
        age = st.number_input("房龄（年）", min_value=0, max_value=50, value=5)
        extra = st.text_input("特殊信息", placeholder="如：满五唯一/急售/价格刚降")

    highlights = st.text_area("核心卖点 *", placeholder="如：6.5米大面宽、南向无遮挡、地铁口500米、对口XX小学", height=80)
    drawbacks = st.text_area("不足之处", placeholder="如：临街有噪音、需要装修、楼层偏低", height=80)

    # 计算单价
    unit_price = int(price * 10000 / area) if area > 0 else 0

    # ---- 生成内容选择 ----
    st.divider()
    st.header("🎯 选择生成内容")

    gen_type = st.radio(
        "你想生成什么？",
        ["📝 口播文案（30秒/60秒/3分钟）", "🏷️ 视频标题（5个版本）", "📱 多平台文案（抖音/小红书/视频号）", "💬 评论区回复话术"],
        horizontal=True
    )

    # ---- 生成按钮 ----
    if st.button("🚀 生成", type="primary", use_container_width=True):
        # 检查必填项
        if not community:
            st.error("请填写小区名称")
            return
        if not layout:
            st.error("请填写户型")
            return
        if not highlights:
            st.error("请填写核心卖点")
            return
        if not dashscope.api_key:
            st.error("请在左侧边栏配置 API Key")
            return

        # 构建参数字典
        params = {
            "city": city,
            "district": district,
            "community": community,
            "layout": layout,
            "area": area,
            "price": price,
            "unit_price": unit_price,
            "floor": floor,
            "total_floor": total_floor,
            "orientation": orientation,
            "decoration": decoration,
            "age": age,
            "highlights": highlights,
            "drawbacks": drawbacks if drawbacks else "暂无明显不足",
            "extra": extra if extra else "无",
        }

        # 选择对应 Prompt
        if "口播文案" in gen_type:
            prompt = PROMPT_ORAL_SCRIPT.format(**params)
        elif "视频标题" in gen_type:
            prompt = PROMPT_TITLES.format(**params)
        elif "多平台文案" in gen_type:
            prompt = PROMPT_MULTI_PLATFORM.format(**params)
        elif "评论区" in gen_type:
            prompt = PROMPT_COMMENTS.format(**params)

        # 调用模型
        with st.spinner("AI 正在生成中，请稍候..."):
            result = call_llm(prompt)

        # 展示结果
        st.divider()
        st.header("✅ 生成结果")
        st.markdown(result)

        # 复制按钮
        st.download_button(
            label="📋 下载结果为文本文件",
            data=result,
            file_name=f"{community}_{gen_type[:4]}.txt",
            mime="text/plain"
        )


if __name__ == "__main__":
    main()
